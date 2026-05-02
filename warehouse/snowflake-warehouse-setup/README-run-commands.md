# Phase 3 Run Commands

This quick reference provides the Python commands for synthetic generation and Phase 3 dataset-level execution.

## 1) Synthetic Data Generation (Phase 2)

Generate one synthetic batch locally:

```powershell
py -m synthetic_generator.generate --mode mixed --output-dir data --profile small_fast --seed 42
```

Generate and upload to MinIO:

```powershell
py -m synthetic_generator.generate --mode mixed --output-dir data --profile small_fast --seed 42 --validate --upload-minio
```

Generate using runtime config file:

```powershell
py -m synthetic_generator.generate --runtime-config synthetic_generator/runtime_config.yaml --mode mixed --output-dir data --profile small_fast --seed 42 --validate --upload-minio
```

## 2) Phase 3 Environment Checks

Print active profile config:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py local
```

Connectivity checks:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
```

## 3) Generate Layer Assets

Generate Bronze/Silver/Gold dataset-level SQL and Spark job templates:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/generate_layer_assets.py --layers all --clean --emit-spark-jobs
```

Bronze-only compatibility command:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/generate_bronze_assets.py
```

## 4) Bronze SQL Load Helpers

Create one dataset `COPY INTO` SQL for a batch:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_one_dataset.py --batch-id <batch_id> --dataset payment_instruction --write-sql
```

Create full batch SQL from manifest:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_batch.py --batch-id <batch_id>
```

## 5) Per-Dataset Spark Job Execution

Run one dataset job manually:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_dataset_spark_job.py --layer bronze --dataset region --batch-id <batch_id> --profile local --spark-submit-cmd spark-submit
```

For local script-only contract test (without Spark cluster):

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_dataset_spark_job.py --layer bronze --dataset region --batch-id <batch_id> --profile local --spark-submit-cmd python
```

## 5.1) Local Hive DDL/DML Check (Per Dataset)

Generate and execute local Hive Bronze DDL/DML for one dataset:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_local_hive_bronze_check.py --dataset region --batch-id latest --execute --dml-mode explain
```

## 6) Airflow DAG

Dataset-level orchestration DAG:

- `airflow/dags/phase3_layer_dataset_orchestration.py`

Local Bronze Spark + Hive validation DAG:

- `airflow/dags/phase3_bronze_local_hive_validation.py`

Trigger with `dag_run.conf`:

```json
{"batch_id": "20260501_010203"}
```

Recommended trigger for local Bronze Hive validation DAG:

```json
{"batch_id":"latest","hive_dml_mode":"explain"}
```

If you want full physical DML execution (slower, heavier):

```json
{"batch_id":"latest","hive_dml_mode":"execute"}
```

If DAGs are not visible in Airflow UI because the UI is not mounted to this repo path, sync DAG files to container DAG folder:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_airflow_dags_to_fraudlens_container.ps1
```
