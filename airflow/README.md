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

Current orchestration DAG set includes:

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
- `dags/fraudlens_transformation_workflow.py`
  - transformation workflow task groups:
    `prepare_runtime_context -> bronze_layer -> silver_layer -> gold_layer -> kpi_layer -> publish_transformation_metadata`
- `dags/fraudlens_validation_workflow.py`
  - validation workflow task groups:
    `quality_checks -> governance_checks -> readiness_bundle`
- `tests/test_ingestion_dag.py`
  - profile contract and DAG scaffold syntax/topology checks
- `tests/test_transformation_dag.py`
  - transformation DAG syntax, topology, and command contract checks
- `tests/test_validation_dag.py`
  - validation DAG syntax and gate command checks
- `tests/test_logging_metadata.py`
  - canonical metadata schema and failure-artifact hook checks
- `runtime_failure_handling_policy.md`
  - runtime schedule/retry/timeout/fail-fast and escalation policy reference

Artifact persistence:

- orchestration run artifacts now persist to MongoDB for `local`, `ci`, and `snowflake` profiles
- local filesystem artifact folders under `airflow/artifacts/` are generated legacy leftovers and can be cleaned with:
  - `python scripts/cleanup_airflow_artifacts.py --dry-run`
  - `python scripts/cleanup_airflow_artifacts.py`

Operational docs:

- `../documents/airflow-orchestration-design-reference.md`
- `../documents/airflow-orchestration-dependency-matrix.md`
- `../documents/airflow-orchestration-operations-runbook.md`
- `../documents/airflow-orchestration-cicd-handoff-checklist.md`
- `../documents/airflow-e2e-validation-runbook.md`
- `../documents/airflow-orchestration-readiness-report.md`
- `../documents/airflow-observability-lineage-design.md`
- `../documents/airflow-observability-operations-runbook.md`

## Syncing DAGs Into Data-Lab Container

If Airflow UI does not watch this repo path directly, sync DAG files into the running container DAG folder:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```

This script copies repo DAGs to `/home/datalab/airflow/dags` in container `fraudlens` and prints import errors.
