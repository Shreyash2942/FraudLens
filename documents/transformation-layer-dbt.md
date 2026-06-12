# Transformation Layer DBT (Phase 4)

Status date: `2026-05-25`
Milestone scope: `#47` with sub-issues `#48`-`#55`

## Purpose

This document consolidates Phase 4 planning, implementation structure, governance controls, and readiness validation for the dbt transformation layer.

## Primary Phase File

Use this as the primary Phase 4 review and handoff file in `documents/`.

## Scope Consolidated

- `#48` Setup dbt project and warehouse profiles
- `#49` Build Bronze models
- `#50` Build Silver models
- `#51` Build Gold fact models
- `#52` Build Gold dimension models
- `#53` Implement KPI and metric logic
- `#54` Add auditability, documentation, and model standards
- `#55` Validate model outputs and readiness

## Executive Outcome

Phase 4 delivered a Medallion dbt transformation foundation for FraudLens:

- Bronze -> Silver -> Gold model layering with governed folder structure
- fact, dimension, and KPI model domains aligned to fraud analytics use cases
- centralized KPI logic and reusable macros
- governance controls for ownership, auditability, and documentation standards
- validation runbook and readiness evidence artifacts for handoff review

## Target DBT Architecture

- project: `dbt/dbt_project.yml`
- source declarations: `dbt/models/sources/`
- model layers: `dbt/models/bronze/`, `dbt/models/silver/`, `dbt/models/gold/`
- supporting logic: `dbt/macros/`, `dbt/tests/`, optional `dbt/seeds/`
- profiles include local Spark/Hive validation path plus Snowflake cutover templates

## Issue-by-Issue Delivery Plan

### `#48` Foundation

- initialize dbt project scaffold
- configure target/profile conventions
- define source metadata for governed datasets
- add shared naming and audit macros
- apply layer tags/defaults
- add parse/list CI validation commands

### `#49` Bronze

- create standardized Bronze staging models
- preserve source fidelity and audit passthrough
- apply baseline quality tests and reconciliation checks

### `#50` Silver

- clean and standardize datasets
- deduplicate and normalize typed fields
- enforce relationship-safe and lifecycle-safe transformations

### `#51` Gold Facts

- implement core transaction, payment event, and fraud operations facts
- define explicit grains and conformed keys
- support incremental-friendly execution where needed

### `#52` Gold Dimensions

- implement shared conformed dimensions (calendar, geography, organization)
- implement party/account/payment context dimensions
- support hierarchy-aware reporting navigation

### `#53` KPI Logic

- define canonical KPI contracts and calculations
- centralize reusable metric calculations in dbt layer
- add guardrail tests for denominator/range safety

### `#54` Governance and Standards

- enforce required audit columns and metadata
- complete model documentation and exposure declarations
- run docs generation and governance validation checks

### `#55` Validation and Readiness

- execute parse/build/test bundles by layer
- publish reconciliation and KPI scenario evidence
- issue readiness report and signoff checklist

## Governance Controls

### Required Controls

- ownership/steward metadata on critical models
- required audit and lineage fields in serving outputs
- documented model and key-column definitions
- relationship integrity tests across Silver and Gold
- validation gate (`parse`, `ls`, targeted tests, docs generation)

### Reviewer Command Bundle

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --select test_governance_required_audit_columns --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt docs generate --empty-catalog --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

## Readiness Snapshot

- implementation coverage: `READY`
- governance/docs coverage: `READY`
- runtime validation: `CONDITIONAL` during prior run due to local Hive thrift availability

Final readiness requires rerun of full local validation bundle with active Hive thrift endpoint and attachment of passing evidence artifacts.

## Consolidation Note

Earlier Phase 4 working documents were consolidated into this file and are not retained separately
in the root `documents/` directory.

## Reviewer Notes

Use this as the only retained Phase 4 document in `documents/`.
