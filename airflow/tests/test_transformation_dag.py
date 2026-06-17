from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TRANSFORMATION_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_transformation_workflow.py"


class TransformationDagScaffoldTest(unittest.TestCase):
    def test_transformation_dag_is_syntax_valid(self) -> None:
        source = TRANSFORMATION_DAG_FILE.read_text(encoding="utf-8")
        compile(source, str(TRANSFORMATION_DAG_FILE), "exec")

    def test_transformation_dag_contains_expected_groups_and_gates(self) -> None:
        text = TRANSFORMATION_DAG_FILE.read_text(encoding="utf-8")
        expected_tokens = [
            'dag_id="fraudlens_transformation_workflow"',
            'group_id="prepare_dbt_context"',
            'group_id="run_bronze_models"',
            'group_id="run_silver_models"',
            'group_id="run_gold_models"',
            'group_id="run_kpi_models"',
            'group_id="publish_transformation_metadata"',
            'task_id="bronze_success_gate"',
            'task_id="silver_success_gate"',
            'task_id="gold_success_gate"',
            'task_id="kpi_success_gate"',
        ]
        for token in expected_tokens:
            self.assertIn(token, text)

    def test_transformation_dag_contains_dbt_command_contract_tokens(self) -> None:
        text = TRANSFORMATION_DAG_FILE.read_text(encoding="utf-8")
        command_tokens = [
            '"dbt"',
            '"parse"',
            '"run"',
            '"tag:bronze"',
            '"tag:silver"',
            '"tag:gold"',
            '"tag:kpi"',
            "selector_override",
            "allow_partial",
            "full_refresh_layers",
            "transformation_summary.json",
        ]
        for token in command_tokens:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
