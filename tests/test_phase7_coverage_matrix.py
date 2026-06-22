from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_MATRIX = REPO_ROOT / "monitoring" / "coverage" / "observability-lineage-coverage.json"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_observability_lineage_coverage.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_observability_lineage_coverage", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load validator module from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase7CoverageMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = json.loads(COVERAGE_MATRIX.read_text(encoding="utf-8"))
        cls.validator = load_validator_module()

    def test_critical_services_are_represented(self) -> None:
        services = {item["service"] for item in self.matrix["critical_services"]}
        self.assertEqual(
            services,
            {"airflow", "prometheus", "grafana", "openlineage", "marquez"},
        )

    def test_coverage_validator_accepts_matrix(self) -> None:
        result = self.validator.validate_matrix(self.matrix, repo_root=REPO_ROOT)
        self.assertTrue(result["valid"], msg=result)
        self.assertEqual(result["missing_services"], [])
        self.assertEqual(result["missing_layers"], [])
        self.assertEqual(result["missing_evidence"], [])


if __name__ == "__main__":
    unittest.main()
