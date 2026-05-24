# Phase 5 Quality And Governance Standards

Issue: `#64`  
Parent milestone: `#56`

## Purpose

This standards compendium defines the quality and governance baseline for FraudLens Phase 5.

It aligns policy, implementation, and validation across:
- Bronze ingestion/staging interfaces
- Silver conformed transformation interfaces
- Gold serving and KPI interfaces

## Quality Standards

### Core test families

- `not_null` for mandatory keys and control fields
- `unique` for entity and grain keys
- `relationships` for governed foreign-key paths
- `accepted_values` for controlled lifecycle domains
- reconciliation and chronology singular tests for trust controls

### Severity model

- `quality_critical` for blocking control failures
- `quality_high` for high-impact but non-core-key controls
- `governance_critical` for metadata/governance compliance
- `contract_critical` for structural contract enforcement
- `audit_critical` for traceability/audit continuity
- `validation_critical` for integrated readiness controls

### Selector standards

Key selectors:
- `quality_critical_gate`
- `quality_high_gate`
- `failure_blocking_gate`
- `failure_diagnostic_gate`
- `phase5_readiness_bundle`

## Contract Standards

Contract-critical models must include:
- `meta.owner`
- `meta.steward`
- `meta.domain`
- `meta.criticality`
- `meta.contract_required_fields`
- `meta.contract_expected_types`
- optional `meta.contract_controlled_fields` when domains are constrained

Contract enforcement artifacts:
- `documents/phase-5-data-contract-requirements.md`
- `documents/phase-5-data-contract-enforcement-guide.md`

## Auditability And Traceability Standards

Canonical fields for critical outputs:
- `ingestion_batch_id`
- `source_file_name`
- `ingested_at_utc`
- `created_at_utc`
- `updated_at_utc`
- `source_system`
- `pipeline_run_id`
- `pipeline_processed_at_utc`
- `lineage_run_id`

Audit/trace references:
- `documents/phase-5-audit-traceability-guide.md`

## Governance Execution Standards

Validation entrypoints:
- `bash dbt/scripts/validate_structure.sh`
- `bash dbt/scripts/validate_docs.sh`

Automated policy checks:
- naming checks
- governance metadata checks
- contract checks and alignment
- failure policy coverage checks

## Readiness Standards

Readiness must include evidence artifacts and an explicit status decision:
- checklist
- command artifact JSON
- cross-layer evidence summary
- integrated controls matrix
- final readiness report

Reference:
- `documents/phase-5-governance-readiness-report.md`

