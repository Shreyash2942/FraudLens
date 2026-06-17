from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_validation_workflow.py"
PIPELINE_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_pipeline_orchestration.py"


class ValidationDagScaffoldTest(unittest.TestCase):
    def test_validation_dag_is_syntax_valid(self) -> None:
        source = VALIDATION_DAG_FILE.read_text(encoding="utf-8")
        compile(source, str(VALIDATION_DAG_FILE), "exec")

    def test_validation_dag_contains_expected_gate_and_checkpoint_tokens(self) -> None:
        text = VALIDATION_DAG_FILE.read_text(encoding="utf-8")
        expected_tokens = [
            'dag_id="fraudlens_validation_workflow"',
            'group_id="validate_preflight"',
            'group_id="validate_bronze_gate"',
            'group_id="validate_silver_gate"',
            'group_id="validate_gold_gate"',
            'group_id="validate_kpi_gate"',
            'group_id="validate_governance_gate"',
            'group_id="validate_publish_artifacts"',
            'task_id="checkpoint_bronze_to_silver"',
            'task_id="checkpoint_silver_to_gold"',
            'task_id="checkpoint_gold_to_kpi"',
            'task_id="checkpoint_kpi_to_publish"',
            'task_id="publish_validation_evidence"',
            'trigger_rule="all_done"',
        ]
        for token in expected_tokens:
            self.assertIn(token, text)

    def test_validation_dag_contains_blocking_policy_validators(self) -> None:
        text = VALIDATION_DAG_FILE.read_text(encoding="utf-8")
        expected_tokens = [
            "validate_contracts.py",
            "validate_contract_alignment.py",
            "validate_failure_policy.py",
            "quality_critical_gate",
            "governance_critical_gate",
            "contract_critical_gate",
            "audit_traceability_gate",
        ]
        for token in expected_tokens:
            self.assertIn(token, text)

    def test_pipeline_dag_wires_validation_workflow_trigger(self) -> None:
        text = PIPELINE_DAG_FILE.read_text(encoding="utf-8")
        self.assertIn('trigger_dag_id="fraudlens_validation_workflow"', text)
        self.assertIn('task_id="run_validation_workflow"', text)


if __name__ == "__main__":
    unittest.main()

