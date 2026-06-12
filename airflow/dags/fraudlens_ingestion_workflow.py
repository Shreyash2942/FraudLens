from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import (
    REPO_ROOT,
    bronze_dataset_order,
    dagrun_timeout_for_profile,
    max_active_runs_for_profile,
    runtime_failure_callback,
    schedule_for_profile,
    task_policy_kwargs,
)


def _context_file() -> str:
    return str((REPO_ROOT / "airflow" / "artifacts" / "orchestration" / "ingestion" / "{{ ts_nodash }}" / "runtime_context.json").as_posix())


def _prepare_context_command() -> str:
    return r"""
python - <<'PY'
import json
import sys
from pathlib import Path

repo_root = Path(r'REPO_ROOT_PLACEHOLDER')
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
dags_dir = repo_root / "airflow" / "dags"
if str(dags_dir) not in sys.path:
    sys.path.insert(0, str(dags_dir))

from _fraudlens_orchestration_common import (
    bronze_dataset_order,
    canonical_run_metadata,
    infer_task_group,
    latest_batch_id,
    log_orchestration_event,
    orchestration_defaults,
    orchestration_profile_settings,
    parse_bool,
    parse_dataset_override,
    resolve_orchestration_profile,
    utc_now_iso,
    validate_dataset_subset,
    write_orchestration_artifact,
)

defaults = orchestration_defaults()
profile = resolve_orchestration_profile("{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}")
profile_settings = orchestration_profile_settings(profile)
ingestion_profile = profile_settings.get("ingestion", {})

batch_id_raw = "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}"
batch_id = latest_batch_id() if str(batch_id_raw).strip().lower() in {"", "latest"} else str(batch_id_raw).strip()

datasets_raw = "{{ (dag_run.conf if dag_run else {}).get('datasets', params.datasets) }}"
requested_datasets = parse_dataset_override(datasets_raw)
valid_datasets = bronze_dataset_order()
selected_datasets = validate_dataset_subset(requested_datasets, valid_datasets)

allow_empty = parse_bool(
    "{{ (dag_run.conf if dag_run else {}).get('allow_empty', params.allow_empty) }}",
    default=parse_bool(defaults.get("allow_empty"), default=False),
)
if not selected_datasets and not allow_empty:
    raise ValueError("Dataset selection is empty and allow_empty is false.")

strict_mode = parse_bool(
    "{{ (dag_run.conf if dag_run else {}).get('strict_mode', params.strict_mode) }}",
    default=parse_bool(ingestion_profile.get("strict_mode"), default=True),
)

max_parallel = int(
    "{{ (dag_run.conf if dag_run else {}).get('max_parallel_datasets', params.max_parallel_datasets) }}"
)

command_profile = str(ingestion_profile.get("command_profile", "local")).strip().lower()
execution_mode = str(ingestion_profile.get("execution_mode", "spark_job")).strip().lower()
spark_submit_cmd = str(ingestion_profile.get("spark_submit_cmd", "python")).strip()
context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
started_at_utc = utc_now_iso()
payload = {
    "dag_id": "fraudlens_ingestion_workflow",
    "run_id": "{{ run_id }}",
    "run_stamp": "{{ ts_nodash }}",
    "profile": profile,
    "command_profile": command_profile,
    "execution_mode": execution_mode,
    "spark_submit_cmd": spark_submit_cmd,
    "batch_id": batch_id,
    "strict_mode": strict_mode,
    "allow_empty": allow_empty,
    "max_parallel_datasets": max_parallel,
    "selected_datasets": selected_datasets,
    "run_metadata": canonical_run_metadata(
        pipeline_run_id="{{ run_id }}",
        batch_id=batch_id,
        dag_id="fraudlens_ingestion_workflow",
        task_id="resolve_runtime_context",
        task_group=infer_task_group("prepare_context.resolve_runtime_context"),
        run_profile=profile,
        run_target=command_profile,
        execution_date_utc="{{ ts }}",
        started_at_utc=started_at_utc,
        ended_at_utc=started_at_utc,
        run_status="SUCCESS",
    ),
}
write_orchestration_artifact(context_path, payload, profile=profile, artifact_type="ingestion_runtime_context")
log_orchestration_event("INFO", "ingestion_runtime_context_prepared", dag_id="fraudlens_ingestion_workflow", run_id="{{ run_id }}", batch_id=batch_id)
print(json.dumps(payload))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).strip()


def _check_input_assets_command() -> str:
    return r"""
