# Airflow

Airflow orchestration assets for FraudLens.

Phase 3 adds:

- `dags/phase3_layer_dataset_orchestration.py`
  - dynamic dataset-level Bronze tasks
  - Bronze-complete dependency gate before Silver/Gold
  - Silver/Gold task groups scaffolded and config-controlled (`enabled: false` by default)
- `dags/phase3_bronze_local_hive_validation.py`
  - local Bronze-only validation flow
  - runs per-dataset Spark contract checks
  - runs per-dataset local Hive DDL/DML checks through Beeline

Phase 6 scaffolding adds:

- `config/orchestration_profiles.yml`
  - profile contract for `local`, `ci`, and future `snowflake` modes
- `dags/_fraudlens_orchestration_common.py`
  - shared repo resolution, profile loading, dataset selection, and batch helpers
- `dags/fraudlens_pipeline_orchestration.py`
  - master stage topology skeleton:
    `prepare_runtime -> ingestion_layer -> transformation_layer -> validation_layer -> publish_run_artifacts`
- `dags/fraudlens_ingestion_workflow.py`
  - ingestion workflow task groups:
    `prepare_context -> load_bronze_datasets -> validate_ingestion_results -> publish_ingestion_metadata`
- `tests/test_ingestion_dag.py`
  - profile contract and DAG scaffold syntax/topology checks
- `runtime_failure_handling_policy.md`
  - runtime schedule/retry/timeout/fail-fast and escalation policy reference

## Syncing DAGs Into Data-Lab Container

If Airflow UI does not watch this repo path directly, sync DAG files into the running container DAG folder:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```

This script copies repo DAGs to `/home/datalab/airflow/dags` in container `fraudlens` and prints import errors.
