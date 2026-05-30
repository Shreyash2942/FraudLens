# DAGs

Airflow DAG definitions for FraudLens orchestration.

Current Phase 3 DAGs:

- `phase3_layer_dataset_orchestration.py`
  - dataset-level Bronze/Silver/Gold orchestration (Silver/Gold disabled by default)
- `phase3_bronze_local_hive_validation.py`
  - local Bronze validation with Spark contract jobs and Hive DDL/DML checks

Phase 6 DAGs:

- `fraudlens_pipeline_orchestration.py`
  - master orchestration scaffold for runtime prep, stage gates, and run artifact publication
- `fraudlens_ingestion_workflow.py`
  - ingestion workflow with context preparation, asset checks, dataset fan-out, validation, and summary publishing
- `_fraudlens_orchestration_common.py`
  - shared helper module for profile/batch/dataset runtime behaviors

Runtime policy reference:

- `../runtime_failure_handling_policy.md`
  - schedule modes, retry/timeouts by task class, and fail-fast escalation behavior

If these DAGs do not appear in UI, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```
