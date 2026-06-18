from __future__ import annotations

from pathlib import Path
import unittest

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRAPE_CONFIG = REPO_ROOT / "monitoring" / "prometheus" / "prometheus.yml"


class Phase7PrometheusScrapeConfigTest(unittest.TestCase):
    def test_scrape_config_includes_required_jobs(self) -> None:
        config = yaml.safe_load(SCRAPE_CONFIG.read_text(encoding="utf-8"))
        job_names = {job["job_name"] for job in config["scrape_configs"]}
        expected_jobs = {
            "fraudlens_metrics_exporter",
            "prometheus",
            "airflow",
            "grafana",
            "marquez",
            "mongodb",
            "spark_hive_runtime",
        }
        self.assertTrue(expected_jobs.issubset(job_names))

    def test_scrape_targets_include_stable_service_labels(self) -> None:
        config = yaml.safe_load(SCRAPE_CONFIG.read_text(encoding="utf-8"))
        for job in config["scrape_configs"]:
            for static_config in job["static_configs"]:
                labels = static_config.get("labels", {})
                self.assertEqual(labels.get("environment"), "local")
                self.assertIn("service_name", labels)


if __name__ == "__main__":
    unittest.main()

