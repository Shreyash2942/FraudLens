from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import (
    REPO_ROOT,
    dagrun_timeout_for_profile,
    max_active_runs_for_profile,
    runtime_failure_callback,
    schedule_for_profile,
    task_policy_kwargs,
)


def _context_file() -> str:
    return str((REPO_ROOT / "airflow" / "artifacts" / "orchestration" / "transformation" / "{{ ts_nodash }}" / "runtime_context.json").as_posix())


def _runtime_context_command() -> str:
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
    canonical_run_metadata,
    infer_task_group,
    latest_batch_id,
    log_orchestration_event,
    orchestration_artifact_dir,
    orchestration_profile_settings,
    resolve_orchestration_profile,
    utc_now_iso,
)

profile = resolve_orchestration_profile("{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}")
profile_settings = orchestration_profile_settings(profile)
transform_settings = profile_settings.get("transformation", {})

batch_id_raw = "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}"
batch_id = latest_batch_id() if str(batch_id_raw).strip().lower() in {"", "latest"} else str(batch_id_raw).strip()

artifact_dir = orchestration_artifact_dir("transformation", "{{ ts_nodash }}")
artifact_dir.mkdir(parents=True, exist_ok=True)
context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
context_path.parent.mkdir(parents=True, exist_ok=True)
started_at_utc = utc_now_iso()
payload = {
    "dag_id": "fraudlens_transformation_workflow",
    "run_id": "{{ run_id }}",
    "run_stamp": "{{ ts_nodash }}",
    "profile": profile,
    "batch_id": batch_id,
    "dbt_profile": str(transform_settings.get("dbt_profile", "fraudlens_local_spark")),
    "dbt_target": str(transform_settings.get("dbt_target", "local")),
    "threads": int("{{ (dag_run.conf if dag_run else {}).get('threads', params.threads) }}"),
    "run_metadata": canonical_run_metadata(
        pipeline_run_id="{{ run_id }}",
        batch_id=batch_id,
        dag_id="fraudlens_transformation_workflow",
        task_id="resolve_runtime_context",
        task_group=infer_task_group("prepare_dbt_context.resolve_runtime_context"),
        run_profile=profile,
        run_target=str(transform_settings.get("dbt_target", "local")),
        execution_date_utc="{{ ts }}",
        started_at_utc=started_at_utc,
        ended_at_utc=started_at_utc,
        run_status="SUCCESS",
    ),
}
context_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
log_orchestration_event("INFO", "transformation_runtime_context_prepared", dag_id="fraudlens_transformation_workflow", run_id="{{ run_id }}", batch_id=batch_id)
print(json.dumps(payload))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).strip()


def _dbt_command(action: str, selector: str | None = None, *, full_refresh: bool = False) -> str:
    parts = [
        "dbt",
        action,
        "--project-dir",
        "dbt",
        "--profiles-dir",
        "dbt/profiles",
        "--profile",
        "fraudlens_local_spark",
        "--target",
        "local",
    ]
    if selector:
        parts.extend(["--select", selector])
    if full_refresh:
        parts.append("--full-refresh")
    return " ".join(parts)


def _stage_status_file(stage_name: str) -> str:
    return str((REPO_ROOT / "airflow" / "artifacts" / "orchestration" / "transformation" / "{{ ts_nodash }}" / "stages" / f"{stage_name}.json").as_posix())


def _dbt_parse_with_status_command() -> str:
    return f"""
set +e
{_dbt_command("parse")}
RC=$?
export RC
python - <<'PY'
import json
import os
from pathlib import Path

target = Path(r'STAGE_STATUS_FILE_PLACEHOLDER')
target.parent.mkdir(parents=True, exist_ok=True)
exit_code = int(os.environ.get("RC", "1"))
payload = {{"stage": "parse_preflight", "exit_code": exit_code, "status": "success" if exit_code == 0 else "failed"}}
target.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(payload))
PY
exit $RC
""".replace(
        "STAGE_STATUS_FILE_PLACEHOLDER", _stage_status_file("parse_preflight").replace("\\", "\\\\")
    ).strip()


def _stage_build_command(layer: str, default_selector: str) -> str:
    return f"""
SELECTOR_OVERRIDE="{{{{ (dag_run.conf if dag_run else {{}}).get('selector_override', params.selector_override) }}}}"
ALLOW_PARTIAL="{{{{ (dag_run.conf if dag_run else {{}}).get('allow_partial', params.allow_partial) }}}}"
LAYER_SUBSET="{{{{ (dag_run.conf if dag_run else {{}}).get('layer_subset', params.layer_subset) }}}}"
FULL_REFRESH_LAYERS="{{{{ (dag_run.conf if dag_run else {{}}).get('full_refresh_layers', params.full_refresh_layers) }}}}"

if [ "$ALLOW_PARTIAL" = "True" ] || [ "$ALLOW_PARTIAL" = "true" ]; then
  if [[ ",$LAYER_SUBSET," != *",{layer},"* ]]; then
    echo "Skipping layer {layer} because allow_partial=true and layer_subset does not include it."
    exit 0
  fi
fi

SELECTOR="{default_selector}"
if [ -n "$SELECTOR_OVERRIDE" ]; then
  SELECTOR="$SELECTOR_OVERRIDE"
fi

if [[ ",$FULL_REFRESH_LAYERS," == *",{layer},"* ]]; then
  DBT_COMMAND="{_dbt_command("build")} --select $SELECTOR --full-refresh"
else
  DBT_COMMAND="{_dbt_command("build")} --select $SELECTOR"
fi

set +e
eval "$DBT_COMMAND"
RC=$?
export RC
python - <<'PY'
import json
import os
from pathlib import Path

target = Path(r'STAGE_STATUS_FILE_PLACEHOLDER')
target.parent.mkdir(parents=True, exist_ok=True)
exit_code = int(os.environ.get("RC", "1"))
payload = {{
    "stage": "{layer}",
    "selector": "{default_selector}",
    "exit_code": exit_code,
    "status": "success" if exit_code == 0 else "failed",
}}
target.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(payload))
PY
exit $RC
""".replace(
        "STAGE_STATUS_FILE_PLACEHOLDER", _stage_status_file(layer).replace("\\", "\\\\")
    ).strip()


