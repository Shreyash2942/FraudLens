from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup


with DAG(
    dag_id="fraudlens_validation_workflow",
    description="Validation workflow scaffold for quality, governance, and checkpoint controls.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fraudlens", "orchestration", "validation", "dbt"],
    params={
        "profile": "local",
        "target": "local",
        "batch_id": "latest",
    },
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    with TaskGroup(group_id="validate_preflight") as validate_preflight:
        preflight_entry = EmptyOperator(task_id="preflight_entry")

    with TaskGroup(group_id="validate_bronze_gate") as validate_bronze_gate:
        bronze_gate_entry = EmptyOperator(task_id="bronze_gate_entry")

    with TaskGroup(group_id="validate_silver_gate") as validate_silver_gate:
        silver_gate_entry = EmptyOperator(task_id="silver_gate_entry")

    with TaskGroup(group_id="validate_gold_gate") as validate_gold_gate:
        gold_gate_entry = EmptyOperator(task_id="gold_gate_entry")

    with TaskGroup(group_id="validate_kpi_gate") as validate_kpi_gate:
        kpi_gate_entry = EmptyOperator(task_id="kpi_gate_entry")

    with TaskGroup(group_id="validate_governance_gate") as validate_governance_gate:
        governance_entry = EmptyOperator(task_id="governance_entry")

    with TaskGroup(group_id="validate_publish_artifacts") as validate_publish_artifacts:
        publish_entry = EmptyOperator(task_id="publish_entry")

    start >> validate_preflight >> validate_bronze_gate >> validate_silver_gate >> validate_gold_gate >> validate_kpi_gate >> validate_governance_gate >> validate_publish_artifacts >> end

