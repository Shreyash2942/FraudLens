from __future__ import annotations

import json
import subprocess
import unittest
from unittest.mock import patch

from scripts.ci import validate_python as validation


class PythonValidationTest(unittest.TestCase):
    def test_lint_uses_only_explicit_tracked_python_files(self) -> None:
        with patch.object(validation, "tracked_paths", return_value=["script.py", "README.md"]), \
             patch.object(validation.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "[]")) as run:
            report = {}
            self.assertTrue(validation.lint(validation.ROOT, report))
        self.assertEqual(run.call_args.args[0][-2:], ["--", "script.py"])
        self.assertIn("--no-fix", run.call_args.args[0])
        self.assertEqual(report["python_files"], 1)

    def test_lint_failure_records_location_without_source_or_message(self) -> None:
        output = json.dumps([{"filename": str(validation.ROOT / "script.py"), "code": "F821",
                              "location": {"row": 2, "column": 3}, "message": "sensitive source omitted"}])
        with patch.object(validation, "tracked_paths", return_value=["script.py"]), \
             patch.object(validation.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, output)):
            report = {}
            self.assertFalse(validation.lint(validation.ROOT, report))
        self.assertEqual(report["lint_errors"], [{"path": "script.py", "rule": "F821", "line": 2, "column": 3}])
        self.assertNotIn("sensitive", json.dumps(report))

    def test_missing_inventory_or_linter_failure_cannot_pass(self) -> None:
        with patch.object(validation, "tracked_paths", return_value=[]), self.assertRaises(ValueError):
            validation.lint(validation.ROOT, {})
        with patch.object(validation, "tracked_paths", return_value=["script.py"]), \
             patch.object(validation.subprocess, "run", return_value=subprocess.CompletedProcess([], 2, "")), \
             self.assertRaises(ValueError):
            validation.lint(validation.ROOT, {})


if __name__ == "__main__":
    unittest.main()
