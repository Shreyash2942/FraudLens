from __future__ import annotations

import json
from pathlib import Path
import unittest

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAFANA_DIR = REPO_ROOT / "monitoring" / "grafana"
DASHBOARD_DIR = GRAFANA_DIR / "dashboards"
DATASOURCE_FILE = GRAFANA_DIR / "provisioning" / "datasources" / "prometheus.yaml"


class Phase7GrafanaDashboardAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dashboard_paths = sorted(DASHBOARD_DIR.glob("*.json"))

    def test_expected_dashboard_files_exist(self) -> None:
        names = {path.name for path in self.dashboard_paths}
        expected = {
            "fraudlens-pipeline-overview.json",
            "fraudlens-pipeline-performance.json",
            "fraudlens-failure-quality.json",
            "fraudlens-system-health.json",
            "fraudlens-lineage-health.json",
        }
        self.assertEqual(names, expected)

    def test_dashboard_json_assets_have_required_shape(self) -> None:
        for path in self.dashboard_paths:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("uid", payload)
                self.assertIn("title", payload)
                self.assertIn("panels", payload)
                self.assertGreaterEqual(len(payload["panels"]), 1)
                self.assertEqual(payload["schemaVersion"], 39)

    def test_dashboards_reference_prometheus_datasource(self) -> None:
        for path in self.dashboard_paths:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                for panel in payload["panels"]:
                    self.assertEqual(panel["datasource"]["uid"], "prometheus")
                for item in payload["templating"]["list"]:
                    self.assertEqual(item["datasource"]["uid"], "prometheus")

    def test_datasource_provisioning_uses_stable_uid(self) -> None:
        payload = yaml.safe_load(DATASOURCE_FILE.read_text(encoding="utf-8"))
        datasource = payload["datasources"][0]
        self.assertEqual(datasource["name"], "Prometheus")
        self.assertEqual(datasource["uid"], "prometheus")
        self.assertEqual(datasource["type"], "prometheus")


if __name__ == "__main__":
    unittest.main()

