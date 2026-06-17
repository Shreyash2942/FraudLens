# Airflow

Airflow orchestration assets for FraudLens.

## Primary Branch Handoff

Start with:

- `../documents/orchestration-airflow.md`
  - consolidated branch handoff for `orchestration-airflow`
  - includes architecture summary, dependency model, runtime profiles, MongoDB artifact model,
    operator commands, validation status, and commit ledger

## Current Orchestration DAG Set

- `config/orchestration_profiles.yml`
  - profile contract for `local`, `ci`, and `snowflake` modes
- `dags/_fraudlens_orchestration_common.py`
  - shared repo resolution, profile loading, policy mapping, MongoDB artifact handling,
    failure classification, and observability emitters
- `dags/fraudlens_pipeline_orchestration.py`
  - master stage topology:
    `prepare_runtime -> ingestion_layer -> transformation_layer -> validation_layer -> publish_run_artifacts`
- `dags/fraudlens_ingestion_workflow.py`
  - ingestion workflow task groups:
    `prepare_context -> load_bronze_datasets -> validate_ingestion_results -> publish_ingestion_metadata`
- `dags/fraudlens_transformation_workflow.py`
  - transformation workflow task groups:
    `prepare_dbt_context -> run_bronze_models -> run_silver_models -> run_gold_models -> run_kpi_models -> publish_transformation_metadata`
- `dags/fraudlens_validation_workflow.py`
  - validation workflow task groups:
    `validate_preflight -> validate_bronze_gate -> validate_silver_gate -> validate_gold_gate -> validate_publish_artifacts`

## Artifact Persistence

- orchestration and observability artifacts now persist to MongoDB for `local`, `ci`, and `snowflake`
- legacy local filesystem artifacts under `airflow/artifacts/` can be cleaned with:

```powershell
python scripts/cleanup_airflow_artifacts.py --dry-run
python scripts/cleanup_airflow_artifacts.py
```

## Test Coverage

- `tests/test_ingestion_dag.py`
  - profile contract and ingestion DAG scaffold checks
- `tests/test_transformation_dag.py`
  - transformation DAG syntax, topology, and dbt command contract checks
- `tests/test_validation_dag.py`
  - validation DAG syntax and gate command checks
- `tests/test_logging_metadata.py`
  - canonical metadata schema and Mongo-backed artifact hook checks
- `tests/test_observability_emission.py`
  - observability helper and profile coverage checks

## Supporting References

- `runtime_failure_handling_policy.md`
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
