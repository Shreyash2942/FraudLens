# Phase 5 Governance Operator Playbooks

Issue: `#64`  
Audience: data platform operators, analytics engineers, and governance reviewers.

## Playbook A: Standard Validation Run (Strict)

Use for PR checks and pre-merge readiness.

Command:

```bash
bash dbt/scripts/validate_structure.sh
```

Expected behavior:
- parse/list validation executes
- gating selector coverage is validated
- naming/governance/contract/failure-policy checks run
- command exits non-zero on critical failures

## Playbook B: Diagnostic Validation Run

Use for triage and broader control visibility.

Command:

```bash
FRAUDLENS_VALIDATION_MODE=diagnostic bash dbt/scripts/validate_structure.sh
```

Expected behavior:
- strict checks still enforced
- diagnostic gate coverage is additionally validated
- broader signal set available for investigation

## Playbook C: Docs And Metadata Verification

Use for publish/readability and lineage metadata sanity.

Command:

```bash
bash dbt/scripts/validate_docs.sh
```

Expected behavior:
- docs artifacts generated
- no structural failure in docs pipeline

## Playbook D: Governance Readiness Evidence Capture

Use when preparing issue closure evidence.

Command:

```bash
python dbt/scripts/capture_phase5_governance_readiness.py
```

Outputs:
- `documents/validation/phase-5-governance-readiness-artifacts.json`

## Playbook E: Failure Triage

When strict mode fails:

1. Identify failing gate/check from output.
2. Classify failure type:
   - naming
   - governance metadata
   - contract completeness/alignment
   - failure policy coverage
   - model-level quality tests
3. Apply fix in smallest scope possible.
4. Rerun strict mode.
5. Capture rerun evidence for issue/PR.

## Exception Handling Playbook

If temporary exception is required:

1. Open issue/PR note with impacted controls and models.
2. Include owner + steward approval.
3. Set expiration date and remediation owner.
4. Track follow-up in readiness artifacts.

