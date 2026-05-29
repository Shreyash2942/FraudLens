from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import REPO_ROOT


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

from _fraudlens_orchestration_common import latest_batch_id, orchestration_artifact_dir, resolve_orchestration_profile

profile = resolve_orchestration_profile("{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}")
batch_id_input = "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}"
batch_id = latest_batch_id() if str(batch_id_input).strip().lower() in {"", "latest"} else str(batch_id_input).strip()
run_stamp = "{{ ts_nodash }}"

target_dir = orchestration_artifact_dir("pipeline", run_stamp)
target_dir.mkdir(parents=True, exist_ok=True)
target_file = target_dir / "runtime_context.json"
payload = {
    "dag_id": "fraudlens_pipeline_orchestration",
    "profile": profile,
    "batch_id": batch_id,
    "run_id": "{{ run_id }}",
    "run_stamp": run_stamp,
    "status": "prepared",
}
target_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
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

target = Path(r'REPO_ROOT_PLACEHOLDER') / "airflow" / "artifacts" / "orchestration" / "pipeline" / "{{ ts_nodash }}" / "pipeline_summary.json"
target.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "dag_id": "fraudlens_pipeline_orchestration",
    "run_id": "{{ run_id }}",
    "batch_id": "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
    "profile": "{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
    "status": "success",
    "note": "Issue #66 skeleton: transformation and validation DAG triggers are added in issues #68/#69.",
}
target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).strip()


with DAG(
    dag_id="fraudlens_pipeline_orchestration",
    description="Phase 6 master DAG skeleton for ingestion, transformation, and validation control gates.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
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
        )

    transformation_complete_gate = EmptyOperator(task_id="transformation_complete_gate")

    with TaskGroup(group_id="validation_layer") as validation_layer:
        validation_entry = TriggerDagRunOperator(
            task_id="run_validation_workflow",
            trigger_dag_id="fraudlens_validation_workflow",
            wait_for_completion=True,
            poke_interval=30,
        )

    with TaskGroup(group_id="publish_run_artifacts") as publish_run_artifacts:
        publish_summary = BashOperator(
            task_id="publish_pipeline_summary",
            bash_command=_publish_summary_command(),
            cwd=REPO_ROOT.as_posix(),
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
