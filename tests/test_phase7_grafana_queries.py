from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / "monitoring" / "grafana" / "dashboards"
ALLOWED_PREFIXES = ("fraudlens_", "up")
BLOCKED_TOKENS = ("batch_202", "manual__", "run_id=", "batch_id=")


def _dashboard_queries(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    queries: list[str] = []
    for panel in payload["panels"]:
        for target in panel.get("targets", []):
            expr = target.get("expr")
            if expr:
                queries.append(expr)
    for item in payload["templating"]["list"]:
        query = item.get("query")
        if query:
            queries.append(query)
    return queries


class Phase7GrafanaPromqlTest(unittest.TestCase):
    def test_dashboard_queries_use_approved_metric_sources(self) -> None:
        for path in sorted(DASHBOARD_DIR.glob("*.json")):
            for query in _dashboard_queries(path):
                with self.subTest(path=path.name, query=query):
                    self.assertTrue(
                        any(prefix in query for prefix in ALLOWED_PREFIXES),
                        msg=f"Query does not reference an approved metric source: {query}",
                    )

    def test_dashboard_queries_do_not_hard_code_run_or_batch_ids(self) -> None:
        for path in sorted(DASHBOARD_DIR.glob("*.json")):
            for query in _dashboard_queries(path):
                with self.subTest(path=path.name, query=query):
                    for token in BLOCKED_TOKENS:
                        self.assertNotIn(token, query)

    def test_dashboards_include_expected_operational_metrics(self) -> None:
        all_queries = "\n".join(
            query
            for path in sorted(DASHBOARD_DIR.glob("*.json"))
            for query in _dashboard_queries(path)
        )
        expected_metrics = [
            "fraudlens_pipeline_run_status",
            "fraudlens_pipeline_stage_duration_seconds",
            "fraudlens_pipeline_failure_total",
            "fraudlens_pipeline_quality_gate_total",
            "fraudlens_service_health_status",
            "fraudlens_pipeline_lineage_event_total",
        ]
        for metric in expected_metrics:
            self.assertIn(metric, all_queries)


if __name__ == "__main__":
    unittest.main()

