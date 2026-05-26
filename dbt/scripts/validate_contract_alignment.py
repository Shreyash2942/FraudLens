#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


INTERFACE_REQUIREMENTS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "stg_bronze__payment_instruction",
        "slv__payment_instruction",
        (
            "payment_instruction_id",
            "instruction_status",
            "debtor_account_id",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "stg_bronze__payment_transaction",
        "slv__payment_transaction",
        (
            "payment_transaction_id",
            "payment_instruction_id",
            "transaction_status",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "stg_bronze__risk_signal",
        "slv__risk_signal",
        (
            "risk_signal_id",
            "payment_instruction_id",
            "risk_level",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "stg_bronze__fraud_alert",
        "slv__fraud_alert",
        (
            "fraud_alert_id",
            "risk_signal_id",
            "alert_status",
            "alert_severity",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "stg_bronze__fraud_case",
        "slv__fraud_case",
        (
            "fraud_case_id",
            "primary_alert_id",
            "case_status",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "slv__payment_instruction",
        "fact_payment_events",
        (
            "payment_instruction_id",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "slv__payment_transaction",
        "fact_transactions",
        (
            "payment_transaction_id",
            "payment_instruction_id",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "fact_daily_fraud_metrics",
        "kpi_daily_fraud_operations",
        (
            "metric_date",
            "total_transactions",
            "total_fraud_alerts",
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
    (
        "fact_payment_events",
        "kpi_portfolio_risk_snapshot",
        (
            "ingestion_batch_id",
            "source_file_name",
            "ingested_at_utc",
            "lineage_run_id",
        ),
    ),
)


def _load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _models_by_name(manifest: dict) -> dict[str, dict]:
    models: dict[str, dict] = {}
    for node in manifest.get("nodes", {}).values():
        if node.get("resource_type") == "model":
            model_name = node.get("name")
            if model_name:
                models[model_name] = node
    return models


def _contract_required_fields(node: dict) -> set[str]:
    required_fields = node.get("meta", {}).get("contract_required_fields", [])
    if not isinstance(required_fields, list):
        return set()
    return {str(column).lower() for column in required_fields}


def _meta_expected_types(node: dict) -> dict[str, str]:
    expected = node.get("meta", {}).get("contract_expected_types", {})
    if not isinstance(expected, dict):
        return {}
    return {str(key).lower(): str(value).lower() for key, value in expected.items()}


def _validate_alignment(manifest: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    models = _models_by_name(manifest)
    checks = 0

    for upstream_name, downstream_name, fields in INTERFACE_REQUIREMENTS:
        checks += 1
        upstream = models.get(upstream_name)
        downstream = models.get(downstream_name)

        if upstream is None:
            errors.append(f"missing upstream model in manifest: {upstream_name}")
            continue
        if downstream is None:
            errors.append(f"missing downstream model in manifest: {downstream_name}")
            continue

        upstream_contract_fields = _contract_required_fields(upstream)
        downstream_contract_fields = _contract_required_fields(downstream)
        upstream_expected_types = _meta_expected_types(upstream)
        downstream_expected_types = _meta_expected_types(downstream)

        if not upstream_contract_fields:
            errors.append(f"{upstream_name}: missing or invalid meta.contract_required_fields")
            continue
        if not downstream_contract_fields:
            errors.append(f"{downstream_name}: missing or invalid meta.contract_required_fields")
            continue

        for field in fields:
            field_lower = field.lower()
            if field_lower not in upstream_contract_fields:
                errors.append(
                    f"{upstream_name} -> {downstream_name}: required interface field missing upstream contract_required_fields: {field}"
                )
            if field_lower not in downstream_contract_fields:
                errors.append(
                    f"{upstream_name} -> {downstream_name}: required interface field missing downstream contract_required_fields: {field}"
                )

            upstream_type = upstream_expected_types.get(field_lower)
            downstream_type = downstream_expected_types.get(field_lower)
            if upstream_type and downstream_type and upstream_type != downstream_type:
                errors.append(
                    f"{upstream_name} -> {downstream_name}: contract_expected_types mismatch for {field} ({upstream_type} vs {downstream_type})"
                )

    return errors, checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate cross-layer contract interface alignment for critical FraudLens dbt models."
    )
    parser.add_argument(
        "--manifest",
        default="dbt/target/manifest.json",
        help="Path to dbt manifest.json (default: dbt/target/manifest.json)",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[contract-alignment] ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = _load_manifest(manifest_path)
    errors, checks = _validate_alignment(manifest)
    if errors:
        print("[contract-alignment] validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"[contract-alignment] validation passed across {checks} interface checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
