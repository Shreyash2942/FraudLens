"""Stage verified dev source, check Airflow imports, then atomically switch managed code."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import tarfile
from pathlib import Path
from typing import Callable

import yaml

from scripts.deployment.candidate import REPOSITORY, sha256, verify
from scripts.deployment.control import prepare


REQUIRED_FILES = {"airflow/dags/fraudlens_pipeline_orchestration.py", "airflow/config/orchestration_profiles.yml",
                  "dbt/dbt_project.yml", "synthetic_generator/contracts.py"}
SMOKE = """import os, sys
from airflow.models.dagbag import DagBag
from airflow.models import DagModel, DagRun
from airflow.utils.session import create_session
bag = DagBag(dag_folder=os.environ['FRAUDLENS_CANDIDATE_DAGS'], include_examples=False, safe_mode=False)
required = {'fraudlens_pipeline_orchestration', 'fraudlens_ingestion_workflow', 'fraudlens_transformation_workflow', 'fraudlens_validation_workflow'}
with create_session() as session:
    models = session.query(DagModel).filter(DagModel.dag_id.in_(required)).all()
    busy = session.query(DagRun).filter(DagRun.dag_id.in_(required), DagRun.state.in_(['running', 'queued'])).first()
    quiet = len(models) == len(required) and all(row.is_paused for row in models) and busy is None
sys.exit(0 if not bag.import_errors and required.issubset(bag.dags) and quiet else 1)
"""


def smoke(release: Path, interpreter: Path) -> None:
    if not interpreter.is_absolute() or not interpreter.is_file() or interpreter.resolve().is_relative_to(release):
        raise ValueError("A separately provisioned Airflow Python interpreter is required")
    environment = dict(os.environ, FRAUDLENS_REPO_ROOT=str(release),
                       PYTHONPATH=str(release),
                       FRAUDLENS_CANDIDATE_DAGS=str(release / "airflow/dags"),
                       AIRFLOW__CORE__DAGS_FOLDER=str(release / "airflow/dags"),
                       AIRFLOW__CORE__LOAD_EXAMPLES="false", AIRFLOW__LOGGING__LOGGING_LEVEL="ERROR")
    environment.pop("PYTHONHOME", None)
    environment.pop("GH_TOKEN", None)
    environment.pop("GITHUB_TOKEN", None)
    result = subprocess.run([str(interpreter), "-c", SMOKE], env=environment,
                            cwd=release, capture_output=True, check=False, timeout=120)
    if result.returncode:
        raise ValueError("Candidate Airflow imports failed; active code was preserved")


def activate(bundle: Path, digest: str, source_sha: str, root: Path,
             check: Callable[[Path], None]) -> dict:
    if os.name != "posix" or not root.is_absolute() or root.is_symlink() or root.resolve() == Path("/"):
        raise ValueError("A managed Linux dev runtime root is required")
    root = root.resolve(strict=True)
    marker_path = root / ".fraudlens-runtime.json"
    if marker_path.is_symlink():
        raise ValueError("Unsafe runtime marker")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker != {"schema_version": 1, "repository": REPOSITORY, "environment": "dev", "profile": "local"}:
        raise ValueError("Managed runtime identity does not match dev/local")
    manifest, payload = verify(bundle, digest, source_sha)
    if manifest.get("origin_main_push") is not True:
        raise ValueError("A preview cannot activate runtime source")
    if not REQUIRED_FILES.issubset(payload) or ".fraudlens-release.json" in payload:
        raise ValueError("Candidate lacks required runtime source")
    profiles = yaml.safe_load(payload["airflow/config/orchestration_profiles.yml"])
    local = profiles["profiles"]["local"]
    if (profiles["defaults"]["profile"] != "local" or local["transformation"]["dbt_profile"] != "fraudlens_local_spark"
            or local["transformation"]["dbt_target"] != "local" or local["validation"]["dbt_target"] != "local"):
        raise ValueError("Dev candidate must preserve the local Spark/Hive profile")
    releases = root / "releases"
    if releases.is_symlink():
        raise ValueError("Unsafe release store")
    releases.mkdir(exist_ok=True)
    current = root / "current"
    previous = None
    if current.is_symlink():
        target = current.resolve(strict=True)
        if not target.is_relative_to(releases) or target.parent != releases:
            raise ValueError("Existing active pointer is outside the managed store")
        previous = target.name
    elif current.exists():
        raise ValueError("Refusing to replace an unmanaged active directory")
    release = releases / (source_sha + "-" + digest[:16])
    record = {"source_sha": source_sha, "candidate_sha256": digest}
    if release.is_symlink():
        raise ValueError("Unsafe candidate destination")
    if not release.exists():
        with tempfile.TemporaryDirectory(prefix=".stage-", dir=releases) as directory:
            staged = Path(directory) / "source"
            staged.mkdir()
            for name, data in payload.items():
                path = staged / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                path.chmod(int(manifest["files"][name]["mode"][-3:], 8))
            (staged / ".fraudlens-release.json").write_text(json.dumps(record), encoding="utf-8")
            staged.rename(release)
    if (release / ".fraudlens-release.json").is_symlink() or json.loads((release / ".fraudlens-release.json").read_text()) != record:
        raise ValueError("Existing release has a different identity")
    expected = set(payload) | {".fraudlens-release.json"}
    actual = {path.relative_to(release).as_posix() for path in release.rglob("*") if path.is_file() or path.is_symlink()}
    if actual != expected or any((release / name).is_symlink() or sha256((release / name).read_bytes()) != manifest["files"][name]["sha256"] for name in payload):
        raise ValueError("Existing release source changed")
    check(release)  # Import verification must succeed before the active pointer changes.
    pointer = root / ".current-next"
    if pointer.exists() or pointer.is_symlink():
        raise ValueError("A pending activation requires operator investigation")
    try:
        pointer.symlink_to(release, target_is_directory=True)
        os.replace(pointer, current)
    finally:
        if pointer.is_symlink():
            pointer.unlink()
    return {**record, "environment": "dev", "profile": "local", "previous_release": previous,
            "active_release": release.name, "airflow_import_check": "success", "deployment_executed": True,
            "maintenance_gate": "paused_and_drained",
            "pipeline_runtime_qualification": "pending_issue_90", "data_rollback_performed": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--airflow-python", type=Path, required=True)
    args = parser.parse_args()
    output = Path(".ci-artifacts/deployment")
    activated = False
    try:
        verification = prepare(dict(os.environ), output)  # Revalidate after environment approval/queueing.
        report = activate(output / "candidate.tar", verification["candidate_sha256"], verification["source_sha"],
                          args.root, lambda release: smoke(release, args.airflow_python))
        activated = True
        report.update(ci_run_id=verification["ci_run_id"], ci_run_attempt=verification["ci_run_attempt"],
                      actor=verification["actor"], runtime_configuration_sha256=sha256(
                          json.dumps({"root": str(args.root), "airflow_python": str(args.airflow_python)}, sort_keys=True).encode()))
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError, tarfile.TarError, yaml.YAMLError):
        output.mkdir(parents=True, exist_ok=True)
        (output / "deployment.json").write_text(json.dumps({"status": "failed", "deployment_executed": activated,
                                                            "data_rollback_performed": False}) + "\n", encoding="utf-8")
        raise SystemExit("Dev deployment stopped; inspect trusted runner and job status") from None
    (output / "deployment.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
