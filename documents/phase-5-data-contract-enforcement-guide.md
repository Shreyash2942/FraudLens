# Phase 5 Data Contract Enforcement Guide

## Purpose

This guide defines how FraudLens enforces data contracts for critical datasets in Phase 5.

Contract enforcement covers:
- required fields
- expected semantic data types
- controlled-value fields
- cross-layer interface consistency
- ownership and stewardship metadata

## Scope

The contract gate applies to models tagged `contract_critical` across:
- Bronze staging interfaces
- Silver conformed interfaces
- Gold fact interfaces
- Gold KPI interfaces

Supporting Gold dimensions are included through governance metadata coverage.

## Contract Metadata Standard

Each `contract_critical` model must include:
- `meta.owner`
- `meta.steward`
- `meta.criticality`
- `meta.contract_required_fields`
- `meta.contract_expected_types`

When a model has controlled domains, it must also include:
- `meta.contract_controlled_fields`

## Enforcement Scripts

### 1) Contract Completeness Validation

Script: `dbt/scripts/validate_contracts.py`

Checks:
- required contract metadata keys exist on all `contract_critical` models
- every required field exists in model columns
- every expected-type field exists in model columns
- controlled fields define accepted-value lists
- controlled fields have matching `accepted_values` dbt tests

### 2) Cross-Layer Contract Alignment Validation

Script: `dbt/scripts/validate_contract_alignment.py`

Checks:
- required interface columns are present across critical upstream/downstream pairs
- semantic type declarations stay consistent where both layers declare the same field
- ingestion-to-transformation and transformation-to-serving interface paths remain stable

## Local Validation Flow

From repository root:

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
python dbt/scripts/validate_contracts.py --manifest dbt/target/manifest.json
python dbt/scripts/validate_contract_alignment.py --manifest dbt/target/manifest.json
```

## CI/Governance Integration

Contract checks are designed to run after `dbt parse` in CI.

Recommended gate behavior:
- fail immediately on contract validation error
- block merge on contract-critical violations
- require explicit remediation or approved exception

## Exception Model

Any contract exception must include:
- issue and PR reference
- impacted model and contract field(s)
- owner and steward approval
- expiration date
- remediation follow-up action

No permanent exception should remain without explicit governance review.

