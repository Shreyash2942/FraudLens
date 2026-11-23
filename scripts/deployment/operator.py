"""Owner-operated local Docker execution of a verified, approved main-workflow handoff."""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import tempfile
from pathlib import Path

from scripts.deployment import control, handoff
from scripts.deployment.candidate import REPOSITORY, ROOT
from scripts.deployment.environments import contract, github


REMOTE_APPLY = r'''
import base64,json,os,pathlib,stat,subprocess,sys,tempfile
try:
 p=json.load(sys.stdin);c=p['configuration'];root=pathlib.Path(c['root']);source=pathlib.Path(c['source_root'])
 if root!=pathlib.Path('/home/datalab/runtime/fraudlens/environments/dev') or source!=pathlib.Path('/home/datalab/fraudlens'):raise ValueError('Unexpected local target')
 cmd=['git','-c','safe.directory='+str(source),'-C',str(source)]
 if subprocess.check_output(cmd+['rev-parse','HEAD']).decode().strip()!=p['controller_sha']:raise ValueError('Controller mismatch')
 subprocess.run(cmd+['diff','--quiet','HEAD'],check=True,capture_output=True)
 secret=root/'secrets/runtime.json'
 if secret.is_symlink() or stat.S_IMODE(secret.stat().st_mode)!=0o600:raise ValueError('Private configuration permissions')
 values=json.loads(secret.read_text())
 allowed={'FRAUDLENS_MONGODB_URI','DATALAB_MINIO_ENDPOINT','DATALAB_MINIO_ACCESS_KEY','DATALAB_MINIO_SECRET_KEY',
 'DATALAB_MINIO_REGION','DATALAB_MINIO_BUCKET','OPENLINEAGE_URL','AIRFLOW_HOME','AIRFLOW__DATABASE__SQL_ALCHEMY_CONN',
 'AIRFLOW__CORE__DAGS_FOLDER','AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION','AIRFLOW__CORE__LOAD_EXAMPLES','AIRFLOW__CORE__EXECUTOR'}
 if set(values)-allowed or any(not isinstance(v,str) or chr(0) in v for v in values.values()):raise ValueError('Private configuration keys')
 if any(not values.get(k) for k in ('FRAUDLENS_MONGODB_URI','DATALAB_MINIO_ACCESS_KEY','DATALAB_MINIO_SECRET_KEY')):raise ValueError('Missing local credential')
 from urllib.parse import urlsplit
 if any(urlsplit(values[k]).hostname not in ('localhost','127.0.0.1',c['container']) for k in ('FRAUDLENS_MONGODB_URI','DATALAB_MINIO_ENDPOINT','OPENLINEAGE_URL')):raise ValueError('Nonlocal endpoint')
 if values.get('AIRFLOW_HOME')!=str(root/'airflow') or values.get('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN')!='sqlite:///'+str(root/'airflow/airflow.db'):raise ValueError('Unisolated metadata')
 for key in ('GH_TOKEN','GITHUB_TOKEN','PYTHONPATH','PYTHONHOME'):os.environ.pop(key,None)
 os.environ.update(values);sys.path.insert(0,str(source))
 from scripts.deployment.runtime import activate,smoke
 descriptor,name=tempfile.mkstemp(prefix='.approved-',suffix='.tar',dir=root)
 try:
  with os.fdopen(descriptor,'wb') as handle:handle.write(base64.b64decode(p['bundle'],validate=True))
  result=activate(pathlib.Path(name),p['candidate_sha256'],p['source_sha'],root,lambda release:smoke(release,pathlib.Path(c['runtime_python'])))
 finally:pathlib.Path(name).unlink(missing_ok=True)
 print(json.dumps(result))
except Exception:
 raise SystemExit('Local activation stopped; private runtime details suppressed') from None
'''


def approved_run(run: dict, reviews: list[dict], jobs: list[dict]) -> None:
    owner = contract()["owner"].lower()
    if (run.get("event") != "workflow_dispatch" or run.get("head_branch") != "main"
            or run.get("path") != ".github/workflows/deploy.yml" or run.get("conclusion") != "success"
            or run.get("status") != "completed" or run.get("head_repository", {}).get("full_name") != REPOSITORY
            or run.get("actor", {}).get("login", "").lower() != owner
            or run.get("triggering_actor", run.get("actor", {})).get("login", "").lower() != owner):
        raise ValueError("A completed owner-dispatched main deployment handoff is required")
    relevant = [row for row in reviews if any(env.get("name") == "dev" for env in row.get("environments", []))]
    if (not any(row.get("state") == "approved" and row.get("user", {}).get("login", "").lower() == owner for row in relevant)
            or any(row.get("state") == "rejected" for row in relevant)):
        raise ValueError("A fresh explicit dev owner environment approval is required")
    for name in ("Verify Main Candidate", "Prepare Approved Dev Handoff"):
        if not any(job["name"] == name and job["conclusion"] == "success" for job in jobs):
            raise ValueError("Required protected handoff job did not succeed")


