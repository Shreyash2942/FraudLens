# Phase 5 Controls Traceability Matrix

Issue: `#64`

## Purpose

Map governance standards to executable controls, selectors, and automation entrypoints.

## Standards -> Controls

| Standard Area | Policy Statement | Primary Controls | Execution Path |
|---|---|---|---|
| Naming | Layer prefixes, aliases, and snake_case must be consistent | `validate_naming_rules.py` | `validate_structure.sh` / PR validation |
| Governance Metadata | Critical models must define owner/steward/domain/criticality | `validate_governance_metadata.py` | `validate_structure.sh` / PR validation |
| Contracts | Contract-critical models must define required fields/types and alignment | `validate_contracts.py`, `validate_contract_alignment.py` | `validate_structure.sh` / PR validation |
| Auditability | Canonical audit fields must be propagated and non-null on critical outputs | `test_governance_required_audit_columns.sql`, `test_audit_trace_lineage_continuity.sql` | selectors + `validate_structure.sh` |
| Lifecycle Traceability | Fraud lifecycle chronology and handoffs must remain valid | `test_lifecycle_traceability_chronology.sql` | selectors + `validate_structure.sh` |
| Failure Handling | Blocking/diagnostic gates must have non-zero coverage and fail-fast behavior | `validate_failure_policy.py`, selector gates | `validate_structure.sh` / PR validation |
| Readiness | Cross-layer governance evidence must be captured for signoff | `capture_phase5_governance_readiness.py` + readiness docs | readiness closure workflow |

## Selector Mapping

| Selector | Control Intent |
|---|---|
| `quality_critical_gate` | Blocking-quality controls |
| `quality_high_gate` | High-severity controls |
| `governance_critical_gate` | Governance metadata compliance |
| `contract_critical_gate` | Contract structural enforcement |
| `audit_traceability_gate` | Audit + trace continuity coverage |
| `failure_blocking_gate` | Unified blocking gate |
| `failure_diagnostic_gate` | Expanded diagnostic gate |
| `phase5_readiness_bundle` | Consolidated readiness scope |

## Workflow Mapping

| Workflow / Script | Role |
|---|---|
| `.github/workflows/pr-validation.yml` | Enforces strict validation in PR |
| `dbt/scripts/validate_structure.sh` | Local + CI fail-fast control bundle |
| `dbt/scripts/validate_docs.sh` | Docs-generation validation |
| `dbt/scripts/capture_phase5_governance_readiness.py` | Readiness evidence artifact capture |

## Evidence Mapping

| Evidence Artifact | Purpose |
|---|---|
| `documents/validation/phase-5-governance-readiness-artifacts.json` | Command + selector execution evidence |
| `documents/validation/phase-5-governance-readiness-evidence.md` | Cross-layer reconciliation narrative |
| `documents/validation/phase-5-governance-integrated-controls.md` | Integrated controls pass/fail matrix |
| `documents/phase-5-governance-readiness-report.md` | Final readiness signoff |

