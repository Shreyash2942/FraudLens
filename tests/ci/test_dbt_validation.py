from __future__ import annotations

import json
import subprocess
import unittest
from unittest.mock import patch

from scripts.ci import validate_dbt as validation


class DbtValidationTest(unittest.TestCase):
    def test_selector_rejects_empty_logs_and_non_test_results(self) -> None:
        for output in ("", "\n", "Running with dbt=1.8.7", '{"msg":"No nodes selected"}',
                       '{"unique_id":"model.fake", "resource_type":"model"}'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                validation.selected_test_count(output)

    def test_selector_counts_unique_test_records(self) -> None:
        record = json.dumps({"unique_id": "test.fraudlens.example", "resource_type": "test"})
        self.assertEqual(validation.selected_test_count(record + "\n" + record), 1)

    def test_validation_rejects_missing_parse_and_changed_manifest(self) -> None:
        with patch.object(validation, "execute") as execute:
            with self.assertRaises(ValueError):
                validation.run_stage("validate", {"stages": {}})
            with patch.object(validation, "manifest_summary", return_value={"sha256": "changed"}):
                with self.assertRaises(ValueError):
                    validation.run_stage("validate", self.parsed_report())
            execute.assert_not_called()

    @staticmethod
    def parsed_report() -> dict:
        return {"stages": {"parse": {"status": "success"}}, "manifest": {"sha256": "original"}}

    def test_parse_failure_removes_stale_manifest_and_stops(self) -> None:
        with patch.object(validation, "MANIFEST") as manifest, patch.object(validation, "execute") as execute:
            execute.side_effect = subprocess.CalledProcessError(2, "dbt")
            with self.assertRaises(subprocess.CalledProcessError):
                validation.run_stage("parse", {})
            manifest.unlink.assert_called_once_with(missing_ok=True)
            manifest.read_bytes.assert_not_called()

    def test_validator_failure_prevents_later_checks_and_docs(self) -> None:
        selected = json.dumps({"unique_id": "test.fraudlens.example", "resource_type": "test"})
        success = subprocess.CompletedProcess([], 0, stdout=selected)
        report = self.parsed_report()
        with patch.object(validation, "manifest_summary", return_value=report["manifest"]), \
             patch.object(validation, "execute", side_effect=[success, success, subprocess.CalledProcessError(1, "naming")]) as execute:
            with self.assertRaises(subprocess.CalledProcessError):
                validation.run_stage("validate", report)
            self.assertEqual(execute.call_count, 3)
            self.assertEqual(report["checks"]["naming_rules"]["status"], "failure")
            self.assertNotIn("docs", report["checks"])

    def test_all_legacy_validators_and_both_selectors_are_required(self) -> None:
        selected = json.dumps({"unique_id": "test.fraudlens.example", "resource_type": "test"})
        report = self.parsed_report()
        with patch.object(validation, "manifest_summary", return_value=report["manifest"]), \
             patch.object(validation, "execute", return_value=subprocess.CompletedProcess([], 0, stdout=selected)) as execute:
            validation.run_stage("validate", report)
        self.assertEqual(len(report["checks"]), 8)
        self.assertTrue(all(check["status"] == "success" for check in report["checks"].values()))
        self.assertEqual(execute.call_count, 8)
        self.assertIn("--no-compile", execute.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
