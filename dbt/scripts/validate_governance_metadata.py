#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CRITICAL_TAGS = {
    "quality_critical",
    "contract_critical",
    "governance_critical",
    "tier_1_critical",
}

REQUIRED_META_FIELDS = ("owner", "steward", "domain", "criticality")
REQUIRED_AUDIT_COLUMNS = (
    "ingestion_batch_id",
    "source_file_name",
    "ingested_at_utc",
    "lineage_run_id",
)


def _load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_critical_model(node: dict) -> bool:
    tags = set(node.get("tags", []))
    return bool(CRITICAL_TAGS.intersection(tags))


def _validate_governance_metadata(manifest: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0

    for node in manifest.get("nodes", {}).values():
        if node.get("resource_type") != "model":
            continue
        if not _is_critical_model(node):
            continue

        checked += 1
        model_name = str(node.get("name", "<unknown_model>"))
        meta = node.get("meta", {})
        missing_meta = [field for field in REQUIRED_META_FIELDS if not meta.get(field)]
        if missing_meta:
            errors.append(
                f"{model_name}: missing governance meta fields: {', '.join(missing_meta)}"
            )

        columns = {column.lower() for column in node.get("columns", {}).keys()}
        missing_audit = [column for column in REQUIRED_AUDIT_COLUMNS if column not in columns]
        if missing_audit:
            errors.append(
                f"{model_name}: missing required audit columns: {', '.join(missing_audit)}"
            )

    return errors, checked


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate governance metadata and auditability standards for critical dbt models."
    )
    parser.add_argument(
        "--manifest",
        default="dbt/target/manifest.json",
        help="Path to dbt manifest.json (default: dbt/target/manifest.json)",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[governance] ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = _load_manifest(manifest_path)
    errors, checked = _validate_governance_metadata(manifest)
    if errors:
        print("[governance] validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"[governance] validation passed for {checked} critical models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

