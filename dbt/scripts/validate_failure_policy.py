#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _selector_names_from_yaml_text(selectors_yaml_text: str) -> set[str]:
    names: set[str] = set()
    pattern = re.compile(r"^\s*-\s+name:\s*([a-zA-Z0-9_]+)\s*$")
    for line in selectors_yaml_text.splitlines():
        match = pattern.match(line)
        if match:
            names.add(match.group(1))
    return names


def _test_tag_counts(manifest: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for node in manifest.get("nodes", {}).values():
        if node.get("resource_type") != "test":
            continue
        for tag in node.get("tags", []):
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def _validate_policy(policy: dict, selectors_yaml_text: str, manifest: dict) -> list[str]:
    errors: list[str] = []

    selectors = _selector_names_from_yaml_text(selectors_yaml_text)
    for selector_name in policy.get("required_selectors", []):
        if selector_name not in selectors:
            errors.append(f"required selector missing: {selector_name}")

    tag_counts = _test_tag_counts(manifest)

    for tag in policy.get("required_blocking_tags", []):
        if tag_counts.get(tag, 0) <= 0:
            errors.append(f"blocking tag has zero tests: {tag}")

    for tag in policy.get("required_diagnostic_tags", []):
        if tag_counts.get(tag, 0) <= 0:
            errors.append(f"diagnostic tag has zero tests: {tag}")

    for tag, minimum_count in policy.get("minimum_test_count_by_tag", {}).items():
        actual_count = tag_counts.get(tag, 0)
        if actual_count < int(minimum_count):
            errors.append(
                f"tag '{tag}' has {actual_count} tests, below required minimum {minimum_count}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate fail-fast policy selectors and test-tag coverage expectations."
    )
    parser.add_argument(
        "--manifest",
        default="dbt/target/manifest.json",
        help="Path to dbt manifest.json",
    )
    parser.add_argument(
        "--selectors",
        default="dbt/selectors.yml",
        help="Path to selectors.yml",
    )
    parser.add_argument(
        "--policy",
        default="dbt/tests/validation/failure_policy_matrix.json",
        help="Path to failure policy fixture JSON",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    selectors_path = Path(args.selectors)
    policy_path = Path(args.policy)

    missing = [
        str(path)
        for path in (manifest_path, selectors_path, policy_path)
        if not path.exists()
    ]
    if missing:
        print("[failure-policy] ERROR: required files missing:")
        for path in missing:
            print(f"  - {path}")
        return 2

    manifest = _load_json(manifest_path)
    policy = _load_json(policy_path)
    selectors_yaml_text = selectors_path.read_text(encoding="utf-8")

    errors = _validate_policy(policy, selectors_yaml_text, manifest)
    if errors:
        print("[failure-policy] validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("[failure-policy] validation passed for selector coverage and tag policy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