python - <<'PY'
import json
import sys
from pathlib import Path
import sys

repo_root = Path(r'REPO_ROOT_PLACEHOLDER')
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
dags_dir = repo_root / "airflow" / "dags"
if str(dags_dir) not in sys.path:
    sys.path.insert(0, str(dags_dir))

from _fraudlens_orchestration_common import read_orchestration_artifact, write_orchestration_artifact

context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
ctx = read_orchestration_artifact(
    context_path,
    profile="{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
)
if not ctx:
    raise FileNotFoundError(f"Runtime context file not found: {context_path}")
batch_id = ctx["batch_id"]
strict_mode = bool(ctx.get("strict_mode", True))
datasets = ctx.get("selected_datasets", [])

batch_root = Path(r'REPO_ROOT_PLACEHOLDER') / "data" / "batches" / batch_id
manifest_file = batch_root / "control" / "manifest.json"
landing_csv_root = batch_root / "landing" / "csv"
missing: list[str] = []
manifest_datasets: dict = {}

if not manifest_file.exists():
    missing.append(str(manifest_file))
else:
    manifest_payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest_datasets = manifest_payload.get("datasets", {}) if isinstance(manifest_payload, dict) else {}
    if not isinstance(manifest_datasets, dict):
        manifest_datasets = {}

for dataset in datasets:
    candidate = landing_csv_root / f"{dataset}.csv"
    if not candidate.exists():
        missing.append(str(candidate))
    dataset_meta = manifest_datasets.get(dataset)
    if strict_mode and not isinstance(dataset_meta, dict):
        missing.append(f"manifest:datasets.{dataset}")

summary = {
    "status": "ok" if not missing else "missing_assets",
    "batch_id": batch_id,
    "dataset_count": len(datasets),
    "missing_count": len(missing),
    "missing": missing,
}
summary_path = context_path.parent / "input_asset_check.json"
write_orchestration_artifact(
    summary_path,
    summary,
    profile=str(ctx.get("profile", "local")),
    artifact_type="ingestion_input_asset_check",
)
print(json.dumps(summary))

if missing and strict_mode:
    raise SystemExit(2)
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).strip()


def _dataset_load_command(dataset: str) -> str:
    return r"""
python - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

repo_root = Path(r'REPO_ROOT_PLACEHOLDER')
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
dags_dir = repo_root / "airflow" / "dags"
if str(dags_dir) not in sys.path:
    sys.path.insert(0, str(dags_dir))

from _fraudlens_orchestration_common import read_orchestration_artifact, write_orchestration_artifact

dataset = "DATASET_PLACEHOLDER"
context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
ctx = read_orchestration_artifact(
    context_path,
    profile="{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
)
if not ctx:
    raise FileNotFoundError(f"Runtime context file not found: {context_path}")
selected = set(ctx.get("selected_datasets", []))
status_dir = context_path.parent / "datasets"
status_file = status_dir / f"{dataset}.json"

if dataset not in selected:
    payload = {"dataset": dataset, "status": "skipped", "reason": "not_selected"}
    write_orchestration_artifact(
        status_file,
        payload,
        profile=str(ctx.get("profile", "local")),
        artifact_type="ingestion_dataset_status",
    )
    print(json.dumps(payload))
    raise SystemExit(0)

execution_mode = str(ctx.get("execution_mode", "spark_job")).lower()
batch_id = str(ctx["batch_id"])
command_profile = str(ctx.get("command_profile", "local")).lower()
spark_submit_cmd = str(ctx.get("spark_submit_cmd", "python"))

if execution_mode == "dry_run":
    preview_cmd = [
        "python",
        str(Path(r'REPO_ROOT_PLACEHOLDER') / "warehouse" / "snowflake-warehouse-setup" / "scripts" / "run_dataset_spark_job.py"),
        "--layer",
        "bronze",
        "--dataset",
        dataset,
        "--batch-id",
        batch_id,
        "--profile",
        command_profile,
        "--spark-submit-cmd",
        spark_submit_cmd,
    ]
    payload = {
        "dataset": dataset,
        "status": "dry_run",
        "batch_id": batch_id,
        "command_profile": command_profile,
        "load_command": preview_cmd,
    }
    write_orchestration_artifact(
        status_file,
        payload,
        profile=str(ctx.get("profile", "local")),
        artifact_type="ingestion_dataset_status",
    )
    print(json.dumps(payload))
    raise SystemExit(0)

script = Path(r'REPO_ROOT_PLACEHOLDER') / "warehouse" / "snowflake-warehouse-setup" / "scripts" / "run_dataset_spark_job.py"
cmd = [
    "python",
    str(script),
    "--layer",
    "bronze",
    "--dataset",
    dataset,
    "--batch-id",
    batch_id,
    "--profile",
    command_profile,
    "--spark-submit-cmd",
    spark_submit_cmd,
]
completed = subprocess.run(cmd, check=False)
payload = {
    "dataset": dataset,
    "status": "success" if completed.returncode == 0 else "failed",
    "exit_code": int(completed.returncode),
    "command_profile": command_profile,
    "load_command": cmd,
}
write_orchestration_artifact(
    status_file,
    payload,
    profile=str(ctx.get("profile", "local")),
    artifact_type="ingestion_dataset_status",
)
print(json.dumps(payload))
raise SystemExit(completed.returncode)
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).replace(
        "DATASET_PLACEHOLDER", dataset
    ).strip()


def _validate_ingestion_results_command() -> str:
    return r"""
