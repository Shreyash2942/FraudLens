# Airflow E2E Run Evidence

Issue: `#72`
Captured date: `2026-06-09`

## What Was Executed

1. Confirmed container is available.
2. Collected latest reproducible batch candidates from `data/batches/`.
3. Ran Airflow DAG unit/scaffold checks:
   - `py -m pytest airflow/tests -q`
4. Synced DAGs to Data-Lab container:
   - `powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1`
5. Ran Airflow import/runtime checks:
   - `airflow dags list`
   - `airflow dags list-import-errors`
6. Executed component runtime checks:
   - `airflow dags test fraudlens_ingestion_workflow 2026-06-07`
   - `airflow dags test fraudlens_transformation_workflow 2026-06-08`
   - `airflow dags test fraudlens_validation_workflow 2026-06-09`

## Evidence Summary

- Container status: `fraudlens` is running (`Up`, image `shreyash42/data-lab:latest`).
- Local DAG validation tests: `19 passed in 0.11s`.
- Airflow metadata DB check: healthy after manual PostgreSQL startup.
- DAG import check: clean.
- Runtime check status: partial.

## Blocking Signature

Runtime now progresses into DAG execution, but the remaining blocking signature is at the Bronze stage:

- transformation artifact: `airflow/artifacts/orchestration/transformation/20260608T000000/stages/bronze.json`
- result: `exit_code: 1`, `status: failed`
- validation failure artifact: `airflow/artifacts/orchestration/failures/fraudlens_validation_workflow/20260609T000000/validate_bronze_gate.bronze_tag_test.json`

This indicates the runtime environment itself is available, but the stage implementation path is not yet green.

## Dependency and Gate Validation Coverage

Covered now (static):

- DAG definitions and topology tests in `airflow/tests/`
- schedule/retry policy wiring and import-time safety
- clean Airflow metadata DB + import checks
- successful ingestion DAG runtime execution and artifact publication

Blocked now (runtime completion):

- full happy-path master DAG progression (`ingestion -> transformation -> validation`)
- successful transformation path beyond Bronze
- successful validation path beyond Bronze gate

## Artifact Reference

- Structured artifact JSON:
  - `documents/validation/airflow-e2e-run-artifacts.json`