def configuration_context() -> dict[str, str]:
    variables = {row["name"]: row["value"] for row in control.api("environments/dev/variables?per_page=100")["variables"]}
    mapping = {"EXECUTION_MODE": "FRAUDLENS_EXECUTION_MODE", "CLOUD_RESOURCES_ENABLED": "FRAUDLENS_CLOUD_RESOURCES_ENABLED",
               "DOCKER_CONTAINER": "FRAUDLENS_DOCKER_CONTAINER", "DEPLOY_ROOT": "FRAUDLENS_DEPLOY_ROOT",
               "AIRFLOW_PYTHON": "FRAUDLENS_RUNTIME_PYTHON", "SOURCE_ROOT": "FRAUDLENS_SOURCE_ROOT"}
    return {key: variables.get(value, "") for key, value in mapping.items()}


def prepare(run_id: str, output: Path) -> dict:
    if not run_id.isdigit() or int(run_id) <= 0 or github("user")["login"].lower() != contract()["owner"].lower():
        raise ValueError("Authenticated local owner and a positive deployment run ID are required")
    run = control.api(f"actions/runs/{run_id}")
    approved_run(run, control.api(f"actions/runs/{run_id}/approvals"), control.pages(f"actions/runs/{run_id}/jobs", "jobs"))
    name = f"dev-handoff-{run_id}-{run['run_attempt']}"
    artifacts = [row for row in control.pages(f"actions/runs/{run_id}/artifacts", "artifacts") if row["name"] == name and not row["expired"]]
    if len(artifacts) != 1:
        raise ValueError("Approved handoff artifact is missing or expired")
    record = json.loads(control.download_artifact(artifacts[0], {"handoff.json"})["handoff.json"])
    if (record["deployment_run_id"] != run_id or record["deployment_run_attempt"] != str(run["run_attempt"])
            or record["controller_sha"] != run["head_sha"] or record["environment"] != "dev"
            or record["execution_mode"] != "local_docker_operator" or record["deployment_executed"] is not False
            or record["state"] != "approved_handoff_awaiting_local_operator"):
        raise ValueError("Handoff identity mismatch")
    context = configuration_context()
    settings = handoff.configuration(context)
    if record["configuration"] != settings or record["configuration_sha256"] != handoff.fingerprint(settings):
        raise ValueError("Runtime configuration changed after approval; request a new handoff")
    context.update(GITHUB_REPOSITORY=REPOSITORY, GITHUB_EVENT_NAME="workflow_dispatch", GITHUB_REF="refs/heads/main", TARGET_ENVIRONMENT="dev",
                   GITHUB_ACTOR=run["actor"]["login"], CANDIDATE_SHA=record["source_sha"], OWNER_APPROVAL=record["source_sha"],
                   CANDIDATE_SHA256=record["candidate_sha256"], CI_RUN_ID=str(record["ci_run_id"]),
                   DEPLOY_ENABLED=control.api("actions/variables/FRAUDLENS_DEV_DEPLOY_ENABLED")["value"],
                   COST_PROFILE=control.api("actions/variables/FRAUDLENS_COST_PROFILE")["value"])
    verification = control.prepare(context, output)
    if verification["ci_run_attempt"] != record["ci_run_attempt"]:
        raise ValueError("CI attempt changed after handoff approval")
    return record


def apply(record: dict, bundle: Path) -> dict:
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    if current != record["controller_sha"]:
        raise ValueError("Run the operator from the exact approved clean main controller commit")
    subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=ROOT, check=True, capture_output=True)
    settings = record["configuration"]
    payload = {"configuration": settings, "controller_sha": current, "source_sha": record["source_sha"],
               "candidate_sha256": record["candidate_sha256"], "bundle": base64.b64encode(bundle.read_bytes()).decode()}
    result = subprocess.run(["docker", "exec", "-i", "--user", "datalab", settings["container"],
                             "flock", "-n", settings["root"] + "/.activation.lock", settings["runtime_python"], "-c", REMOTE_APPLY],
                            input=json.dumps(payload).encode(), capture_output=True, timeout=180, check=False)
    if result.returncode:
        raise ValueError("Local operator activation failed; inspect the managed runtime without exporting credentials")
    report = json.loads(result.stdout.decode().strip().splitlines()[-1])
    report.update(deployment_run_id=record["deployment_run_id"], configuration_sha256=record["configuration_sha256"],
                  execution_mode="local_docker_operator", credentials_exported_to_github=False)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment-run", required=True)
    parser.add_argument("--apply", action="store_true", help="Activate the explicitly approved local Docker candidate")
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/local-operator.json"))
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="fraudlens-approved-handoff-") as directory:
            output = Path(directory)
            record = prepare(args.deployment_run, output)
            result = apply(record, output / "candidate.tar") if args.apply else {
                "source_sha": record["source_sha"], "deployment_run_id": record["deployment_run_id"],
                "configuration_sha256": record["configuration_sha256"], "state": "verified_local_plan",
                "deployment_executed": False, "credentials_exported_to_github": False}
    except Exception:
        raise SystemExit("Local handoff rejected; no private details emitted") from None
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
