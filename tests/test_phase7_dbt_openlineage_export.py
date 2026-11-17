from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from uuid import UUID
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTER_PATH = REPO_ROOT / "dbt" / "scripts" / "export_openlineage_from_manifest.py"


def load_exporter_module():
    spec = importlib.util.spec_from_file_location("export_openlineage_from_manifest", EXPORTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load exporter module from {EXPORTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DbtOpenLineageExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exporter = load_exporter_module()

    def test_manifest_dependencies_render_openlineage_events(self) -> None:
        manifest = {
            "sources": {
                "source.fraudlens.bronze.payment_transaction": {
                    "resource_type": "source",
                    "database": "fraudlens",
                    "schema": "bronze",
                    "name": "payment_transaction",
                }
            },
            "nodes": {
                "model.fraudlens.slv__payment_transaction": {
                    "resource_type": "model",
                    "package_name": "fraudlens",
                    "database": "fraudlens",
                    "schema": "silver",
                    "alias": "slv__payment_transaction",
                    "path": "silver/slv__payment_transaction.sql",
                    "tags": ["silver"],
                    "config": {"materialized": "view"},
                    "depends_on": {
                        "nodes": ["source.fraudlens.bronze.payment_transaction"],
                    },
                }
            },
        }

        events = self.exporter.iter_model_events(
            manifest,
            namespace="fraudlens.orchestration.local",
            run_id="dbt-run-001",
            batch_id="batch_001",
            event_time="2026-06-20T00:00:00Z",
        )

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["event_type"], "dbt_transformation_completed")
        self.assertEqual(event["openlineage_event"]["eventType"], "COMPLETE")
        self.assertEqual(event["openlineage_event"]["job"]["name"], "dbt.model.fraudlens.slv__payment_transaction")
        self.assertEqual(event["openlineage_event"]["inputs"][0]["name"], "fraudlens.bronze.payment_transaction")
        self.assertEqual(event["openlineage_event"]["outputs"][0]["name"], "fraudlens.silver.slv__payment_transaction")
        self.assertEqual(event["openlineage_event"]["job"]["facets"]["dbt_job"]["layer"], "silver")
        self.assertEqual(UUID(event["openlineage_event"]["run"]["runId"]).version, 5)
        self.assertEqual(event["openlineage_event"]["run"]["facets"]["fraudlens_run"]["pipeline_run_id"], "dbt-run-001")

        manifest["nodes"]["model.fraudlens.another_model"] = dict(manifest["nodes"]["model.fraudlens.slv__payment_transaction"])
        repeated = self.exporter.iter_model_events(manifest, namespace="fraudlens.orchestration.local",
            run_id="dbt-run-001", batch_id="batch_001", event_time="2026-06-20T00:00:00Z")
        run_ids = [item["openlineage_event"]["run"]["runId"] for item in repeated]
        self.assertEqual(len(set(run_ids)), 2)
        self.assertIn(event["openlineage_event"]["run"]["runId"], run_ids)

    def test_write_events_outputs_jsonl(self) -> None:
        event = {
            "event_type": "dbt_transformation_completed",
            "openlineage_event": {"eventType": "COMPLETE"},
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "lineage" / "dbt_events.jsonl"
            self.exporter.write_events([event], output_path)
            written = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(written, [event])


if __name__ == "__main__":
    unittest.main()
