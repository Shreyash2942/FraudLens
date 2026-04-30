from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from synthetic_generator.blueprints import list_builtin_blueprints, load_blueprint
from synthetic_generator.contracts import DATASET_ORDER
from synthetic_generator.generate import main
from synthetic_generator.storage import upload_run_to_minio


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


class _FakeMinio:
    init_calls: list[dict[str, object]] = []
    uploaded: list[tuple[str, str, str]] = []

    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool) -> None:
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        _FakeMinio.init_calls.append(
            {
                "endpoint": endpoint,
                "access_key": access_key,
                "secret_key": secret_key,
                "secure": secure,
            }
        )

    def bucket_exists(self, _bucket: str) -> bool:
        return False

    def make_bucket(self, _bucket: str) -> None:
        return None

    def fput_object(self, bucket: str, object_name: str, file_path: str) -> None:
        _FakeMinio.uploaded.append((bucket, object_name, file_path))


class MinioConfigCompatibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        _FakeMinio.init_calls.clear()
        _FakeMinio.uploaded.clear()

    def test_upload_uses_datalab_aliases(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            run_dir = Path(tmp_dir)
            artifact = run_dir / "control" / "manifest.json"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("{}", encoding="utf-8")

            env = {
                "DATALAB_MINIO_ENDPOINT_OUTSIDE": "http://localhost:9009",
                "DATALAB_MINIO_ACCESS_KEY": "minio_admin",
                "DATALAB_MINIO_SECRET_KEY": "minioadmin",
                "DATALAB_MINIO_BUCKET": "datalab",
            }
            with patch.dict(os.environ, env, clear=True), patch("minio.Minio", _FakeMinio):
                report = upload_run_to_minio(run_dir, "synthetic_demo_seed42")

            self.assertEqual(report["status"], "uploaded")
            self.assertEqual(report["bucket"], "datalab")
            self.assertEqual(report["prefix"], "fraudlens/synthetic_data/batches/synthetic_demo_seed42")
            self.assertEqual(report["file_count"], 1)
            self.assertEqual(_FakeMinio.init_calls[-1]["endpoint"], "localhost:9009")
            self.assertEqual(_FakeMinio.init_calls[-1]["access_key"], "minio_admin")
            self.assertTrue(_FakeMinio.uploaded[-1][1].endswith("governance/control/manifest.json"))

    def test_primary_minio_vars_override_datalab_aliases(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            run_dir = Path(tmp_dir)
            artifact = run_dir / "landing" / "csv" / "party.csv"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("party_id\nP-1\n", encoding="utf-8")

            env = {
                "MINIO_ENDPOINT": "http://localhost:19000",
                "MINIO_ACCESS_KEY": "fraudlens_user",
                "MINIO_SECRET_KEY": "fraudlens_secret",
                "DATALAB_MINIO_ENDPOINT_OUTSIDE": "http://localhost:9009",
                "DATALAB_MINIO_ACCESS_KEY": "minio_admin",
                "DATALAB_MINIO_SECRET_KEY": "minioadmin",
            }
            with patch.dict(os.environ, env, clear=True), patch("minio.Minio", _FakeMinio):
                report = upload_run_to_minio(run_dir, "synthetic_demo_seed17")

            self.assertEqual(report["status"], "uploaded")
            self.assertEqual(_FakeMinio.init_calls[-1]["endpoint"], "localhost:19000")
            self.assertEqual(_FakeMinio.init_calls[-1]["access_key"], "fraudlens_user")
            self.assertTrue(_FakeMinio.uploaded[-1][1].endswith("raw_zone/csv/party.csv"))

    def test_missing_minio_keys_still_reports_bucket(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            report = upload_run_to_minio(Path(tmp_dir), "synthetic_demo_seed99")
        self.assertEqual(report["status"], "skipped")
        self.assertEqual(report["reason"], "missing_minio_configuration")
        self.assertEqual(report["bucket"], "fraudlensdata")

    def test_generator_loads_minio_config_from_dotenv(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            output_dir = workspace / "data"
            (workspace / ".env").write_text(
                "\n".join(
                    [
                        "DATALAB_MINIO_ENDPOINT=http://localhost:9004",
                        "DATALAB_MINIO_ACCESS_KEY=minio_admin",
                        "DATALAB_MINIO_SECRET_KEY=minioadmin",
                        "DATALAB_MINIO_BUCKET=fraudlensdata",
                    ]
                ),
                encoding="utf-8",
            )
            original_cwd = Path.cwd()
            try:
                os.chdir(workspace)
                with patch.dict(os.environ, {}, clear=True), patch("minio.Minio", _FakeMinio):
                    exit_code = main(
                        [
                            "--output-dir",
                            str(output_dir),
                            "--days",
                            "7",
                            "--profile",
                            "small_fast",
                            "--seed",
                            "23",
                            "--upload-minio",
                        ]
                    )
            finally:
                os.chdir(original_cwd)

            self.assertEqual(exit_code, 0)
            self.assertEqual(_FakeMinio.init_calls[-1]["endpoint"], "localhost:9004")
            self.assertEqual(_FakeMinio.init_calls[-1]["access_key"], "minio_admin")
            self.assertTrue(any(bucket == "fraudlensdata" for bucket, _, _ in _FakeMinio.uploaded))

    def test_generator_loads_runtime_yaml_config(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            output_dir = workspace / "data"
            config_dir = workspace / "synthetic_generator"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "runtime_config.yaml").write_text(
                "\n".join(
                    [
                        "minio:",
                        "  endpoint: http://localhost:9011",
                        "  access_key: runtime_user",
                        "  secret_key: runtime_secret",
                        "  bucket: runtime-bucket",
                        "  prefix_root: runtime/prefix",
                    ]
                ),
                encoding="utf-8",
            )
            original_cwd = Path.cwd()
            try:
                os.chdir(workspace)
                with patch.dict(os.environ, {}, clear=True), patch("minio.Minio", _FakeMinio):
                    exit_code = main(
                        [
                            "--output-dir",
                            str(output_dir),
                            "--days",
                            "7",
                            "--profile",
                            "small_fast",
                            "--seed",
                            "31",
                            "--upload-minio",
                        ]
                    )
            finally:
                os.chdir(original_cwd)

            self.assertEqual(exit_code, 0)
            self.assertEqual(_FakeMinio.init_calls[-1]["endpoint"], "localhost:9011")
            self.assertEqual(_FakeMinio.init_calls[-1]["access_key"], "runtime_user")
            self.assertTrue(any(bucket == "runtime-bucket" for bucket, _, _ in _FakeMinio.uploaded))
            self.assertTrue(any("runtime/prefix" in object_name for _, object_name, _ in _FakeMinio.uploaded))


if __name__ == "__main__":
    unittest.main()
