from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import (
    REPO_ROOT,
    dagrun_timeout_for_profile,
    max_active_runs_for_profile,
    runtime_failure_callback,
    schedule_for_profile,
    task_policy_kwargs,
)


def _runtime_context_command() -> str:
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
    latest_batch_id,
    log_orchestration_event,
    orchestration_artifact_dir,
    resolve_orchestration_profile,
    utc_now_iso,
)

profile = resolve_orchestration_profile("{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}")
batch_id_input = "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}"
batch_id = latest_batch_id() if str(batch_id_input).strip().lower() in {"", "latest"} else str(batch_id_input).strip()
run_stamp = "{{ ts_nodash }}"

target_dir = orchestration_artifact_dir("pipeline", run_stamp)
target_dir.mkdir(parents=True, exist_ok=True)
target_file = target_dir / "runtime_context.json"
started_at_utc = utc_now_iso()
payload = {
    "dag_id": "fraudlens_pipeline_orchestration",
    "profile": profile,
    "batch_id": batch_id,
    "run_id": "{{ run_id }}",
    "run_stamp": run_stamp,
    "status": "prepared",
    "run_metadata": canonical_run_metadata(
        pipeline_run_id="{{ run_id }}",
        batch_id=batch_id,
        dag_id="fraudlens_pipeline_orchestration",
        task_id="resolve_runtime_context",
        task_group=infer_task_group("prepare_runtime.resolve_runtime_context"),
        run_profile=profile,
        run_target="local",
        execution_date_utc="{{ ts }}",
        started_at_utc=started_at_utc,
        ended_at_utc=started_at_utc,
        run_status="SUCCESS",
    ),
}
target_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
log_orchestration_event("INFO", "runtime_context_prepared", dag_id="fraudlens_pipeline_orchestration", batch_id=batch_id, run_id="{{ run_id }}")
print(json.dumps(payload))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).strip()


def _publish_summary_command() -> str:
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
    emit_lineage_event,
    emit_metric_event,
    infer_task_group,
    log_orchestration_event,
    observability_settings,
    parse_bool,
    utc_now_iso,
)

target = Path(r'REPO_ROOT_PLACEHOLDER') / "airflow" / "artifacts" / "orchestration" / "pipeline" / "{{ ts_nodash }}" / "pipeline_summary.json"
target.parent.mkdir(parents=True, exist_ok=True)
ended_at_utc = utc_now_iso()
workflow_root = Path(r'REPO_ROOT_PLACEHOLDER') / "airflow" / "artifacts" / "orchestration"
ingestion_summary = workflow_root / "ingestion" / "{{ ts_nodash }}" / "ingestion_summary.json"
transformation_summary = workflow_root / "transformation" / "{{ ts_nodash }}" / "transformation_summary.json"
validation_summary = workflow_root / "validation" / "{{ ts_nodash }}" / "validation_summary.json"

workflow_artifacts = {
    "ingestion_summary_file": str(ingestion_summary),
    "transformation_summary_file": str(transformation_summary),
    "validation_summary_file": str(validation_summary),
}
payload = {
    "dag_id": "fraudlens_pipeline_orchestration",
    "run_id": "{{ run_id }}",
    "pipeline_run_id": "{{ run_id }}",
    "batch_id": "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
    "run_profile": "{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
    "run_target": "local",
    "status": "success",
    "run_status": "SUCCESS",
    "failure_category": None,
    "execution_date_utc": "{{ ts }}",
    "ended_at_utc": ended_at_utc,
    "workflow_artifacts": workflow_artifacts,
    "run_metadata": canonical_run_metadata(
        pipeline_run_id="{{ run_id }}",
        batch_id="{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
        dag_id="fraudlens_pipeline_orchestration",
        task_id="publish_pipeline_summary",
        task_group=infer_task_group("publish_run_artifacts.publish_pipeline_summary"),
        run_profile="{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
        run_target="local",
        execution_date_utc="{{ ts }}",
        started_at_utc=ended_at_utc,
        ended_at_utc=ended_at_utc,
        run_status="SUCCESS",
    ),
    "note": "Issue #66 skeleton: transformation and validation DAG triggers are added in issues #68/#69.",
}
target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

