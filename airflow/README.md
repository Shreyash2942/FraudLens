# Airflow

Airflow orchestration assets for FraudLens.

Phase 3 adds:

- `dags/phase3_layer_dataset_orchestration.py`
  - dynamic dataset-level Bronze tasks
  - Bronze-complete dependency gate before Silver/Gold
  - Silver/Gold task groups scaffolded and config-controlled (`enabled: false` by default)
