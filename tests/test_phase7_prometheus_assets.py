from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import unittest

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMETHEUS_DIR = REPO_ROOT / "monitoring" / "prometheus"
MAPPING_FILE = PROMETHEUS_DIR / "fraudlens_metrics_mapping.yaml"
SAMPLE_EVENTS = PROMETHEUS_DIR / "sample-metric-events.jsonl"
EXPECTED_EXPOSITION = PROMETHEUS_DIR / "expected-fraudlens-metrics.prom"
RENDER_SCRIPT = PROMETHEUS_DIR / "render_fraudlens_metrics.py"


def _load_render_module():
    spec = importlib.util.spec_from_file_location("render_fraudlens_metrics", RENDER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {RENDER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase7PrometheusAssetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mapping = yaml.safe_load(MAPPING_FILE.read_text(encoding="utf-8"))
        cls.render_module = _load_render_module()

    def test_metric_mapping_uses_fraudlens_prefix_and_allowed_labels(self) -> None:
        self.assertEqual(self.mapping["prometheus_metric_prefix"], "fraudlens_")
        allowed_labels = set(self.mapping["labels"]["allowed"])
        for label in ["environment", "run_profile", "run_target", "workflow", "stage", "status"]:
            self.assertIn(label, allowed_labels)
        for metric in self.mapping["metrics"].values():
            self.assertTrue(metric["prometheus_name"].startswith("fraudlens_"))

    def test_sample_events_render_expected_prometheus_exposition(self) -> None:
        events = list(self.render_module.iter_events([SAMPLE_EVENTS]))
        rendered = self.render_module.render_events(events, self.mapping)
        expected = EXPECTED_EXPOSITION.read_text(encoding="utf-8")
        self.assertEqual(rendered, expected)

    def test_unknown_metric_is_skipped_and_counted(self) -> None:
        rendered = self.render_module.render_events(
            [
                {
                    "metric_name": "unexpected_metric",
                    "metric_value": 1,
                    "metric_type": "gauge",
                }
            ],
            self.mapping,
        )
        self.assertIn("fraudlens_metric_adapter_events_parsed_total 0", rendered)
        self.assertIn("fraudlens_metric_adapter_events_skipped_total 1", rendered)

    def test_dashboard_metric_sources_can_be_rendered(self) -> None:
        required = set()
        for path in (PROMETHEUS_DIR.parent / "grafana/dashboards").glob("*.json"):
            required.update(re.findall(r"fraudlens_(?:pipeline|service|runtime)_[a-z_]+", path.read_text(encoding="utf-8")))
        events = [{"metric_name": name.removeprefix("fraudlens_"), "metric_value": 1, "run_profile": "local"} for name in sorted(required)]
        rendered = self.render_module.render_events(events, self.mapping)
        for name in required:
            with self.subTest(metric=name):
                self.assertIn(name + "{", rendered)
        self.assertIn("fraudlens_metric_adapter_events_skipped_total 0", rendered)


if __name__ == "__main__":
    unittest.main()
