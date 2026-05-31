# Airflow E2E Failure And Recovery Evidence

Issue: `#72`
Captured date: `2026-05-30`

## Goal

Validate failure-branch behavior and recovery expectations for orchestration DAGs:

- failure categorization
- retry policy linkage
- downstream blocking semantics

## Static Validation Completed

### 1) Runtime policy and failure hooks exist

- Source confirms runtime policy mapping and task policy adapters:
  - `airflow/dags/_fraudlens_orchestration_common.py`
- Source confirms failure callback and artifact path emission:
  - `airflow/dags/_fraudlens_orchestration_common.py`
- Source confirms ingestion strict-mode failure gates:
  - `airflow/dags/fraudlens_ingestion_workflow.py`

### 2) Tests validating observability/failure contract pass

Executed:

```powershell
py -m pytest airflow/tests -q
```

Result:

- `15 passed in 0.16s`

This includes logging metadata checks in `airflow/tests/test_logging_metadata.py` that assert presence of:

- `runtime_failure_callback`
- failure classification wiring
- failure artifact directory under `airflow/artifacts/orchestration/failures`

## Runtime Failure-Path Execution Status

Runtime branch execution is currently blocked before DAG run startup because Airflow metadata DB is unavailable:

- `psycopg2.OperationalError`
- connection refused to `localhost:5432`

Because of this, live task-state evidence (`failed`, `upstream_failed`, retry events) cannot be collected in this window.

## Recovery Procedure (When DB Is Restored)

1. Re-run DAG import checks:
   - `airflow dags list`
   - `airflow dags list-import-errors`
2. Trigger controlled strict-mode ingestion failure with invalid batch input.
3. Capture task state output for failure run:
   - `airflow tasks states-for-dag-run fraudlens_ingestion_workflow <run_id>`
4. Verify downstream tasks show `upstream_failed` where expected.
5. Trigger recovery run with valid batch and, where applicable, relaxed strict mode.
6. Verify failure artifact JSON and successful recovery summary artifacts.

## Expected Runtime Evidence Files

- `airflow/artifacts/orchestration/failures/<dag_id>/<run_stamp>/<task_id>.json`
- `airflow/artifacts/orchestration/ingestion/<run_stamp>/ingestion_summary.json`
- `airflow/artifacts/orchestration/pipeline/<run_stamp>/pipeline_summary.json`

## Conclusion

Failure and retry behavior is validated at design and test-contract level; live execution evidence remains blocked by infrastructure dependency (Airflow metadata DB availability).
