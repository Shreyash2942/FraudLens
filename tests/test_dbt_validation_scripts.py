from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
NAMING_SCRIPT = REPO_ROOT / "dbt" / "scripts" / "validate_naming_rules.py"


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DbtNamingValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.naming_module = _load_module(NAMING_SCRIPT, "validate_naming_rules")

    def test_lowercase_snake_case_alias_passes_for_bronze_model(self) -> None:
        manifest = {
            "nodes": {
                "model.fraudlens.stg_bronze__party": {
                    "resource_type": "model",
                    "name": "stg_bronze__party",
                    "original_file_path": "models/bronze/stg_bronze__party.sql",
                    "alias": "bronze_stg_party",
                    "tags": ["bronze", "staging_raw"],
                    "columns": {
                        "party_id": {},
                        "ingestion_batch_id": {},
                    },
                }
            }
        }

        errors, checked = self.naming_module._validate_model_naming(manifest)
        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_uppercase_alias_fails_validation(self) -> None:
        manifest = {
            "nodes": {
                "model.fraudlens.slv__party": {
                    "resource_type": "model",
                    "name": "slv__party",
                    "original_file_path": "models/silver/slv__party.sql",
                    "alias": "SILVER_PARTY",
                    "tags": ["silver", "conformed"],
                    "columns": {
                        "party_id": {},
                    },
                }
            }
        }

        errors, checked = self.naming_module._validate_model_naming(manifest)
        self.assertEqual(checked, 1)
        self.assertIn("alias must be lowercase snake_case", errors[0])


if __name__ == "__main__":
    unittest.main()
