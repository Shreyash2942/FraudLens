from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ci import validate_python as validation


class PythonValidationTest(unittest.TestCase):
    def test_snapshot_omits_untracked_private_files_and_preserves_current_tracked_edits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "script.py").write_text("print('edited tracked source')")
            (root / ".env").write_text("PRIVATE=never copy")
            destination = Path(directory) / "snapshot"
            with patch.object(validation, "tracked_paths", return_value=["script.py"]):
                validation.copy_tracked_source(root, destination)
            self.assertEqual((destination / "script.py").read_text(), "print('edited tracked source')")
            self.assertFalse((destination / ".env").exists())

    def test_failed_empty_or_all_skipped_test_suite_cannot_pass(self) -> None:
        for exit_code, tests, failures, skipped in ((1, 1, 1, 0), (0, 0, 0, 0), (0, 1, 0, 1)):
            def fake_run(arguments, **kwargs):
                xml_path = Path(arguments[-1].split("=", 1)[1])
                xml_path.write_text(f'<testsuites><testsuite tests="{tests}" failures="{failures}" errors="0" skipped="{skipped}"/></testsuites>')
                self.assertEqual(kwargs["env"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"], "1")
                self.assertNotIn("MINIO_ENDPOINT", kwargs["env"])
                return subprocess.CompletedProcess(arguments, exit_code)
            with self.subTest(exit_code=exit_code, tests=tests, skipped=skipped), \
                 patch.dict(validation.os.environ, MINIO_ENDPOINT="must-not-inherit"), \
                 patch.object(validation, "copy_tracked_source"), \
                 patch.object(validation.subprocess, "run", side_effect=fake_run):
                report = {}
                self.assertFalse(validation.run_tests(validation.ROOT, report))
                self.assertNotIn("must-not-inherit", json.dumps(report))

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
