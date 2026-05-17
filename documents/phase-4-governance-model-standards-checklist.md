# Phase 4 Governance Model Standards Checklist

This checklist defines the governance review baseline for FraudLens dbt transformation assets in Phase 4.

## Scope

- Bronze, Silver, and Gold dbt models
- Gold KPI models
- dbt tests and exposures
- dbt documentation artifacts

## Standards Alignment

- `standards/modeling-standard.md`
- `standards/auditability-standard.md`
- `specs/relationship-map.yaml`

## Required Governance Controls

1. Ownership and Stewardship
- each Gold model has `meta.owner` and `meta.steward`
- business domain is declared in model metadata (`meta.domain`)
- critical models are flagged with `meta.criticality`

2. Auditability
- required audit fields are preserved in serving facts and KPI outputs
- `test_governance_required_audit_columns` passes for governed Gold outputs
- lineage identifiers (`lineage_run_id`, batch metadata) are present and non-null

3. Documentation Coverage
- model descriptions are present for governed dbt models
- key columns used for joins and KPIs have descriptions
- docs site generation succeeds via `dbt docs generate --empty-catalog`

4. Relationship and Dependency Clarity
- relationship tests exist for key FK links in Silver and Gold
- Gold exposures map dashboard and analytical dependencies
- relationship-map assumptions are reflected in model contracts/tests

5. Validation Gate
- `dbt parse` passes
- `dbt ls` passes
- selected governance and KPI tests pass

## Reviewer Runbook

Run from local container:

```bash
dbt parse --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt ls --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt test --select test_governance_required_audit_columns --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
dbt docs generate --empty-catalog --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

## Signoff Checklist

- [ ] Ownership metadata verified
- [ ] Audit column enforcement test verified
- [ ] Documentation generation verified
- [ ] Exposures reviewed for downstream dependency coverage
- [ ] Open governance exceptions recorded in issue comments
