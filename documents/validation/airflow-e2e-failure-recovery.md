# Airflow E2E Failure And Recovery Evidence

Issue: `#72`
Captured date: `2026-06-09`

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

- `19 passed in 0.11s`

This includes logging metadata checks in `airflow/tests/test_logging_metadata.py` that assert presence of:

- `runtime_failure_callback`
- failure classification wiring
- failure artifact directory under `airflow/artifacts/orchestration/failures`

## Runtime Failure-Path Execution Status

Runtime failure-path evidence is now partially captured:

- transformation Bronze stage writes a failed stage artifact
- validation Bronze gate writes a failed task artifact under `airflow/artifacts/orchestration/failures/...`
- validation summary artifacts now surface `run_status: FAILED` instead of ending green on gate failure

What is still missing:

- a successful recovery run after the Bronze-stage blocker is removed
- a full master-DAG failure/recovery sequence captured through `fraudlens_pipeline_orchestration`

## Recovery Procedure

1. Resolve the Bronze-stage runtime blocker in the warehouse/dbt path.
2. Re-run component DAGs until transformation and validation complete successfully.
3. Trigger `fraudlens_pipeline_orchestration` with a known-good batch.
4. Capture task state output for the controlled failure run:
   - `airflow tasks states-for-dag-run fraudlens_pipeline_orchestration <run_id>`
5. Verify downstream tasks show `upstream_failed` where expected.
6. Trigger the recovery run with corrected inputs/runtime state.
7. Verify failure artifact JSON and successful recovery summary artifacts.

## Expected Runtime Evidence Files

- `airflow/artifacts/orchestration/failures/<dag_id>/<run_stamp>/<task_id>.json`
- `airflow/artifacts/orchestration/ingestion/<run_stamp>/ingestion_summary.json`
- `airflow/artifacts/orchestration/pipeline/<run_stamp>/pipeline_summary.json`

## Conclusion

Failure and retry behavior is now validated at design, test-contract, and partial runtime evidence level; full recovery evidence still depends on clearing the Bronze-stage runtime blocker and completing a master-DAG rerun.
