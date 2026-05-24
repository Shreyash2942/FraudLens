# Phase 5 Governance Maintenance Model

Issue: `#64`

## Purpose

Define ownership, update cadence, and handoff responsibilities for Phase 5 quality/governance controls and documentation.

## Ownership Model

- Control framework owner: `fraudlens-data-platform`
- Business governance steward: `fraud-analytics`
- Technical steward: phase owner for active branch milestone

## Maintenance Cadence

- On any selector/test/script change:
  - update control matrix and relevant standards docs in same PR
- On each phase closure:
  - refresh readiness evidence pack and signoff report
- Quarterly (or equivalent milestone):
  - review thresholds and severity policy in failure matrix

## Required Sync Points

When modifying controls, keep these in sync:

- `dbt/selectors.yml`
- `dbt/scripts/validate_*.py`
- `documents/phase-5-quality-governance-standards.md`
- `documents/phase-5-controls-traceability-matrix.md`
- `documents/phase-5-governance-operator-playbooks.md`

## Handoff Checklist

- [ ] All validation scripts pass in local strict mode
- [ ] PR validation workflow reflects current gate design
- [ ] Readiness artifacts regenerated if selector/test coverage changed
- [ ] Standards docs updated with new controls
- [ ] Issue closing notes include commit map + validation summary

## Change Logging Expectation

Every governance change should capture:

- control intent
- impacted selectors/tags/tests/scripts
- risk if omitted
- validation evidence after change

