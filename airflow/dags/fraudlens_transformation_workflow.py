from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import REPO_ROOT


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
  {_dbt_command("build")} --select "$SELECTOR" --full-refresh
else
  {_dbt_command("build")} --select "$SELECTOR"
fi
""".strip()


with DAG(
    dag_id="fraudlens_transformation_workflow",
    description="Transformation workflow scaffold for Bronze, Silver, Gold, and KPI orchestration.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fraudlens", "orchestration", "transformation", "dbt"],
    params={
        "profile": "local",
        "target": "local",
        "batch_id": "latest",
        "selector_override": "",
        "allow_partial": False,
        "layer_subset": "bronze,silver,gold,kpi",
        "full_refresh_layers": "",
    },
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    with TaskGroup(group_id="prepare_dbt_context") as prepare_dbt_context:
        preflight_parse = BashOperator(
            task_id="preflight_parse",
            bash_command=_dbt_command("parse"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="run_bronze_models") as run_bronze_models:
        bronze_build = BashOperator(
            task_id="build_bronze_models",
            bash_command=_stage_build_command("bronze", "tag:bronze"),
            cwd=REPO_ROOT.as_posix(),
        )
    bronze_success_gate = EmptyOperator(task_id="bronze_success_gate")

    with TaskGroup(group_id="run_silver_models") as run_silver_models:
        silver_build = BashOperator(
            task_id="build_silver_models",
            bash_command=_stage_build_command("silver", "tag:silver"),
            cwd=REPO_ROOT.as_posix(),
        )
    silver_success_gate = EmptyOperator(task_id="silver_success_gate")

    with TaskGroup(group_id="run_gold_models") as run_gold_models:
        gold_build = BashOperator(
            task_id="build_gold_models",
            bash_command=_stage_build_command("gold", "tag:gold"),
            cwd=REPO_ROOT.as_posix(),
        )
    gold_success_gate = EmptyOperator(task_id="gold_success_gate")

    with TaskGroup(group_id="run_kpi_models") as run_kpi_models:
        kpi_build = BashOperator(
            task_id="build_kpi_models",
            bash_command=_stage_build_command("kpi", "tag:kpi"),
            cwd=REPO_ROOT.as_posix(),
        )
    kpi_success_gate = EmptyOperator(task_id="kpi_success_gate")

    with TaskGroup(group_id="publish_transformation_metadata") as publish_transformation_metadata:
        publish_entry = EmptyOperator(task_id="publish_entry")

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
