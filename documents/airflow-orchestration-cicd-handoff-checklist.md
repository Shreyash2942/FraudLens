# Airflow Orchestration CI/CD Integration And Handoff Checklist

Issue: `#73`
Last updated: `2026-05-30`

## Objective

Define minimum CI/CD and handoff requirements before operations can treat orchestration changes as release-ready.

## CI Integration Checklist

- [ ] DAG imports pass in CI runtime context.
- [ ] `airflow/tests` suite passes.
- [ ] profile contract parse checks pass for `local` and `ci`.
- [ ] no unresolved import errors from `airflow dags list-import-errors` in CI image.
- [ ] orchestration docs updated when DAG behavior changes.

## Runtime Integrity Checklist

- [ ] master DAG topology preserved: `prepare -> ingestion -> transformation -> validation -> publish`.
- [ ] transformation layer gate order preserved: `bronze -> silver -> gold -> kpi`.
- [ ] failure callback wiring remains enabled for all workflow DAGs.
- [ ] canonical run metadata keys remain complete in summary artifacts.

## Promotion Checklist

- [ ] execute one successful pipeline run in promoted environment.
- [ ] execute one controlled failure/recovery scenario.
- [ ] archive run evidence and failure artifacts with run IDs.
- [ ] confirm operator runbook references current commands and paths.

## Handoff Package

Minimum package for the next phase/team:

1. design reference (`documents/airflow-orchestration-design-reference.md`)
2. dependency matrix (`documents/airflow-orchestration-dependency-matrix.md`)
3. operations runbook (`documents/airflow-orchestration-operations-runbook.md`)
4. e2e validation evidence (`documents/validation/airflow-e2e-*.md` and `.json`)
5. readiness report (`documents/airflow-orchestration-readiness-report.md`)

## Sign-Off Fields

- owner:
- date:
- environment:
- baseline commit:
- known risks/open blockers:
