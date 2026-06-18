from __future__ import annotations

from pathlib import Path
import unittest

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
MONITORING_DIR = REPO_ROOT / "monitoring"
CONTRACT_FILE = MONITORING_DIR / "observability-contract.yaml"
METRICS_CATALOG = MONITORING_DIR / "metrics-catalog.md"
ALERT_THRESHOLDS = MONITORING_DIR / "alert-thresholds.md"


class Phase7MonitoringStrategyAssetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = yaml.safe_load(CONTRACT_FILE.read_text(encoding="utf-8"))
        cls.catalog_text = METRICS_CATALOG.read_text(encoding="utf-8")
        cls.threshold_text = ALERT_THRESHOLDS.read_text(encoding="utf-8")

    def test_observability_contract_declares_phase7_metric_strategy(self) -> None:
        metrics = self.contract["metrics"]
        self.assertEqual(metrics["prometheus_metric_prefix"], "fraudlens_")
        self.assertIn("pipeline_execution", metrics["metric_categories"])
        self.assertIn("data_governance", metrics["metric_categories"])
        self.assertIn("lineage_health", metrics["metric_categories"])
        self.assertIn("system_health", metrics["metric_categories"])
        self.assertIn("environment", metrics["required_labels"])
        self.assertIn("raw_exception_message", metrics["blocked_label_sources"])

    def test_canonical_metrics_cover_pipeline_system_and_lineage(self) -> None:
        metric_names = {
            metric["metric_name"]
            for metric in self.contract["metrics"]["canonical_metrics"]
        }
        required_metrics = {
            "pipeline_run_status",
            "pipeline_run_duration_seconds",
            "pipeline_stage_duration_seconds",
            "pipeline_failure_total",
            "pipeline_quality_gate_total",
            "pipeline_lineage_event_total",
            "pipeline_lineage_delivery_total",
            "service_health_status",
            "runtime_cpu_utilization_percent",
            "runtime_memory_utilization_percent",
        }
        self.assertTrue(required_metrics.issubset(metric_names))

    def test_metric_catalog_documents_label_standards(self) -> None:
        expected_tokens = [
            "Prometheus metric prefix: `fraudlens_`",
            "`pipeline_run_duration_seconds`",
            "`pipeline_stage_duration_seconds`",
            "`pipeline_lineage_event_total`",
            "`service_health_status`",
            "Blocked label sources",
        ]
        for token in expected_tokens:
            self.assertIn(token, self.catalog_text)

    def test_alert_thresholds_cover_pipeline_lineage_and_services(self) -> None:
        expected_tokens = [
            "latest run failed",
            "artifact completeness incomplete",
            "lineage delivery failed",
            "Airflow unavailable",
            "Marquez unavailable",
        ]
        for token in expected_tokens:
            self.assertIn(token, self.threshold_text)


if __name__ == "__main__":
    unittest.main()

