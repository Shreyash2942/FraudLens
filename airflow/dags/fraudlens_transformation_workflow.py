from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import REPO_ROOT


def _dbt_command(action: str, selector: str | None = None) -> str:
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
    return " ".join(parts)


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
            bash_command=_dbt_command("build", "tag:bronze"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="run_silver_models") as run_silver_models:
        silver_build = BashOperator(
            task_id="build_silver_models",
            bash_command=_dbt_command("build", "tag:silver"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="run_gold_models") as run_gold_models:
        gold_build = BashOperator(
            task_id="build_gold_models",
            bash_command=_dbt_command("build", "tag:gold"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="run_kpi_models") as run_kpi_models:
        kpi_build = BashOperator(
            task_id="build_kpi_models",
            bash_command=_dbt_command("build", "tag:kpi"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="publish_transformation_metadata") as publish_transformation_metadata:
        publish_entry = EmptyOperator(task_id="publish_entry")

    start >> prepare_dbt_context >> run_bronze_models >> run_silver_models >> run_gold_models >> run_kpi_models >> publish_transformation_metadata >> end
