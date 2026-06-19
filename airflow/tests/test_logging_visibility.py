from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_MODULE_PATH = REPO_ROOT / "airflow" / "dags" / "_fraudlens_orchestration_common.py"


def load_common_module():
    spec = importlib.util.spec_from_file_location("fraudlens_orchestration_common", COMMON_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load common module from {COMMON_MODULE_PATH}")
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


if __name__ == "__main__":
    unittest.main()