def _publish_transformation_metadata_command() -> str:
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

from _fraudlens_orchestration_common import log_orchestration_event, utc_now_iso

context_path = Path(r'CONTEXT_FILE_PLACEHOLDER')
ctx = json.loads(context_path.read_text(encoding="utf-8")) if context_path.exists() else {}
stage_dir = context_path.parent / "stages"
stage_status = []
if stage_dir.exists():
    for entry in sorted(stage_dir.glob("*.json")):
        stage_status.append(json.loads(entry.read_text(encoding="utf-8")))

overall_status = "success"
if any(item.get("status") != "success" for item in stage_status):
    overall_status = "failed"

summary = {
    "dag_id": "fraudlens_transformation_workflow",
    "run_id": ctx.get("run_id"),
    "run_stamp": ctx.get("run_stamp"),
    "profile": ctx.get("profile"),
    "batch_id": ctx.get("batch_id"),
    "dbt_profile": ctx.get("dbt_profile"),
    "dbt_target": ctx.get("dbt_target"),
    "threads": ctx.get("threads"),
    "stage_status": stage_status,
    "overall_status": overall_status,
    "ended_at_utc": utc_now_iso(),
}
target = context_path.parent / "transformation_summary.json"
target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
log_orchestration_event("INFO", "transformation_summary_published", dag_id="fraudlens_transformation_workflow", run_id=ctx.get("run_id"), summary_file=str(target))
print(json.dumps({"status": "published", "summary_file": str(target), "overall_status": overall_status}))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "CONTEXT_FILE_PLACEHOLDER", _context_file().replace("\\", "\\\\")
    ).strip()


with DAG(
    dag_id="fraudlens_transformation_workflow",
    description="Transformation workflow scaffold for Bronze, Silver, Gold, and KPI orchestration.",
    start_date=datetime(2026, 1, 1),
    schedule=schedule_for_profile(),
    catchup=False,
    max_active_runs=max_active_runs_for_profile(),
    dagrun_timeout=dagrun_timeout_for_profile(),
    default_args={
        "on_failure_callback": runtime_failure_callback,
    },
    tags=["fraudlens", "orchestration", "transformation", "dbt"],
    params={
        "profile": "local",
        "target": "local",
        "batch_id": "latest",
        "selector_override": "",
        "allow_partial": False,
        "layer_subset": "bronze,silver,gold,kpi",
        "full_refresh_layers": "",
        "threads": 4,
    },
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    with TaskGroup(group_id="prepare_dbt_context") as prepare_dbt_context:
        resolve_runtime_context = BashOperator(
            task_id="resolve_runtime_context",
            bash_command=_runtime_context_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("infra_transient"),
        )
        preflight_parse = BashOperator(
            task_id="preflight_parse",
            bash_command=_dbt_parse_with_status_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
        )
        resolve_runtime_context >> preflight_parse

    with TaskGroup(group_id="run_bronze_models") as run_bronze_models:
        bronze_build = BashOperator(
            task_id="build_bronze_models",
            bash_command=_stage_build_command("bronze", "tag:bronze"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("dbt_transform"),
        )
    bronze_success_gate = EmptyOperator(task_id="bronze_success_gate")

    with TaskGroup(group_id="run_silver_models") as run_silver_models:
        silver_build = BashOperator(
            task_id="build_silver_models",
            bash_command=_stage_build_command("silver", "tag:silver"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("dbt_transform"),
        )
    silver_success_gate = EmptyOperator(task_id="silver_success_gate")

    with TaskGroup(group_id="run_gold_models") as run_gold_models:
        gold_build = BashOperator(
            task_id="build_gold_models",
            bash_command=_stage_build_command("gold", "tag:gold"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("dbt_transform"),
        )
    gold_success_gate = EmptyOperator(task_id="gold_success_gate")

    with TaskGroup(group_id="run_kpi_models") as run_kpi_models:
        kpi_build = BashOperator(
            task_id="build_kpi_models",
            bash_command=_stage_build_command("kpi", "tag:kpi"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("dbt_transform"),
        )
    kpi_success_gate = EmptyOperator(task_id="kpi_success_gate")

    with TaskGroup(group_id="publish_transformation_metadata") as publish_transformation_metadata:
        publish_summary = BashOperator(
            task_id="publish_transformation_summary",
            bash_command=_publish_transformation_metadata_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("artifact_publish"),
        )

    (
        start
        >> prepare_dbt_context
        >> run_bronze_models
        >> bronze_success_gate
        >> run_silver_models
        >> silver_success_gate
        >> run_gold_models
        >> gold_success_gate
        >> run_kpi_models
        >> kpi_success_gate
        >> publish_transformation_metadata
        >> end
    )
