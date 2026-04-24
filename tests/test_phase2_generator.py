from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from synthetic_generator.blueprints import list_builtin_blueprints, load_blueprint
from synthetic_generator.contracts import DATASET_ORDER
from synthetic_generator.generate import main


class Phase2GeneratorSmokeTest(unittest.TestCase):
    def test_small_fast_generation_with_validation(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exit_code = main(
                [
                    "--output-dir",
                    tmp_dir,
                    "--days",
                    "30",
                    "--profile",
                    "small_fast",
                    "--seed",
                    "11",
                    "--validate",
                ]
            )
            self.assertEqual(exit_code, 0)

            runs_dir = Path(tmp_dir) / "batches"
            run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]

            manifest = json.loads((run_dir / "control" / "manifest.json").read_text(encoding="utf-8"))
            validation = json.loads((run_dir / "quality" / "validation_report.json").read_text(encoding="utf-8"))

            self.assertEqual(len(manifest["datasets"]), len(DATASET_ORDER))
            self.assertTrue(validation["passed"], validation.get("errors"))
            self.assertGreater(manifest["datasets"]["payment_instruction"]["row_count"], 0)
            self.assertGreater(manifest["datasets"]["fraud_alert"]["row_count"], 0)
            self.assertIn("calendar_day", manifest["datasets"])
            self.assertIn("region", manifest["datasets"])
            self.assertIn("analyst_team", manifest["datasets"])
            self.assertEqual(manifest["validation"]["status"], "completed")
            self.assertEqual(manifest["mode"], "mixed")
            self.assertIn("org_geography_summary", manifest)
            self.assertIn("org_structure_consistency", validation["checks"])

    def test_list_builtin_blueprints_and_load_one(self) -> None:
        names = list_builtin_blueprints()
        self.assertIn("hybrid_fraud_ops_demo", names)
        blueprint = load_blueprint("hybrid_fraud_ops_demo")
        self.assertEqual(blueprint.name, "hybrid_fraud_ops_demo")
        self.assertGreater(blueprint.lifecycle_counts["alert_count"], 0)

    def test_blueprint_mode_requires_blueprint(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--mode", "blueprint"])

    def test_invalid_blueprint_file_fails_to_load(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "invalid.yaml"
            path.write_text("metadata:\n  name: broken\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_blueprint(str(path))

    def test_blueprint_generation_with_validation(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exit_code = main(
                [
                    "--mode",
                    "blueprint",
                    "--blueprint",
                    "false_positive_review_showcase",
                    "--output-dir",
                    tmp_dir,
                    "--profile",
                    "small_fast",
                    "--seed",
                    "17",
                    "--validate",
                ]
            )
            self.assertEqual(exit_code, 0)

            runs_dir = Path(tmp_dir) / "batches"
            run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]

            manifest = json.loads((run_dir / "control" / "manifest.json").read_text(encoding="utf-8"))
            validation = json.loads((run_dir / "quality" / "validation_report.json").read_text(encoding="utf-8"))
            batch_control = json.loads((run_dir / "control" / "batch_control.json").read_text(encoding="utf-8"))

            self.assertEqual(manifest["mode"], "blueprint")
            self.assertEqual(manifest["blueprint"]["name"], "false_positive_review_showcase")
            self.assertIn("scenario_summary", manifest)
            self.assertIn("lifecycle_summary", manifest)
            self.assertIn("org_geography_summary", manifest)
            self.assertEqual(batch_control["mode"], "blueprint")
            self.assertEqual(batch_control["blueprint"]["name"], "false_positive_review_showcase")
            self.assertIn("control_summary", batch_control)
            self.assertTrue(validation["checks"]["blueprint_compliance"]["passed"], validation.get("errors"))
            false_positive_count = manifest["scenario_summary"]["counts_by_scenario"]["false_positive"]
            suspicious_device_count = manifest["scenario_summary"]["counts_by_scenario"]["suspicious_new_device"]
            self.assertGreater(false_positive_count, suspicious_device_count)


if __name__ == "__main__":
    unittest.main()
