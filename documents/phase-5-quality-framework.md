# Phase 5 Data Quality Framework

## Purpose

This framework defines how FraudLens evaluates data quality and governance reliability across Bronze, Silver, Gold, and KPI layers.

It establishes:
- quality expectations by layer
- severity levels for validation outcomes
- control categories and execution intent
- baseline acceptance criteria for critical datasets

## Layer Expectations

### Bronze

Objective:
- preserve source fidelity with minimal transformation

Minimum expectations:
- source freshness is tracked for governed datasets
- required business keys are present for critical entities
- ingestion and lineage metadata is present
- row-count reconciliation is available for critical ingestion paths

### Silver

Objective:
- provide conformed, trusted, and standardized datasets

Minimum expectations:
- canonical identifiers are unique where contract requires it
- controlled status/code fields remain in approved domains
- governed relationships align with `specs/relationship-map.yaml`
- normalization rules are consistent and testable

### Gold And KPI

Objective:
- provide business-ready serving models and trustworthy metrics

Minimum expectations:
- fact grain integrity is enforced
- dimension conformance supports stable slicing/filtering
- KPI logic is denominator-safe and range-bounded
- audit/trace fields are retained for governance evidence

## Validation Categories

Validation categories used in Phase 5:

1. `freshness`
2. `completeness`
3. `uniqueness`
4. `referential_integrity`
5. `domain_validity`
6. `audit_traceability`
7. `reconciliation`

## Severity Model

### `critical`

- meaning: unsafe or non-compliant state
- behavior: hard stop for execution and CI gating
- examples:
  - null critical keys
  - duplicate critical unique keys
  - broken critical relationships
  - missing required audit/lineage fields

### `high`

- meaning: high operational or governance risk
- behavior: blocks release/readiness, may be investigated in dev loops
- examples:
  - controlled-domain drift on high-impact lifecycle fields
  - contract metadata gaps in critical serving outputs

### `medium`

- meaning: quality degradation with contained immediate risk
- behavior: track and fix before readiness signoff
- examples:
  - non-critical reconciliation drift outside baseline tolerance
  - non-blocking contract hygiene issues

### `low`

- meaning: informational or trend-watch quality concern
- behavior: monitor and prioritize through backlog hygiene

## Baseline Acceptance Criteria

For critical dataset interfaces:

- required key null tolerance: `0%`
- required unique-key duplicate tolerance: `0%`
- critical relationship failure tolerance: `0%`
- KPI percentage bounds: `0 <= value <= 100`
- critical audit field non-null tolerance: `0%`

## Execution Intent

Phase 5 implementation maps this framework to:
- dbt selectors for severity/category routing
- standardized dbt tests by layer and model criticality
- CI fail-fast behavior for `critical` controls
- readiness evidence artifacts for governance signoff
