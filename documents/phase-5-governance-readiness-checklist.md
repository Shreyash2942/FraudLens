# Phase 5 Governance Readiness Checklist

Issue: `#63`  
Parent milestone: `#56`

## Bronze Governance Coverage

- [ ] Critical Bronze staging models preserve ingestion + lineage metadata
- [ ] Bronze contract-critical model metadata is present (`owner`, `steward`, `criticality`, contract fields)
- [ ] Bronze naming and layer conventions pass automated checks
- [ ] Bronze-to-Silver lineage continuity is evidenced for payment/fraud lifecycle entities

## Silver Quality Controls

- [ ] Critical Silver keys pass `not_null` and `unique` controls
- [ ] Critical Silver relationships pass referential checks
- [ ] Controlled-value tests exist for lifecycle status fields
- [ ] Silver contract-critical metadata coverage is complete
- [ ] Silver audit/trace fields align to canonical model (`created_at_utc`, `updated_at_utc`, `pipeline_run_id`, `source_system`)

## Gold Business Trustworthiness

- [ ] Gold facts and KPI models satisfy critical governance/audit checks
- [ ] Gold relationship and grain checks pass
- [ ] KPI guardrails and controlled scenario tests are present
- [ ] Fact/KPI outputs retain upstream trace context (`batch`, `file`, `run`, canonical audit timestamps)

## Orchestration And CI Readiness

- [ ] `failure_blocking_gate` resolves to non-zero test coverage
- [ ] `phase5_readiness_bundle` resolves to non-zero test coverage
- [ ] `validate_structure` scripts enforce fail-fast critical checks
- [ ] PR validation workflow runs strict validation mode
- [ ] Failure policy matrix is aligned with live selector/tag coverage

## Evidence Artifacts

- [ ] `documents/validation/phase-5-governance-readiness-artifacts.json`
- [ ] `documents/validation/phase-5-governance-readiness-evidence.md`
- [ ] `documents/phase-5-governance-readiness-report.md`

## Readiness Decision

- [ ] `READY`
- [ ] `CONDITIONAL READY`
- [ ] `NOT READY`

