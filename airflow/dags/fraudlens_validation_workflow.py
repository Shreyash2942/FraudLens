from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from _fraudlens_orchestration_common import REPO_ROOT


def _dbt_test_command(selector: str) -> str:
    return " ".join(
        [
            "dbt",
            "test",
            "--project-dir",
            "dbt",
            "--profiles-dir",
            "dbt/profiles",
            "--profile",
            "fraudlens_local_spark",
            "--target",
            "local",
            "--select",
            selector,
        ]
    )


def _dbt_parse_command() -> str:
    return " ".join(
        [
            "dbt",
            "parse",
            "--project-dir",
            "dbt",
            "--profiles-dir",
            "dbt/profiles",
            "--profile",
            "fraudlens_local_spark",
            "--target",
            "local",
        ]
    )


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
        preflight_parse = BashOperator(
            task_id="preflight_parse",
            bash_command=_dbt_parse_command(),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="validate_bronze_gate") as validate_bronze_gate:
        bronze_tag_test = BashOperator(
            task_id="bronze_tag_test",
            bash_command=_dbt_test_command("tag:bronze"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="validate_silver_gate") as validate_silver_gate:
        silver_tag_test = BashOperator(
            task_id="silver_tag_test",
            bash_command=_dbt_test_command("tag:silver"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="validate_gold_gate") as validate_gold_gate:
        gold_tag_test = BashOperator(
            task_id="gold_tag_test",
            bash_command=_dbt_test_command("tag:gold"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="validate_kpi_gate") as validate_kpi_gate:
        kpi_tag_test = BashOperator(
            task_id="kpi_tag_test",
            bash_command=_dbt_test_command("tag:kpi"),
            cwd=REPO_ROOT.as_posix(),
        )

    with TaskGroup(group_id="validate_governance_gate") as validate_governance_gate:
        quality_critical_gate_test = BashOperator(
            task_id="quality_critical_gate_test",
            bash_command=_dbt_test_command("quality_critical_gate"),
            cwd=REPO_ROOT.as_posix(),
        )
        governance_critical_gate_test = BashOperator(
            task_id="governance_critical_gate_test",
            bash_command=_dbt_test_command("governance_critical_gate"),
            cwd=REPO_ROOT.as_posix(),
        )
        contract_critical_gate_test = BashOperator(
            task_id="contract_critical_gate_test",
            bash_command=_dbt_test_command("contract_critical_gate"),
            cwd=REPO_ROOT.as_posix(),
        )
        audit_traceability_gate_test = BashOperator(
            task_id="audit_traceability_gate_test",
            bash_command=_dbt_test_command("audit_traceability_gate"),
            cwd=REPO_ROOT.as_posix(),
        )
        contract_metadata_validator = BashOperator(
            task_id="contract_metadata_validator",
            bash_command="python dbt/scripts/validate_contracts.py",
            cwd=REPO_ROOT.as_posix(),
            retries=0,
        )
        contract_alignment_validator = BashOperator(
            task_id="contract_alignment_validator",
            bash_command="python dbt/scripts/validate_contract_alignment.py",
            cwd=REPO_ROOT.as_posix(),
            retries=0,
        )
        failure_policy_validator = BashOperator(
            task_id="failure_policy_validator",
            bash_command="python dbt/scripts/validate_failure_policy.py",
            cwd=REPO_ROOT.as_posix(),
            retries=0,
        )
        (
            quality_critical_gate_test
            >> governance_critical_gate_test
            >> contract_critical_gate_test
            >> audit_traceability_gate_test
            >> contract_metadata_validator
            >> contract_alignment_validator
            >> failure_policy_validator
        )

    with TaskGroup(group_id="validate_publish_artifacts") as validate_publish_artifacts:
        publish_entry = EmptyOperator(task_id="publish_entry")

    checkpoint_bronze_to_silver = EmptyOperator(task_id="checkpoint_bronze_to_silver")
    checkpoint_silver_to_gold = EmptyOperator(task_id="checkpoint_silver_to_gold")
    checkpoint_gold_to_kpi = EmptyOperator(task_id="checkpoint_gold_to_kpi")
    checkpoint_kpi_to_publish = EmptyOperator(task_id="checkpoint_kpi_to_publish")

    (
        start
        >> validate_preflight
        >> validate_bronze_gate
        >> checkpoint_bronze_to_silver
        >> validate_silver_gate
        >> checkpoint_silver_to_gold
        >> validate_gold_gate
        >> checkpoint_gold_to_kpi
        >> validate_kpi_gate
        >> checkpoint_kpi_to_publish
        >> validate_governance_gate
        >> validate_publish_artifacts
        >> end
    )