python - <<'PY'
import json
from pathlib import Path
import sys

repo_root = Path(r'REPO_ROOT_PLACEHOLDER')
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
dags_dir = repo_root / "airflow" / "dags"
if str(dags_dir) not in sys.path:
    sys.path.insert(0, str(dags_dir))

from _fraudlens_orchestration_common import (
    canonical_run_metadata,
    infer_task_group,
    list_orchestration_artifacts,
    log_orchestration_event,
    read_orchestration_artifact,
    utc_now_iso,
    write_orchestration_artifact,
)

context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
ctx = read_orchestration_artifact(
    context_path,
    profile="{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
)
if not ctx:
    raise FileNotFoundError(f"Runtime context file not found: {context_path}")
selected = ctx.get("selected_datasets", [])
strict_mode = bool(ctx.get("strict_mode", True))
status_dir = context_path.parent / "datasets"
missing_status: list[str] = []
failed_status: list[dict] = []
status_by_dataset = {
    str(row.get("dataset")): row
    for row in list_orchestration_artifacts(
        status_dir,
        profile=str(ctx.get("profile", "local")),
        artifact_type="ingestion_dataset_status",
    )
}
rows: list[dict] = []

for dataset in selected:
    payload = status_by_dataset.get(dataset)
    if not payload:
        missing_status.append(dataset)
        continue
    rows.append(payload)
    if payload.get("status") not in {"success", "dry_run"}:
        failed_status.append(payload)

summary = {
    "batch_id": ctx.get("batch_id"),
    "selected_datasets": selected,
    "status_files_present": len(rows),
    "missing_status_files": missing_status,
    "failed_or_unexpected_status": failed_status,
}
target = context_path.parent / "ingestion_validation.json"
write_orchestration_artifact(
    target,
    summary,
    profile=str(ctx.get("profile", "local")),
    artifact_type="ingestion_validation_summary",
)
print(json.dumps(summary))

if strict_mode and (missing_status or failed_status):
    raise SystemExit(3)
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).strip()


