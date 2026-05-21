# Phase 5 Governance Naming Standard

## Purpose

This document defines enforceable naming and governance standards for FraudLens dbt assets.

It supports Phase 5 Issue #60 by standardizing:
- model/table naming
- column naming conventions
- schema and folder organization
- governance metadata requirements

## Layer Naming Standards

Model names must follow layer-specific prefixes:

- Bronze: `stg_bronze__*`
- Silver: `slv__*`
- Gold Facts: `fact_*`
- Gold Dimensions: `dim_*`
- Gold KPI: `kpi_*`

Warehouse-facing aliases must be uppercase.

## Column Naming Standards

All model columns must use snake_case:
- lowercase letters
- numbers
- underscore separators

Examples:
- `payment_instruction_id`
- `ingested_at_utc`
- `high_severity_alert_rate_pct`

## Folder and Schema Standards

Folder placement and model naming must stay aligned:
- `dbt/models/bronze` -> `stg_bronze__*`
- `dbt/models/silver` -> `slv__*`
- `dbt/models/gold/facts` -> `fact_*`
- `dbt/models/gold/dimensions` -> `dim_*`
- `dbt/models/gold/kpi` -> `kpi_*`

Schema mapping remains layer-driven through `dbt_project.yml`:
- Bronze schema
- Silver schema
- Gold schema

## Governance Metadata Standard

Critical models must declare:
- `meta.owner`
- `meta.steward`
- `meta.domain`
- `meta.criticality`

Critical models must also include auditability columns:
- `ingestion_batch_id`
- `source_file_name`
- `ingested_at_utc`
- `lineage_run_id`

## Automated Enforcement

Validation is automated by:
- `dbt/scripts/validate_naming_rules.py`
- `dbt/scripts/validate_governance_metadata.py`
- `dbt/scripts/validate_contracts.py`
- `dbt/scripts/validate_contract_alignment.py`

These checks are executed by:
- `dbt/scripts/validate_structure.sh`
- `dbt/scripts/validate_structure.ps1`
- `.github/workflows/pr-validation.yml`

## Local Validation Command

```bash
bash dbt/scripts/validate_structure.sh
```

## Exception Handling

If a naming or governance exception is required:
- document the exception in issue/PR context
- identify impacted models and fields
- include owner/steward approval
- define expiration date and remediation plan

