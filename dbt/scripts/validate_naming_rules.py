#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

LAYER_RULES: tuple[tuple[str, str], ...] = (
    ("models/bronze/", "stg_bronze__"),
    ("models/silver/", "slv__"),
    ("models/gold/facts/", "fact_"),
    ("models/gold/dimensions/", "dim_"),
    ("models/gold/kpi/", "kpi_"),
)


def _load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _expected_prefix_for_path(path: str) -> str | None:
    normalized = path.replace("\\", "/").lower()
    for root_path, prefix in LAYER_RULES:
        if normalized.startswith(root_path):
            return prefix
    return None


def _validate_model_naming(manifest: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0

    for node in manifest.get("nodes", {}).values():
        if node.get("resource_type") != "model":
            continue

        model_name = str(node.get("name", ""))
        original_file_path = str(node.get("original_file_path", "")).replace("\\", "/")
        expected_prefix = _expected_prefix_for_path(original_file_path)
        if expected_prefix is None:
            continue

        checked += 1

        if not model_name.startswith(expected_prefix):
            errors.append(
                f"{model_name}: invalid model prefix for {original_file_path}; expected prefix '{expected_prefix}'"
            )

        alias = str(node.get("alias", ""))
        if alias and alias != alias.upper():
            errors.append(f"{model_name}: alias must be uppercase; found '{alias}'")

        tags = set(node.get("tags", []))
        if "bronze" in original_file_path and "bronze" not in tags:
            errors.append(f"{model_name}: bronze path model must include 'bronze' tag")
        if "silver" in original_file_path and "silver" not in tags:
            errors.append(f"{model_name}: silver path model must include 'silver' tag")
        if "models/gold/" in original_file_path and "gold" not in tags:
            errors.append(f"{model_name}: gold path model must include 'gold' tag")

        for column_name in node.get("columns", {}).keys():
            if not SNAKE_CASE_PATTERN.match(str(column_name)):
                errors.append(
                    f"{model_name}: column '{column_name}' is not snake_case"
                )

    return errors, checked


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate FraudLens dbt naming rules for model, alias, and column conventions."
    )
    parser.add_argument(
        "--manifest",
        default="dbt/target/manifest.json",
        help="Path to dbt manifest.json (default: dbt/target/manifest.json)",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[naming] ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = _load_manifest(manifest_path)
    errors, checked = _validate_model_naming(manifest)
    if errors:
        print("[naming] validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"[naming] validation passed for {checked} dbt models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

