# DAGs

Airflow DAG definitions for FraudLens orchestration.

Current Phase 3 DAGs:

- `phase3_layer_dataset_orchestration.py`
  - dataset-level Bronze/Silver/Gold orchestration (Silver/Gold disabled by default)
- `phase3_bronze_local_hive_validation.py`
  - local Bronze validation with Spark contract jobs and Hive DDL/DML checks

If these DAGs do not appear in UI, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```
