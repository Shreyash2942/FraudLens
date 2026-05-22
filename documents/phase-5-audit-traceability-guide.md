# Phase 5 Auditability And Traceability Guide

## Purpose

This guide documents the Phase 5 auditability and traceability controls implemented for FraudLens.

The controls are designed to support:
- transparent lineage from Bronze to Silver to Gold
- SOX-oriented operational traceability
- reproducible pipeline attribution for reporting outputs

## Canonical Audit Columns

Critical models standardize the following canonical fields:

- `ingestion_batch_id`
- `source_file_name`
- `ingested_at_utc`
- `created_at_utc`
- `updated_at_utc`
- `source_system`
- `pipeline_run_id`
- `pipeline_processed_at_utc`
- `lineage_run_id`

## Implementation Summary

### Bronze

- `fraudlens_pipeline_audit_projection()` now emits canonical trace fields for staged sources.
- `source_system` defaults to `FRAUDLENS_SOURCE_SYSTEM` environment variable and falls back to `synthetic_generator`.
- `pipeline_run_id` is aligned to dbt invocation context.

### Silver

Critical lifecycle models now expose canonical audit fields with business-event-aware mappings:

- `slv__payment_instruction`
- `slv__payment_transaction`
- `slv__risk_signal`
- `slv__fraud_alert`
- `slv__fraud_case`
- `slv__decision_record`
- `slv__case_disposition`

### Gold And KPI

Canonical audit fields are propagated and coalesced in:

- `fact_transactions`
- `fact_fraud_alerts`
- `fact_payment_events`
- `fact_daily_fraud_metrics`
- `kpi_daily_fraud_operations`
- `kpi_portfolio_risk_snapshot`

## Traceability Macros

`dbt/macros/audit.sql` now provides:

- `fraudlens_required_audit_columns()`
- `fraudlens_source_system_name()`
- `fraudlens_pipeline_run_id()`
- `fraudlens_trace_audit_projection(...)`
- `fraudlens_pipeline_audit_projection(...)`

These macros standardize lineage and run attribution behavior across layers.

## Validation Coverage

### Cross-Layer Audit Presence

- `dbt/tests/gold/test_governance_required_audit_columns.sql`
- `dbt/tests/validation/test_audit_trace_lineage_continuity.sql`

### Lifecycle Chronology And Handoff

- `dbt/tests/validation/test_lifecycle_traceability_chronology.sql`

These tests validate:
- canonical field non-nullness on critical models
- lineage continuity between key upstream/downstream model pairs
- lifecycle chronology across alert/case/decision/disposition entities

## Operational Usage

For any record in Gold/KPI outputs, operators can answer:

- **where did it come from?**
  - `source_system`, `source_file_name`
- **which batch/run produced it?**
  - `ingestion_batch_id`, `pipeline_run_id`, `lineage_run_id`
- **when was it created/updated in pipeline context?**
  - `created_at_utc`, `updated_at_utc`, `pipeline_processed_at_utc`

## Local Validation Commands

```bash
bash dbt/scripts/validate_structure.sh
bash dbt/scripts/validate_docs.sh
```

