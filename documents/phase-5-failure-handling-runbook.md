# Phase 5 Failure Handling Runbook

## Purpose

This runbook defines how FraudLens handles validation failures in local and CI execution.

It enforces fail-fast behavior for critical controls while preserving a diagnostic path for investigation workflows.

## Severity Model

- `critical`: block execution immediately
- `high`: include in diagnostic and readiness gates
- `medium`: non-blocking during iteration, must be remediated before signoff
- `low`: informational

## Selector Gates

Configured in `dbt/selectors.yml`:

- `quality_critical_gate`
- `quality_high_gate`
- `governance_critical_gate`
- `contract_critical_gate`
- `audit_critical_gate`
- `validation_critical_gate`
- `failure_blocking_gate`
- `failure_diagnostic_gate`

## Execution Modes

### Strict Mode (default)

- env: `FRAUDLENS_VALIDATION_MODE=strict`
- hard requirements:
  - `failure_blocking_gate` resolves to non-zero test coverage
  - naming/governance/contract/failure-policy checks pass
- behavior:
  - stop immediately on first blocking failure

### Diagnostic Mode

- env: `FRAUDLENS_VALIDATION_MODE=diagnostic`
- requirements:
  - strict checks
  - `failure_diagnostic_gate` resolves to non-zero coverage
- behavior:
  - same hard blocking for critical failures
  - expanded gate coverage for triage workflows

## Enforced Validation Commands

Primary entrypoint:

```bash
bash dbt/scripts/validate_structure.sh
```

This script performs:

1. `dbt parse`
2. gate coverage validation (`failure_blocking_gate`, and `failure_diagnostic_gate` in diagnostic mode)
3. governance/contract/naming/failure-policy checks:
   - `validate_naming_rules.py`
   - `validate_governance_metadata.py`
   - `validate_contracts.py`
   - `validate_contract_alignment.py`
   - `validate_failure_policy.py`
4. `dbt ls`

## CI Behavior

`pr-validation.yml` runs strict mode by default:

- `FRAUDLENS_VALIDATION_MODE: strict`
- fails PR on any critical gate or governance/contract policy failure

## Failure Triage Steps

When validation fails:

1. Identify failing gate/check from script output
2. Determine impacted layer/model family
3. Validate if failure is:
   - metadata/config defect
   - contract drift
   - audit lineage gap
   - selector coverage regression
4. Apply fix and rerun:
   - `bash dbt/scripts/validate_structure.sh`
5. Only merge after strict mode passes

## Exception Handling

Any temporary exception requires:

- issue/PR reference
- impacted selector/check and model list
- owner + steward approval
- expiry date
- remediation follow-up

No critical validation exception is permanent.

