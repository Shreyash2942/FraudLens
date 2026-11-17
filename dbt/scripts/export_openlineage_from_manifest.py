from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRODUCER = "https://github.com/Shreyash2942/FraudLens"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"dbt manifest must be a JSON object: {path}")
    return payload


def node_layer(node: dict[str, Any]) -> str:
    tags = node.get("tags", [])
    if isinstance(tags, list):
        for layer in ("bronze", "silver", "gold", "kpi"):
            if layer in tags:
                return layer
    path = str(node.get("path", "")).lower()
    for layer in ("bronze", "silver", "gold", "kpi"):
        if f"{layer}/" in path or f"{layer}\\" in path:
            return layer
    return "unknown"


def relation_name(node: dict[str, Any]) -> str:
    database = str(node.get("database") or "").strip()
    schema = str(node.get("schema") or "").strip()
    alias = str(node.get("alias") or node.get("name") or "").strip()
    return ".".join(part for part in [database, schema, alias] if part) or str(node.get("unique_id", "unknown"))


def dataset_from_unique_id(unique_id: str, manifest: dict[str, Any], *, namespace: str) -> dict[str, Any]:
    nodes = manifest.get("nodes", {})
    sources = manifest.get("sources", {})
    node = nodes.get(unique_id) if isinstance(nodes, dict) else None
    source = sources.get(unique_id) if isinstance(sources, dict) else None
    payload = node if isinstance(node, dict) else source if isinstance(source, dict) else {}
    return {
        "namespace": namespace,
        "name": relation_name(payload) if payload else unique_id,
        "facets": {
            "dbt_node": {
                "_producer": DEFAULT_PRODUCER,
                "_schemaURL": "https://fraudlens.local/openlineage/facets/dbt-node-v1.json",
                "unique_id": unique_id,
                "resource_type": payload.get("resource_type", "unknown") if isinstance(payload, dict) else "unknown",
                "layer": node_layer(payload) if isinstance(payload, dict) else "unknown",
            }
        },
    }


def build_openlineage_event(
    *,
    node_id: str,
    node: dict[str, Any],
    manifest: dict[str, Any],
    namespace: str,
    run_id: str,
    batch_id: str,
    event_time: str,
) -> dict[str, Any]:
    depends_on = node.get("depends_on", {})
    upstream_ids = depends_on.get("nodes", []) if isinstance(depends_on, dict) else []
    inputs = [
        dataset_from_unique_id(str(upstream_id), manifest, namespace=namespace)
        for upstream_id in upstream_ids
        if str(upstream_id).startswith(("model.", "source."))
    ]
    output = {
        "namespace": namespace,
        "name": relation_name(node),
        "facets": {
            "dbt_node": {
                "_producer": DEFAULT_PRODUCER,
                "_schemaURL": "https://fraudlens.local/openlineage/facets/dbt-node-v1.json",
                "unique_id": node_id,
                "resource_type": node.get("resource_type", "model"),
                "materialized": (node.get("config", {}) or {}).get("materialized", "unknown")
                if isinstance(node.get("config", {}), dict)
                else "unknown",
                "layer": node_layer(node),
            }
        },
    }
    return {
        "event_type": "dbt_transformation_completed",
        "event_time_utc": event_time,
        "namespace": namespace,
        "job_name": f"dbt.{node_id}",
        "run_id": run_id,
        "batch_id": batch_id,
        "run_profile": namespace.rsplit(".", 1)[-1] if "." in namespace else "local",
        "status": "SUCCESS",
        "inputs": inputs,
        "outputs": [output],
        "openlineage_event": {
            "eventType": "COMPLETE",
            "eventTime": event_time,
            "producer": DEFAULT_PRODUCER,
            "schemaURL": "https://openlineage.io/spec/1-0-5/OpenLineage.json",
            "run": {
                "runId": str(uuid5(NAMESPACE_URL, json.dumps([namespace, f"dbt.{node_id}", run_id]))),
                "facets": {
                    "fraudlens_run": {
                        "_producer": DEFAULT_PRODUCER,
                        "_schemaURL": "https://fraudlens.local/openlineage/facets/fraudlens-run-v1.json",
                        "pipeline_run_id": run_id,
                        "batch_id": batch_id,
                    }
                },
            },
            "job": {
                "namespace": namespace,
                "name": f"dbt.{node_id}",
                "facets": {
                    "dbt_job": {
                        "_producer": DEFAULT_PRODUCER,
                        "_schemaURL": "https://fraudlens.local/openlineage/facets/dbt-job-v1.json",
                        "package_name": node.get("package_name", "fraudlens"),
                        "resource_type": node.get("resource_type", "model"),
                        "layer": node_layer(node),
                    }
                },
            },
            "inputs": inputs,
            "outputs": [output],
        },
    }


def iter_model_events(
    manifest: dict[str, Any],
    *,
    namespace: str,
    run_id: str,
    batch_id: str,
    event_time: str,
) -> list[dict[str, Any]]:
    nodes = manifest.get("nodes", {})
    if not isinstance(nodes, dict):
        return []
    events = []
    for node_id, node in sorted(nodes.items()):
        if not isinstance(node, dict) or node.get("resource_type") != "model":
            continue
        events.append(
            build_openlineage_event(
                node_id=str(node_id),
                node=node,
                manifest=manifest,
                namespace=namespace,
                run_id=run_id,
                batch_id=batch_id,
                event_time=event_time,
            )
        )
    return events


def write_events(events: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event) + "\n")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export dbt manifest dependencies as OpenLineage-compatible events.")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "dbt" / "target" / "manifest.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--namespace", default="fraudlens.orchestration.local")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--batch-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    events = iter_model_events(
        manifest,
        namespace=args.namespace,
        run_id=args.run_id,
        batch_id=args.batch_id,
        event_time=utc_now_iso(),
    )
    write_events(events, args.output)
    print(json.dumps({"event_count": len(events), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
