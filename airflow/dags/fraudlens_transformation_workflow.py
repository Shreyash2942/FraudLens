from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import REPO_ROOT


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
        prepare_entry = EmptyOperator(task_id="prepare_entry")

    with TaskGroup(group_id="run_bronze_models") as run_bronze_models:
        bronze_entry = EmptyOperator(task_id="bronze_entry")

    with TaskGroup(group_id="run_silver_models") as run_silver_models:
        silver_entry = EmptyOperator(task_id="silver_entry")

    with TaskGroup(group_id="run_gold_models") as run_gold_models:
        gold_entry = EmptyOperator(task_id="gold_entry")

    with TaskGroup(group_id="run_kpi_models") as run_kpi_models:
        kpi_entry = EmptyOperator(task_id="kpi_entry")

    with TaskGroup(group_id="publish_transformation_metadata") as publish_transformation_metadata:
        publish_entry = EmptyOperator(task_id="publish_entry")

    start >> prepare_dbt_context >> run_bronze_models >> run_silver_models >> run_gold_models >> run_kpi_models >> publish_transformation_metadata >> end

