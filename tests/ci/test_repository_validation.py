from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("ci_repository_validation", ROOT / "scripts/ci/validate_repository.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RepositoryValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.track("README.md", "# Fixture\n")

    def track(self, name: str, content: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "-f", "--", name], cwd=self.root, check=True, capture_output=True)

    def validate(self):
        return VALIDATOR.validate_repository(self.root, required_paths=("README.md",))

    def test_parses_tracked_sources_without_executing_them(self) -> None:
        self.track("source.py", "raise RuntimeError('must never execute')\n")
        self.track("config.yaml", "enabled: true\n")
        result = self.validate()
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["counts"]["python"], 1)
        self.assertEqual(result["counts"]["yaml"], 1)

    def test_python_failure_is_blocking_and_omits_source_content(self) -> None:
        self.track("broken.py", "confidential_value = (\n")
        result = self.validate()
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "python_syntax")
        self.assertNotIn("confidential_value", json.dumps(result))

    def test_yaml_failure_is_blocking_and_omits_source_content(self) -> None:
        self.track("broken.yaml", "confidential_value: [\n")
        result = self.validate()
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "yaml_syntax")
        self.assertNotIn("confidential_value", json.dumps(result))

    def test_private_and_generated_files_are_rejected_without_reading_values(self) -> None:
        for name in (".env", "synthetic_generator/runtime_config.yaml", "dbt/target/manifest.json"):
            self.track(name, "confidential_value")
        result = self.validate()
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 3)
        self.assertTrue(all(error["code"] == "private_or_generated_file_tracked" for error in result["errors"]))
        self.assertNotIn("confidential_value", json.dumps(result))

    def test_ignored_private_configuration_is_not_a_validation_input(self) -> None:
        self.track(".gitignore", ".env\n")
        (self.root / ".env").write_text("confidential_value", encoding="utf-8")
        self.assertTrue(self.validate()["valid"])

    def test_missing_required_file_fails(self) -> None:
        result = VALIDATOR.validate_repository(self.root, required_paths=("missing.md",))
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "required_file_untracked")

    def test_missing_tracked_file_and_non_git_workspace_fail(self) -> None:
        (self.root / "README.md").unlink()
        self.assertFalse(self.validate()["valid"])
        with tempfile.TemporaryDirectory() as directory:
            result = VALIDATOR.validate_repository(Path(directory), required_paths=())
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "git_file_inventory_failed")


if __name__ == "__main__":
    unittest.main()
