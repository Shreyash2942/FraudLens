from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_MODULE_PATH = REPO_ROOT / "airflow" / "dags" / "_fraudlens_orchestration_common.py"
ARTIFACT_LOCATOR_PATH = REPO_ROOT / "scripts" / "locate_latest_airflow_artifacts.py"


def load_common_module():
    spec = importlib.util.spec_from_file_location("fraudlens_orchestration_common", COMMON_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load common module from {COMMON_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_artifact_locator_module():
    spec = importlib.util.spec_from_file_location("locate_latest_airflow_artifacts", ARTIFACT_LOCATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load artifact locator from {ARTIFACT_LOCATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LoggingVisibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = load_common_module()

    def test_log_context_fields_cover_debugging_correlation(self) -> None:
        expected_fields = {
            "pipeline_run_id",
            "batch_id",
            "dag_id",
            "task_id",
            "task_group",
            "run_profile",
            "run_target",
            "workflow",
            "stage",
            "status",
            "failure_category",
            "artifact_reference",
        }
        self.assertTrue(expected_fields.issubset(set(self.common.LOG_CONTEXT_FIELDS)))

    def test_failure_category_classifier_supports_triage_taxonomy(self) -> None:
        cases = [
            ("check_input_assets", "missing input", "infra_transient"),
            ("validate_contract_alignment", "contract mismatch", "config_contract"),
            ("run_quality_gate", "accepted values failed", "data_quality"),
            ("publish_governance_traceability", "policy blocked", "governance_block"),
            ("unknown_task", "unexpected failure", "unknown"),
        ]
        for task_id, error_text, expected_category in cases:
            with self.subTest(task_id=task_id):
                self.assertEqual(self.common.classify_failure_category(task_id, error_text), expected_category)

    def test_structured_logger_redacts_sensitive_values(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            self.common.log_orchestration_event(
                "info",
                "credential_probe",
                batch_id="batch_001",
                password="plain-text",
                nested={"access_token": "token-value", "safe_field": "visible"},
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["level"], "INFO")
        self.assertEqual(payload["event"], "credential_probe")
        self.assertEqual(payload["batch_id"], "batch_001")
        self.assertEqual(payload["password"], self.common.REDACTED_LOG_VALUE)
        self.assertEqual(payload["nested"]["access_token"], self.common.REDACTED_LOG_VALUE)
        self.assertEqual(payload["nested"]["safe_field"], "visible")

    def test_artifact_locator_returns_latest_workflow_references(self) -> None:
        locator = load_artifact_locator_module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            locator.REPO_ROOT = temporary_root
            locator.AIRFLOW_ARTIFACT_ROOT = temporary_root / "airflow" / "artifacts"

            metric_file = locator.AIRFLOW_ARTIFACT_ROOT / "observability" / "metrics" / "pipeline" / "run_002" / "metric_events.jsonl"
            failure_file = locator.AIRFLOW_ARTIFACT_ROOT / "orchestration" / "failures" / "pipeline" / "run_001" / "task.json"
            unrelated_file = locator.AIRFLOW_ARTIFACT_ROOT / "observability" / "lineage" / "validation" / "run_003" / "lineage_events.jsonl"
            for artifact_file in (metric_file, failure_file, unrelated_file):
                artifact_file.parent.mkdir(parents=True, exist_ok=True)
                artifact_file.write_text("{}\n", encoding="utf-8")

            payload = locator.locate_latest_artifacts(workflow="pipeline", limit=10)

        references = {artifact["artifact_reference"] for artifact in payload["artifacts"]}
        kinds = {artifact["artifact_kind"] for artifact in payload["artifacts"]}
        self.assertEqual(payload["workflow"], "pipeline")
        self.assertIn("airflow/artifacts/observability/metrics/pipeline/run_002/metric_events.jsonl", references)
        self.assertIn("airflow/artifacts/orchestration/failures/pipeline/run_001/task.json", references)
        self.assertNotIn("airflow/artifacts/observability/lineage/validation/run_003/lineage_events.jsonl", references)
        self.assertIn("metric", kinds)
        self.assertIn("failure", kinds)


if __name__ == "__main__":
    unittest.main()
