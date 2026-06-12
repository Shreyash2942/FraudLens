from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATION_PROFILE_FILE = REPO_ROOT / "airflow" / "config" / "orchestration_profiles.yml"
MASTER_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_pipeline_orchestration.py"
INGESTION_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_ingestion_workflow.py"
COMMON_FILE = REPO_ROOT / "airflow" / "dags" / "_fraudlens_orchestration_common.py"
BRONZE_INDEX_FILE = REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "sql" / "bronze" / "dataset_index.json"


class OrchestrationAirflowScaffoldTest(unittest.TestCase):
    def test_profile_contract_has_required_profiles(self) -> None:
        payload = yaml.safe_load(ORCHESTRATION_PROFILE_FILE.read_text(encoding="utf-8"))
        self.assertIsInstance(payload, dict)
        self.assertIn("defaults", payload)
        self.assertIn("profiles", payload)
        profiles = payload["profiles"]
        self.assertIn("local", profiles)
        self.assertIn("ci", profiles)
        self.assertIn("snowflake", profiles)

    def test_python_files_are_syntax_valid(self) -> None:
        for file_path in (COMMON_FILE, MASTER_DAG_FILE, INGESTION_DAG_FILE):
            source = file_path.read_text(encoding="utf-8")
            compile(source, str(file_path), "exec")

    def test_master_dag_contains_expected_topology_tokens(self) -> None:
        text = MASTER_DAG_FILE.read_text(encoding="utf-8")
        expected_tokens = [
            'dag_id="fraudlens_pipeline_orchestration"',
            'group_id="prepare_runtime"',
            'group_id="ingestion_layer"',
            'task_id="ingestion_complete_gate"',
            'group_id="transformation_layer"',
            'task_id="transformation_complete_gate"',
            'group_id="validation_layer"',
            'group_id="publish_run_artifacts"',
        ]
        for token in expected_tokens:
            self.assertIn(token, text)

    def test_master_dag_triggers_ingestion_workflow(self) -> None:
        text = MASTER_DAG_FILE.read_text(encoding="utf-8")
        self.assertIn('task_id="run_ingestion_workflow"', text)
        self.assertIn('trigger_dag_id="fraudlens_ingestion_workflow"', text)
        self.assertIn("conf=_stage_trigger_conf()", text)

    def test_ingestion_dag_contains_expected_task_groups(self) -> None:
        text = INGESTION_DAG_FILE.read_text(encoding="utf-8")
        expected_groups = [
            'group_id="prepare_context"',
            'group_id="load_bronze_datasets"',
            'group_id="validate_ingestion_results"',
            'group_id="publish_ingestion_metadata"',
        ]
        for token in expected_groups:
            self.assertIn(token, text)
        self.assertIn('dag_id="fraudlens_ingestion_workflow"', text)
        self.assertIn('task_id="ingestion_completion_gate"', text)

    def test_ingestion_dag_builds_dataset_tasks_from_bronze_index(self) -> None:
        payload = json.loads(BRONZE_INDEX_FILE.read_text(encoding="utf-8"))
        datasets = [row["dataset"] for row in payload["datasets"]]
        self.assertGreaterEqual(len(datasets), 21)
        text = INGESTION_DAG_FILE.read_text(encoding="utf-8")
        self.assertIn("for dataset_name in bronze_dataset_order()", text)


if __name__ == "__main__":
    unittest.main()
