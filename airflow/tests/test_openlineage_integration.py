from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_MODULE_PATH = REPO_ROOT / "airflow" / "dags" / "_fraudlens_orchestration_common.py"
PROFILE_CONFIG = REPO_ROOT / "airflow" / "config" / "orchestration_profiles.yml"


def load_common_module():
    spec = importlib.util.spec_from_file_location("fraudlens_orchestration_common_openlineage", COMMON_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load common module from {COMMON_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OpenLineageIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = load_common_module()

    def test_profiles_define_openlineage_settings(self) -> None:
        source = PROFILE_CONFIG.read_text(encoding="utf-8")
        for token in (
            "openlineage_enabled",
            "openlineage_transport",
            "openlineage_url_env",
            "openlineage_default_url",
            "openlineage_producer",
        ):
            self.assertIn(token, source)

    def test_openlineage_builder_maps_successful_run(self) -> None:
        event = self.common.build_openlineage_event(
            job_name="fraudlens_pipeline_orchestration",
            run_id="manual__2026-06-20",
            run_profile="local",
            event_time_utc="2026-06-20T00:00:00Z",
            status="SUCCESS",
            batch_id="batch_001",
            inputs=["data/batches/batch_001"],
            outputs=["airflow/artifacts/orchestration/pipeline/summary.json"],
            namespace="fraudlens.orchestration.local",
        )

        self.assertEqual(event["eventType"], "COMPLETE")
        self.assertEqual(event["run"]["runId"], "manual__2026-06-20")
        self.assertEqual(event["job"]["namespace"], "fraudlens.orchestration.local")
        self.assertEqual(event["inputs"][0]["name"], "data/batches/batch_001")
        self.assertEqual(event["outputs"][0]["name"], "airflow/artifacts/orchestration/pipeline/summary.json")
        self.assertEqual(event["run"]["facets"]["fraudlens_run"]["batch_id"], "batch_001")

    def test_emit_lineage_event_writes_openlineage_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            original_repo_root = self.common.REPO_ROOT
            original_profile = os.environ.get("ORCHESTRATION_PROFILE")
            self.common.REPO_ROOT = Path(temporary_directory)
            os.environ["ORCHESTRATION_PROFILE"] = "local"
            try:
                with patch.object(self.common, "artifact_backend_settings", return_value={"backend": "filesystem"}):
                    target = self.common.emit_lineage_event(
                        workflow="pipeline",
                        run_stamp="20260620T000000",
                        event_type="pipeline_run_completed",
                        run_profile="local",
                        payload={
                            "job_name": "fraudlens_pipeline_orchestration",
                            "run_id": "manual__2026-06-20",
                            "batch_id": "batch_001",
                            "run_profile": "local",
                            "status": "SUCCESS",
                            "inputs": ["data/batches/batch_001"],
                            "outputs": ["airflow/artifacts/orchestration/pipeline/summary.json"],
                        },
                    )
            finally:
                self.common.REPO_ROOT = original_repo_root
                if original_profile is None:
                    os.environ.pop("ORCHESTRATION_PROFILE", None)
                else:
                    os.environ["ORCHESTRATION_PROFILE"] = original_profile

            payload = json.loads(target.read_text(encoding="utf-8").strip())

        self.assertEqual(payload["openlineage_schema_version"], self.common.OPENLINEAGE_EVENT_SCHEMA_VERSION)
        self.assertEqual(payload["openlineage_event"]["eventType"], "COMPLETE")
        self.assertEqual(payload["openlineage_event"]["job"]["name"], "fraudlens_pipeline_orchestration")
        self.assertEqual(payload["openlineage_event"]["inputs"][0]["name"], "data/batches/batch_001")


if __name__ == "__main__":
    unittest.main()