def _publish_ingestion_metadata_command() -> str:
    return r"""
python - <<'PY'
import json
from pathlib import Path
import sys

repo_root = Path(r'REPO_ROOT_PLACEHOLDER')
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
dags_dir = repo_root / "airflow" / "dags"
if str(dags_dir) not in sys.path:
    sys.path.insert(0, str(dags_dir))

from _fraudlens_orchestration_common import (
    canonical_run_metadata,
    infer_task_group,
    list_orchestration_artifacts,
    log_orchestration_event,
    read_orchestration_artifact,
    utc_now_iso,
    write_orchestration_artifact,
)

context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
ctx = read_orchestration_artifact(
    context_path,
    profile="{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
)
if not ctx:
    raise FileNotFoundError(f"Runtime context file not found: {context_path}")
validation_file = context_path.parent / "ingestion_validation.json"
validation = read_orchestration_artifact(validation_file, profile=str(ctx.get("profile", "local"))) or {}

status_dir = context_path.parent / "datasets"
statuses = list_orchestration_artifacts(
    status_dir,
    profile=str(ctx.get("profile", "local")),
    artifact_type="ingestion_dataset_status",
)

summary = {
    "dag_id": "fraudlens_ingestion_workflow",
    "run_id": ctx.get("run_id"),
    "pipeline_run_id": ctx.get("run_id"),
    "run_stamp": ctx.get("run_stamp"),
    "run_profile": ctx.get("profile"),
    "run_target": ctx.get("command_profile"),
    "execution_mode": ctx.get("execution_mode"),
    "batch_id": ctx.get("batch_id"),
    "execution_date_utc": "{{ ts }}",
    "selected_datasets": ctx.get("selected_datasets", []),
    "dataset_status": statuses,
    "validation": validation,
    "run_status": "SUCCESS",
    "failure_category": None,
    "ended_at_utc": utc_now_iso(),
}
failed = [row for row in statuses if row.get("status") == "failed"]
if failed:
    summary["run_status"] = "FAILED"
    summary["failure_category"] = "data_quality"

summary["run_metadata"] = canonical_run_metadata(
    pipeline_run_id=str(ctx.get("run_id", "")),
    batch_id=str(ctx.get("batch_id", "")),
    dag_id="fraudlens_ingestion_workflow",
    task_id="publish_ingestion_summary",
    task_group=infer_task_group("publish_ingestion_metadata.publish_ingestion_summary"),
    run_profile=str(ctx.get("profile", "local")),
    run_target=str(ctx.get("command_profile", "local")),
    execution_date_utc="{{ ts }}",
    started_at_utc=str((ctx.get("run_metadata", {}) or {}).get("started_at_utc", "")),
    ended_at_utc=str(summary.get("ended_at_utc", "")),
    run_status=str(summary["run_status"]),
    failure_category=summary.get("failure_category"),
)
target = context_path.parent / "ingestion_summary.json"
write_orchestration_artifact(
    target,
    summary,
    profile=str(ctx.get("profile", "local")),
    artifact_type="ingestion_summary",
)
log_orchestration_event("INFO", "ingestion_summary_published", dag_id="fraudlens_ingestion_workflow", run_id=ctx.get("run_id"), summary_file=str(target))
print(json.dumps({"status": "published", "summary_file": str(target)}))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).strip()


with DAG(
    dag_id="fraudlens_ingestion_workflow",
    description="Phase 6 ingestion workflow for Bronze dataset loading with governed runtime controls.",
    start_date=datetime(2026, 1, 1),
    schedule=schedule_for_profile(),
    catchup=False,
    max_active_tasks=8,
    max_active_runs=max_active_runs_for_profile(),
    dagrun_timeout=dagrun_timeout_for_profile(),
    default_args={
        "on_failure_callback": runtime_failure_callback,
    },
    tags=["fraudlens", "orchestration", "ingestion", "bronze"],
    params={
        "profile": "local",
        "batch_id": "latest",
        "datasets": "from_contract",
        "strict_mode": True,
        "allow_empty": False,
        "max_parallel_datasets": 4,
    },
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    with TaskGroup(group_id="prepare_context") as prepare_context:
        resolve_runtime_context = BashOperator(
            task_id="resolve_runtime_context",
            bash_command=_prepare_context_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("infra_transient"),
        )
        check_input_assets = BashOperator(
            task_id="check_input_assets",
            bash_command=_check_input_assets_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
        )
        resolve_runtime_context >> check_input_assets

    with TaskGroup(group_id="load_bronze_datasets") as load_bronze_datasets:
        for dataset_name in bronze_dataset_order():
            BashOperator(
                task_id=f"load_bronze__{dataset_name}",
                bash_command=_dataset_load_command(dataset_name),
                cwd=REPO_ROOT.as_posix(),
                **task_policy_kwargs("ingestion_dataset"),
            )

    with TaskGroup(group_id="validate_ingestion_results") as validate_ingestion_results:
        validate_results = BashOperator(
            task_id="validate_dataset_statuses",
            bash_command=_validate_ingestion_results_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
        )

    ingestion_completion_gate = EmptyOperator(task_id="ingestion_completion_gate")

    with TaskGroup(group_id="publish_ingestion_metadata") as publish_ingestion_metadata:
        publish_summary = BashOperator(
            task_id="publish_ingestion_summary",
            bash_command=_publish_ingestion_metadata_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("artifact_publish"),
        )

    (
        start
        >> prepare_context
        >> load_bronze_datasets
        >> validate_ingestion_results
        >> ingestion_completion_gate
        >> publish_ingestion_metadata
        >> end
    )
