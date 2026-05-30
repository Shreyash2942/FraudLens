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


def _validation_status_file(check_name: str) -> str:
    return str((REPO_ROOT / "airflow" / "artifacts" / "orchestration" / "validation" / "{{ ts_nodash }}" / "checks" / f"{check_name}.json").as_posix())


def _command_with_status(check_name: str, base_command: str) -> str:
    return f"""
set +e
{base_command}
RC=$?
export RC
python - <<'PY'
import json
import os
from pathlib import Path

target = Path(r'VALIDATION_STATUS_FILE_PLACEHOLDER')
target.parent.mkdir(parents=True, exist_ok=True)
exit_code = int(os.environ.get("RC", "1"))
payload = {{
    "check_name": "{check_name}",
    "exit_code": exit_code,
    "status": "success" if exit_code == 0 else "failed",
}}
target.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(payload))
PY
exit $RC
""".replace(
        "VALIDATION_STATUS_FILE_PLACEHOLDER", _validation_status_file(check_name).replace("\\", "\\\\")
    ).strip()


def _publish_validation_evidence_command() -> str:
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
from _fraudlens_orchestration_common import canonical_run_metadata, infer_task_group

artifact_root = Path(r'VALIDATION_ARTIFACT_ROOT_PLACEHOLDER')
status_dir = artifact_root / "checks"
status_rows = []
if status_dir.exists():
    for entry in sorted(status_dir.glob("*.json")):
        status_rows.append(json.loads(entry.read_text(encoding="utf-8")))

overall_status = "success"
if any(row.get("status") != "success" for row in status_rows):
    overall_status = "failed"

summary = {
    "dag_id": "fraudlens_validation_workflow",
    "run_id": "{{ run_id }}",
    "pipeline_run_id": "{{ run_id }}",
    "run_stamp": "{{ ts_nodash }}",
    "run_profile": "{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
    "run_target": "{{ (dag_run.conf if dag_run else {}).get('target', params.target) }}",
    "batch_id": "{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
    "execution_date_utc": "{{ ts }}",
    "check_status": status_rows,
    "run_status": "SUCCESS" if overall_status == "success" else "FAILED",
    "failure_category": None if overall_status == "success" else "governance_block",
    "ended_at_utc": utc_now_iso(),
}
summary["run_metadata"] = canonical_run_metadata(
    pipeline_run_id="{{ run_id }}",
    batch_id="{{ (dag_run.conf if dag_run else {}).get('batch_id', params.batch_id) }}",
    dag_id="fraudlens_validation_workflow",
    task_id="publish_validation_evidence",
    task_group=infer_task_group("validate_publish_artifacts.publish_validation_evidence"),
    run_profile="{{ (dag_run.conf if dag_run else {}).get('profile', params.profile) }}",
    run_target="{{ (dag_run.conf if dag_run else {}).get('target', params.target) }}",
    execution_date_utc="{{ ts }}",
    started_at_utc=str(summary.get("ended_at_utc", "")),
    ended_at_utc=str(summary.get("ended_at_utc", "")),
    run_status=str(summary.get("run_status", "UNKNOWN")),
    failure_category=summary.get("failure_category"),
)
target = artifact_root / "validation_summary.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
log_orchestration_event("INFO", "validation_summary_published", dag_id="fraudlens_validation_workflow", run_id="{{ run_id }}", summary_file=str(target))
print(json.dumps({"status": "published", "summary_file": str(target), "overall_status": overall_status}))
PY
""".replace(
        "REPO_ROOT_PLACEHOLDER", REPO_ROOT.as_posix()
    ).replace(
        "VALIDATION_ARTIFACT_ROOT_PLACEHOLDER",
        str((REPO_ROOT / "airflow" / "artifacts" / "orchestration" / "validation" / "{{ ts_nodash }}").as_posix()).replace(
            "\\", "\\\\"
        ),
    ).strip()


with DAG(
    dag_id="fraudlens_validation_workflow",
    description="Validation workflow scaffold for quality, governance, and checkpoint controls.",
    start_date=datetime(2026, 1, 1),
    schedule=schedule_for_profile(),
    catchup=False,
    max_active_runs=max_active_runs_for_profile(),
    dagrun_timeout=dagrun_timeout_for_profile(),
    default_args={
        "on_failure_callback": runtime_failure_callback,
    },
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
            bash_command=_command_with_status("preflight_parse", _dbt_parse_command()),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
        )

    with TaskGroup(group_id="validate_bronze_gate") as validate_bronze_gate:
        bronze_tag_test = BashOperator(
            task_id="bronze_tag_test",
            bash_command=_command_with_status("bronze_tag_test", _dbt_test_command("tag:bronze")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )

    with TaskGroup(group_id="validate_silver_gate") as validate_silver_gate:
        silver_tag_test = BashOperator(
            task_id="silver_tag_test",
            bash_command=_command_with_status("silver_tag_test", _dbt_test_command("tag:silver")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )

    with TaskGroup(group_id="validate_gold_gate") as validate_gold_gate:
        gold_tag_test = BashOperator(
            task_id="gold_tag_test",
            bash_command=_command_with_status("gold_tag_test", _dbt_test_command("tag:gold")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )

    with TaskGroup(group_id="validate_kpi_gate") as validate_kpi_gate:
        kpi_tag_test = BashOperator(
            task_id="kpi_tag_test",
            bash_command=_command_with_status("kpi_tag_test", _dbt_test_command("tag:kpi")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )

    with TaskGroup(group_id="validate_governance_gate") as validate_governance_gate:
        quality_critical_gate_test = BashOperator(
            task_id="quality_critical_gate_test",
            bash_command=_command_with_status("quality_critical_gate_test", _dbt_test_command("quality_critical_gate")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )
        governance_critical_gate_test = BashOperator(
            task_id="governance_critical_gate_test",
            bash_command=_command_with_status("governance_critical_gate_test", _dbt_test_command("governance_critical_gate")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )
        contract_critical_gate_test = BashOperator(
            task_id="contract_critical_gate_test",
            bash_command=_command_with_status("contract_critical_gate_test", _dbt_test_command("contract_critical_gate")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )
        audit_traceability_gate_test = BashOperator(
            task_id="audit_traceability_gate_test",
            bash_command=_command_with_status("audit_traceability_gate_test", _dbt_test_command("audit_traceability_gate")),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("validation_gate"),
        )
        contract_metadata_validator = BashOperator(
            task_id="contract_metadata_validator",
            bash_command=_command_with_status("contract_metadata_validator", "python dbt/scripts/validate_contracts.py"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
        )
        contract_alignment_validator = BashOperator(
            task_id="contract_alignment_validator",
            bash_command=_command_with_status("contract_alignment_validator", "python dbt/scripts/validate_contract_alignment.py"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
        )
        failure_policy_validator = BashOperator(
            task_id="failure_policy_validator",
            bash_command=_command_with_status("failure_policy_validator", "python dbt/scripts/validate_failure_policy.py"),
            cwd=REPO_ROOT.as_posix(),
            **task_policy_kwargs("deterministic_contract"),
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
        publish_validation_evidence = BashOperator(
            task_id="publish_validation_evidence",
            bash_command=_publish_validation_evidence_command(),
            cwd=REPO_ROOT.as_posix(),
            trigger_rule="all_done",
            **task_policy_kwargs("artifact_publish"),
        )

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
