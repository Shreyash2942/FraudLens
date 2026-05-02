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