completed_stage_artifacts = sum(
    1 for path in [ingestion_summary, transformation_summary, validation_summary] if path.exists()
)
artifact_completeness = completed_stage_artifacts / 3
run_profile = str(payload.get("run_profile", "local")).strip().lower() or "local"
obs_settings = observability_settings(run_profile)
obs_enabled = parse_bool(obs_settings.get("enabled"), default=True)
metrics_file = None
lineage_file = None
if obs_enabled and parse_bool(obs_settings.get("emit_metrics"), default=True):
    metrics_file = emit_metric_event(
        workflow="pipeline",
        run_stamp="{{ ts_nodash }}",
        metric_name="pipeline_run_status",
        metric_value=1.0,
        metric_type="gauge",
        run_profile=run_profile,
        payload={
            "dag_id": "fraudlens_pipeline_orchestration",
            "run_id": "{{ run_id }}",
            "batch_id": "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
            "run_profile": run_profile,
            "run_target": "local",
            "workflow": "pipeline",
            "run_status": "SUCCESS",
        },
    )
    emit_metric_event(
        workflow="pipeline",
        run_stamp="{{ ts_nodash }}",
        metric_name="pipeline_artifact_completeness",
        metric_value=float(artifact_completeness),
        metric_type="gauge",
        run_profile=run_profile,
        payload={
            "dag_id": "fraudlens_pipeline_orchestration",
            "run_id": "{{ run_id }}",
            "batch_id": "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
            "run_profile": run_profile,
            "run_target": "local",
            "workflow": "pipeline",
            "completed_stage_artifacts": completed_stage_artifacts,
            "expected_stage_artifacts": 3,
        },
    )
if obs_enabled and parse_bool(obs_settings.get("emit_lineage"), default=True):
    lineage_file = emit_lineage_event(
        workflow="pipeline",
        run_stamp="{{ ts_nodash }}",
        event_type="pipeline_run_completed",
        run_profile=run_profile,
        payload={
            "job_name": "fraudlens_pipeline_orchestration",
            "run_id": "{{ run_id }}",
            "batch_id": "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
            "run_profile": run_profile,
            "status": "SUCCESS",
            "inputs": [
                "data/batches/{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}"
            ],
            "outputs": [
                str(target),
                str(ingestion_summary),
                str(transformation_summary),
                str(validation_summary),
            ],
        },
    )
payload["observability_artifacts"] = {
    "metrics_file": str(metrics_file) if metrics_file else None,
    "lineage_file": str(lineage_file) if lineage_file else None,
}
target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
log_orchestration_event("INFO", "pipeline_summary_published", dag_id="fraudlens_pipeline_orchestration", run_id="{{ run_id }}", summary_file=str(target))
print(json.dumps(payload))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).strip()


with DAG(
    dag_id="fraudlens_pipeline_orchestration",
    description="Phase 6 master DAG skeleton for ingestion, transformation, and validation control gates.",
    start_date=datetime(2026, 1, 1),
    schedule=schedule_for_profile(),
    catchup=False,
    max_active_runs=max_active_runs_for_profile(),
    dagrun_timeout=dagrun_timeout_for_profile(),
    default_args={
        "on_failure_callback": runtime_failure_callback,
    },
    tags=["fraudlens", "orchestration", "airflow"],
    params={
        "profile": "local",
        "batch_id": "latest",
    },
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    with TaskGroup(group_id="prepare_runtime") as prepare_runtime:
        runtime_context = BashOperator(
            task_id="resolve_runtime_context",
            bash_command=_runtime_context_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("infra_transient"),
        )

    with TaskGroup(group_id="ingestion_layer") as ingestion_layer:
        ingestion_entry = EmptyOperator(task_id="ingestion_entrypoint")

    ingestion_complete_gate = EmptyOperator(task_id="ingestion_complete_gate")

    with TaskGroup(group_id="transformation_layer") as transformation_layer:
        transformation_entry = TriggerDagRunOperator(
            task_id="run_transformation_workflow",
            trigger_dag_id="fraudlens_transformation_workflow",
            wait_for_completion=True,
            poke_interval=30,
            **task_policy_kwargs("infra_transient"),
        )

    transformation_complete_gate = EmptyOperator(task_id="transformation_complete_gate")

    with TaskGroup(group_id="validation_layer") as validation_layer:
        validation_entry = TriggerDagRunOperator(
            task_id="run_validation_workflow",
            trigger_dag_id="fraudlens_validation_workflow",
            wait_for_completion=True,
            poke_interval=30,
            **task_policy_kwargs("infra_transient"),
        )

    with TaskGroup(group_id="publish_run_artifacts") as publish_run_artifacts:
        publish_summary = BashOperator(
            task_id="publish_pipeline_summary",
            bash_command=_publish_summary_command(),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("artifact_publish"),
        )

    (
        start
        >> prepare_runtime
        >> ingestion_layer
        >> ingestion_complete_gate
        >> transformation_layer
        >> transformation_complete_gate
        >> validation_layer
        >> publish_run_artifacts
        >> end
    )
