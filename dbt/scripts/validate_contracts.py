#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_META_KEYS = (
    "owner",
    "steward",
    "criticality",
    "contract_required_fields",
    "contract_expected_types",
)


def _load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _model_nodes(manifest: dict) -> dict[str, dict]:
    nodes = manifest.get("nodes", {})
    return {
        unique_id: node
        for unique_id, node in nodes.items()
        if node.get("resource_type") == "model"
    }


def _accepted_values_index(manifest: dict, model_name_by_unique_id: dict[str, str]) -> dict[tuple[str, str], set[str]]:
    accepted_values: dict[tuple[str, str], set[str]] = {}
    for test_node in manifest.get("nodes", {}).values():
        if test_node.get("resource_type") != "test":
            continue

        test_metadata = test_node.get("test_metadata", {})
        if test_metadata.get("name") != "accepted_values":
            continue

        kwargs = test_metadata.get("kwargs", {})
        column_name = kwargs.get("column_name")
        values = kwargs.get("values", [])
        if not column_name:
            continue

        normalized_values = {str(value).upper() for value in values}
        for dependency in test_node.get("depends_on", {}).get("nodes", []):
            model_name = model_name_by_unique_id.get(dependency)
            if not model_name:
                continue
            accepted_values[(model_name, str(column_name).lower())] = normalized_values
    return accepted_values


def _validate_contract_critical_models(manifest: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    model_nodes = _model_nodes(manifest)
    model_name_by_unique_id = {unique_id: node.get("name", "") for unique_id, node in model_nodes.items()}
    accepted_values_index = _accepted_values_index(manifest, model_name_by_unique_id)

    checked = 0
    for node in model_nodes.values():
        tags = set(node.get("tags", []))
        if "contract_critical" not in tags:
            continue

        checked += 1
        model_name = node.get("name", "<unknown_model>")
        columns = {name.lower() for name in node.get("columns", {}).keys()}
        meta = node.get("meta", {})

        missing_meta_keys = [key for key in REQUIRED_META_KEYS if key not in meta]
        if missing_meta_keys:
            errors.append(
                f"{model_name}: missing required contract meta keys: {', '.join(missing_meta_keys)}"
            )
            continue

        required_fields = meta.get("contract_required_fields")
        if not isinstance(required_fields, list) or not required_fields:
            errors.append(f"{model_name}: contract_required_fields must be a non-empty list")
            continue

        expected_types = meta.get("contract_expected_types")
        if not isinstance(expected_types, dict) or not expected_types:
            errors.append(f"{model_name}: contract_expected_types must be a non-empty object")
            continue

        missing_required_columns = [
            field for field in required_fields if str(field).lower() not in columns
        ]
        if missing_required_columns:
            errors.append(
                f"{model_name}: required fields missing in model columns: {', '.join(map(str, missing_required_columns))}"
            )

        for field_name in expected_types.keys():
            if str(field_name).lower() not in columns:
                errors.append(
                    f"{model_name}: contract_expected_types references missing column '{field_name}'"
                )

        controlled_fields = meta.get("contract_controlled_fields", {})
        if controlled_fields and not isinstance(controlled_fields, dict):
            errors.append(f"{model_name}: contract_controlled_fields must be an object when present")
            continue

        for controlled_field, controlled_values in controlled_fields.items():
            controlled_field_lower = str(controlled_field).lower()
            if controlled_field_lower not in columns:
                errors.append(
                    f"{model_name}: controlled field '{controlled_field}' is missing from model columns"
                )
                continue

            if not isinstance(controlled_values, list) or not controlled_values:
                errors.append(
                    f"{model_name}: controlled field '{controlled_field}' must define a non-empty accepted value list"
                )
                continue

            declared_values = {str(value).upper() for value in controlled_values}
            tested_values = accepted_values_index.get((model_name, controlled_field_lower))
            if not tested_values:
                errors.append(
                    f"{model_name}: controlled field '{controlled_field}' has no accepted_values test"
                )
                continue

            if declared_values != tested_values:
                errors.append(
                    f"{model_name}: controlled field '{controlled_field}' contract values do not match accepted_values test"
                )

    return errors, checked


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate contract metadata and controlled-field enforcement for contract-critical dbt models."
    )
    parser.add_argument(
        "--manifest",
        default="dbt/target/manifest.json",
        help="Path to dbt manifest.json (default: dbt/target/manifest.json)",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[contract] ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = _load_manifest(manifest_path)
    errors, checked = _validate_contract_critical_models(manifest)
    if errors:
        print("[contract] validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"[contract] validation passed for {checked} contract-critical models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

