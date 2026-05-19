# Phase 5 Data Contract Requirements

## Purpose

This document defines contract requirements for critical FraudLens datasets and transformation outputs.

Contracts in Phase 5 must make structural expectations explicit and enforceable:
- required fields
- expected data types
- accepted values for controlled fields
- interface alignment across Bronze, Silver, Gold, and KPI layers

## Contract Scope

Critical contract scope includes:
- payment and transaction lifecycle models
- fraud operations lifecycle models (risk, alert, case, decision, disposition)
- Gold fact and KPI serving interfaces

## Required Field Baseline

For critical models, contracts must include:

1. Business key fields
- entity identifier at model grain

2. Governing relationship fields
- upstream/downstream join keys required by `specs/relationship-map.yaml`

3. Audit and lineage fields
- `ingestion_batch_id`
- `source_file_name`
- `ingested_at_utc`
- `lineage_run_id`
- plus layer-specific canonical audit fields where defined

## Expected Data Type Baseline

Type expectations must be documented for contract-critical fields:

- identifier fields: `string`
- date fields: `date`
- event timestamps: `timestamp`
- code/status/severity fields: `string`
- amounts: `decimal`/`numeric`
- boolean flags: `boolean`

Type intent may differ physically by adapter, but semantic contract type must remain stable.

## Accepted Value Baseline

Controlled field domains must be contract-declared where applicable:

- lifecycle status fields
- severity/risk bands
- decision/disposition type fields
- transaction direction and similar enumerations

Accepted values are enforced with dbt tests and tied to severity controls.

## Cross-Layer Contract Alignment

### Bronze
- preserve source-facing interface with required load/audit columns
- no destructive normalization that obscures source meaning

### Silver
- normalize to canonical names/types
- maintain relationship-ready conformed keys
- enforce controlled domains

### Gold/KPI
- preserve serving-grain identifiers
- retain contract-critical auditability fields
- maintain stable metric interface used by downstream analytics

## Contract Metadata Requirements

Critical models must carry metadata that supports governance automation:

- `owner`
- `steward`
- `criticality`
- contract-specific metadata:
  - required_fields
  - expected_types
  - controlled_fields (where applicable)

## Enforcement Path

Contract controls are implemented through:
- model property metadata (`*.yml`)
- generic and singular dbt tests
- selector-driven governance/contract gates in CI and readiness validation

## Exception Policy

Any contract exception must:
- be documented in issue/PR context
- include owner and expiration target
- include mitigation and follow-up tracking reference
