from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_FILE = REPO_ROOT / "airflow" / "dags" / "_fraudlens_orchestration_common.py"
PIPELINE_DAG_FILE = REPO_ROOT / "airflow" / "dags" / "fraudlens_pipeline_orchestration.py"
PROFILE_FILE = REPO_ROOT / "airflow" / "config" / "orchestration_profiles.yml"


class ObservabilityEmitterCoverageTest(unittest.TestCase):
    def test_common_helpers_define_observability_emitters(self) -> None:
        source = COMMON_FILE.read_text(encoding="utf-8")
        expected_tokens = [
            "observability_settings",
            "observability_enabled",
            "observability_artifact_dir",
            "emit_metric_event",
            "emit_lineage_event",
            '"artifacts" / "observability"',
        ]
        for token in expected_tokens:
            self.assertIn(token, source)

    def test_pipeline_summary_wires_metrics_and_lineage(self) -> None:
        source = PIPELINE_DAG_FILE.read_text(encoding="utf-8")
        expected_tokens = [
            "emit_metric_event",
            "emit_lineage_event",
            "pipeline_artifact_completeness",
            "pipeline_run_status",
            "observability_artifacts",
        ]
        for token in expected_tokens:
            self.assertIn(token, source)

    def test_profiles_include_observability_blocks(self) -> None:
        source = PROFILE_FILE.read_text(encoding="utf-8")
        for profile in ["local", "ci", "snowflake"]:
            self.assertIn(f"{profile}:", source)
        self.assertIn("observability:", source)
        self.assertIn("artifact_backend: mongodb", source)
        self.assertIn("mongodb_collection: orchestration_artifacts", source)
        self.assertIn("emit_metrics", source)
        self.assertIn("emit_lineage", source)


if __name__ == "__main__":
    unittest.main()
