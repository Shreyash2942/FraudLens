# Airflow E2E Run Evidence

Issue: `#72`
Captured date: `2026-05-30`

## What Was Executed

1. Confirmed container is available.
2. Collected latest reproducible batch candidates from `data/batches/`.
3. Ran Airflow DAG unit/scaffold checks:
   - `py -m pytest airflow/tests -q`
4. Synced DAGs to Data-Lab container:
   - `powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1`
5. Attempted Airflow import/runtime checks:
   - `airflow dags list`
   - `airflow dags list-import-errors`

## Evidence Summary

- Container status: `fraudlens` is running (`Up`, image `shreyash42/data-lab:latest`).
- Local DAG validation tests: `15 passed in 0.16s`.
- Runtime check status: blocked.

## Blocking Signature

Both `airflow dags list` and `airflow dags list-import-errors` fail with:

- `psycopg2.OperationalError`
- connection refused on `localhost:5432`

This indicates Airflow metadata DB is not reachable in the current runtime.

## Dependency and Gate Validation Coverage

Covered now (static):

- DAG definitions and topology tests in `airflow/tests/`
- schedule/retry policy wiring and import-time safety

Blocked now (runtime):

- task-state transition proof from live DAG run
- runtime dependency progression evidence (`ingestion -> transformation -> validation`)
- live failure branch (`failed`/`upstream_failed`) state capture

## Artifact Reference

- Structured artifact JSON:
  - `documents/validation/airflow-e2e-run-artifacts.json`
