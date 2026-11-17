from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = REPO_ROOT / "documents"
MONITORING_README = REPO_ROOT / "monitoring" / "README.md"


class Phase7DocumentationCompleteTest(unittest.TestCase):
    def test_phase7_operator_guides_exist(self) -> None:
        expected_docs = [
            "observability-lineage-setup-guide.md",
            "observability-metrics-dashboards-guide.md",
            "lineage-interpretation-guide.md",
            "observability-lineage-troubleshooting-guide.md",
            "phase-7-observability-lineage.md",
            "observability-lineage-coverage-readiness-report.md",
        ]
        for doc_name in expected_docs:
            with self.subTest(doc_name=doc_name):
                self.assertTrue((DOCUMENTS / doc_name).exists())

    def test_phase7_overview_links_core_guides(self) -> None:
        source = (DOCUMENTS / "phase-7-observability-lineage.md").read_text(encoding="utf-8")
        expected_links = [
            "documents/observability-lineage-setup-guide.md",
            "documents/observability-metrics-dashboards-guide.md",
            "documents/openlineage-airflow-dbt-runbook.md",
            "documents/marquez-lineage-visualization-runbook.md",
            "documents/observability-lineage-troubleshooting-guide.md",
        ]
        for link in expected_links:
            with self.subTest(link=link):
                self.assertIn(link, source)

    def test_monitoring_readme_links_phase7_guides(self) -> None:
        source = MONITORING_README.read_text(encoding="utf-8")
        for token in (
            "Marquez Quick Start",
            "OpenLineage documentation",
            "Marquez documentation",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
