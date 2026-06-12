from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_FILE = REPO_ROOT / "airflow" / "dags" / "_fraudlens_orchestration_common.py"
PIPELINE_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_pipeline_orchestration.py"
INGESTION_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_ingestion_workflow.py"
TRANSFORMATION_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_transformation_workflow.py"
VALIDATION_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_validation_workflow.py"


class LoggingMetadataCompletenessTest(unittest.TestCase):
    def test_common_metadata_schema_fields_are_defined(self) -> None:
        source = COMMON_FILE.read_text(encoding="utf-8")
        expected_fields = [
            "RUN_METADATA_FIELDS",
            "pipeline_run_id",
            "batch_id",
            "dag_id",
            "task_id",
            "task_group",
            "run_profile",
            "run_target",
            "execution_date_utc",
            "started_at_utc",
            "ended_at_utc",
            "run_status",
            "failure_category",
            "canonical_run_metadata",
            "log_orchestration_event",
            "runtime_failure_callback",
            "artifact_backend_settings",
            "write_orchestration_artifact",
            "read_orchestration_artifact",
            "list_orchestration_artifacts",
        ]
        for token in expected_fields:
            self.assertIn(token, source)

    def test_workflow_summaries_include_run_metadata(self) -> None:
        for file_path in (
            PIPELINE_DAG_FILE,
            INGESTION_DAG_FILE,
            TRANSFORMATION_DAG_FILE,
            VALIDATION_DAG_FILE,
        ):
            source = file_path.read_text(encoding="utf-8")
            self.assertIn("run_metadata", source, msg=f"Missing run_metadata in {file_path.name}")
            self.assertIn("run_status", source, msg=f"Missing run_status in {file_path.name}")
            self.assertIn("pipeline_run_id", source, msg=f"Missing pipeline_run_id in {file_path.name}")
            self.assertIn("log_orchestration_event", source, msg=f"Missing structured logging in {file_path.name}")

    def test_runtime_policy_and_failure_artifact_hooks_present(self) -> None:
        source = COMMON_FILE.read_text(encoding="utf-8")
        self.assertIn("task_policy_kwargs", source)
        self.assertIn("classify_failure_category", source)
        self.assertIn('"orchestration" / "failures"', source)
        self.assertIn("artifact_backend", source)


if __name__ == "__main__":
    unittest.main()
