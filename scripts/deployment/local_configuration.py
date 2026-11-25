"""Provision private dev settings in the existing Docker volume; no deployment or services started."""
from __future__ import annotations

import json
import os
import subprocess
from urllib.parse import urlsplit, urlunsplit

import yaml

from scripts.deployment.candidate import ROOT
from scripts.deployment.environments import contract


# This program runs as the existing unprivileged Data-Lab user. Secret values arrive on stdin only.
BOOTSTRAP = r'''
import json,os,pathlib,stat,subprocess,sys,tempfile
p=json.load(sys.stdin);root=pathlib.Path(p['root'])
expected=pathlib.Path('/home/datalab/runtime/fraudlens/environments/dev')
if root!=expected or root.is_symlink():raise SystemExit('Unexpected managed root')
root.mkdir(parents=True,exist_ok=True,mode=0o700);root.chmod(0o700)
marker=root/'.fraudlens-runtime.json';identity={'schema_version':1,'repository':p['repository'],'environment':'dev','profile':'local'}
if marker.is_symlink() or (marker.exists() and json.loads(marker.read_text())!=identity):raise SystemExit('Runtime identity mismatch')
secret_dir=root/'secrets';secret_dir.mkdir(exist_ok=True,mode=0o700);secret_dir.chmod(0o700)
secret=secret_dir/'runtime.json'
if secret.is_symlink():raise SystemExit('Unsafe private configuration')
values=p['environment']
if secret.exists():
 existing=json.loads(secret.read_text());values.update({k:v for k,v in existing.items() if k in p['credential_keys'] and v})
if any(not isinstance(v,str) or chr(0) in v for v in values.values()):raise SystemExit('Invalid configuration value')
for key in p['required']:
 if not values.get(key):raise SystemExit('Required local secret missing')
descriptor,temp_name=tempfile.mkstemp(prefix='.runtime-',suffix='.json',dir=secret_dir);temp=pathlib.Path(temp_name)
with os.fdopen(descriptor,'w') as handle:json.dump(values,handle)
os.chmod(temp,0o600);os.replace(temp,secret)
marker.write_text(json.dumps(identity));marker.chmod(0o600)
env=dict(os.environ,**values)
for key in ('GH_TOKEN','GITHUB_TOKEN','PYTHONPATH','PYTHONHOME'):env.pop(key,None)
result=subprocess.run([sys.executable,'-m','airflow','db','migrate'],env=env,capture_output=True,timeout=120)
if result.returncode:raise SystemExit('Isolated Airflow metadata initialization failed')
os.environ.update(values)
from airflow.models import DagModel,DagRun
from airflow.utils.session import create_session
ids=['fraudlens_pipeline_orchestration','fraudlens_ingestion_workflow','fraudlens_transformation_workflow','fraudlens_validation_workflow']
with create_session() as session:
 if session.query(DagRun).filter(DagRun.state.in_(['running','queued'])).first():raise SystemExit('Dev runtime is busy')
 for name in ids:
  model=session.query(DagModel).filter(DagModel.dag_id==name).one_or_none()
  if model is None:
   model=DagModel(dag_id=name,is_paused=True,fileloc=str(root/'current/airflow/dags'/(name+'.py')));session.add(model)
  model.is_paused=True
mode=stat.S_IMODE(secret.stat().st_mode)
print(json.dumps({'configured':True,'runtime_root':str(root),'secret_file':str(secret),'secret_mode':oct(mode),
 'secret_names_present':sorted(k for k in p['required'] if values.get(k)),
 'isolated_airflow_metadata':True,'registered_paused_dags':len(ids),'scheduler_started':False,
 'source_activated':False,'cloud_resources_created':0}))
'''


def dotenv() -> dict[str, str]:
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def provision() -> dict:
    policy = contract()
    dev = policy["environments"]["dev"]
    inspect = json.loads(subprocess.check_output(["docker", "inspect", dev["container"]]))[0]
    if not inspect["State"]["Running"] or not any(m["Type"] == "volume" and m["Destination"] == "/home/datalab/runtime" for m in inspect["Mounts"]):
        raise ValueError("Existing running Data-Lab container and persistent runtime volume are required")
    values = dotenv()
    endpoint = urlsplit(values["DATALAB_MINIO_ENDPOINT"])
    if endpoint.hostname in ("localhost", "127.0.0.1") and endpoint.port:
        for port, bindings in inspect["NetworkSettings"]["Ports"].items():
            if any(binding["HostPort"] == str(endpoint.port) for binding in bindings or []):
                endpoint = endpoint._replace(netloc="127.0.0.1:" + port.split("/")[0])
                break
    profile = yaml.safe_load((ROOT / "airflow/config/orchestration_profiles.yml").read_text())["profiles"]["local"]
    runtime_root = dev["managed_root"]
    private = {"FRAUDLENS_MONGODB_URI": os.getenv("FRAUDLENS_MONGODB_URI") or profile["observability"]["mongodb_default_uri"],
               "DATALAB_MINIO_ENDPOINT": urlunsplit(endpoint),
               "DATALAB_MINIO_ACCESS_KEY": values["DATALAB_MINIO_ACCESS_KEY"],
               "DATALAB_MINIO_SECRET_KEY": values["DATALAB_MINIO_SECRET_KEY"],
               "DATALAB_MINIO_REGION": values.get("DATALAB_MINIO_REGION", "us-east-1"),
               "DATALAB_MINIO_BUCKET": values.get("DATALAB_MINIO_BUCKET", "fraudlensdata"),
               "OPENLINEAGE_URL": profile["observability"]["openlineage_default_url"],
               "AIRFLOW_HOME": runtime_root + "/airflow",
               "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": "sqlite:///" + runtime_root + "/airflow/airflow.db",
               "AIRFLOW__CORE__DAGS_FOLDER": runtime_root + "/current/airflow/dags",
               "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION": "true", "AIRFLOW__CORE__LOAD_EXAMPLES": "false",
               "AIRFLOW__CORE__EXECUTOR": "SequentialExecutor"}
    for key in ("DATALAB_MINIO_ENDPOINT", "FRAUDLENS_MONGODB_URI", "OPENLINEAGE_URL"):
        parsed = urlsplit(private[key])
        if parsed.hostname not in ("localhost", "127.0.0.1", dev["container"]):
            raise ValueError("Portfolio runtime endpoints must stay in the local Docker sandbox")
    payload = {"root": runtime_root, "repository": policy["repository"], "environment": private,
               "required": policy["local_runtime_secrets_required"],
               "credential_keys": [key for key in private if not key.startswith("AIRFLOW")]}
    result = subprocess.run(["docker", "exec", "-i", "--user", "datalab", dev["container"], dev["runtime_python"], "-c", BOOTSTRAP],
                            input=json.dumps(payload).encode(), capture_output=True, timeout=180, check=False)
    if result.returncode:
        raise ValueError("Private Docker configuration failed; raw runtime output was suppressed")
    # Airflow may write startup log lines. Only consume the final structured audit line.
    report = json.loads(result.stdout.decode("utf-8").strip().splitlines()[-1])
    if report["secret_mode"] != "0o600":
        raise ValueError("Private configuration permissions are not restrictive")
    return report


def main() -> None:
    try:
        report = provision()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError, yaml.YAMLError):
        raise SystemExit("Local configuration failed; no credential values were emitted") from None
    output = ROOT / ".ci-artifacts/local-runtime-configuration.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
