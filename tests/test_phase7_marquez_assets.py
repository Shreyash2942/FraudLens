from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import urllib.error
from unittest.mock import patch
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARQUEZ_DIR = REPO_ROOT / "monitoring" / "marquez"
DELIVERY_HELPER = REPO_ROOT / "scripts" / "deliver_openlineage_to_marquez.py"
HEALTH_HELPER = REPO_ROOT / "scripts" / "check_marquez_health.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarquezAssetsTest(unittest.TestCase):
    def test_marquez_config_assets_exist(self) -> None:
        expected_files = [
            MARQUEZ_DIR / "README.md",
            MARQUEZ_DIR / "marquez.env.example",
            MARQUEZ_DIR / "lineage-visualization-checklist.md",
        ]
        for file_path in expected_files:
            with self.subTest(file_path=file_path):
                self.assertTrue(file_path.exists())

    def test_marquez_env_declares_required_endpoints(self) -> None:
        source = (MARQUEZ_DIR / "marquez.env.example").read_text(encoding="utf-8")
        for token in (
            "MARQUEZ_BASE_URL",
            "OPENLINEAGE_URL",
            "OPENLINEAGE_NAMESPACE",
            "OPENLINEAGE_PRODUCER",
            "MARQUEZ_HEALTH_PATH",
        ):
            self.assertIn(token, source)

    def test_delivery_helper_extracts_nested_openlineage_events(self) -> None:
        delivery = load_module(DELIVERY_HELPER, "deliver_openlineage_to_marquez")
        event = {
            "event_type": "pipeline_run_completed",
            "openlineage_event": {
                "eventType": "COMPLETE",
                "eventTime": "2026-06-20T00:00:00Z",
                "run": {"runId": "run-001"},
                "job": {"namespace": "fraudlens.orchestration.local", "name": "job"},
                "inputs": [],
                "outputs": [],
            },
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "lineage.jsonl"
            input_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            payload = delivery.deliver_events(
                input_path=input_path,
                url="http://localhost:5000",
                dry_run=True,
                timeout_seconds=1,
            )

        self.assertEqual(payload["event_count"], 1)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["responses"][0]["status"], "dry_run")
        self.assertEqual(payload["responses"][0]["job"], "job")

    def test_health_helper_normalizes_urls(self) -> None:
        health = load_module(HEALTH_HELPER, "check_marquez_health")
        self.assertEqual(
            health.normalize_url("http://localhost:3003/", "/api/v1/namespaces"),
            "http://localhost:3003/api/v1/namespaces",
        )

    def test_health_reports_timeout_and_http_failure(self) -> None:
        health = load_module(HEALTH_HELPER, "check_marquez_health_errors")
        for error, expected in ((TimeoutError("timed out"), "unreachable"),
                (urllib.error.HTTPError("http://localhost", 404, "missing", {}, None), "unhealthy")):
            with self.subTest(error=type(error).__name__), patch.object(health.urllib.request, "urlopen", side_effect=error):
                result = health.check_marquez_health(base_url="http://localhost", health_path="/api/v1/namespaces", timeout_seconds=1)
                self.assertEqual(result["status"], expected)

    def test_delivery_reports_timeout_without_losing_summary(self) -> None:
        delivery = load_module(DELIVERY_HELPER, "deliver_openlineage_timeout")
        event = {"eventType": "COMPLETE", "eventTime": "2026-06-20T00:00:00Z", "run": {}, "job": {}, "inputs": [], "outputs": []}
        with patch.object(delivery, "extract_openlineage_events", return_value=[event]), patch.object(delivery, "post_event", side_effect=TimeoutError("timed out")):
            result = delivery.deliver_events(input_path=Path("unused"), url="http://localhost/api/v1/lineage", dry_run=False, timeout_seconds=1)
        self.assertEqual(result["event_count"], 1)
        self.assertEqual(result["responses"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
