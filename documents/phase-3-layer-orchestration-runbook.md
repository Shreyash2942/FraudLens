# Phase 3 Layer Orchestration Runbook

This runbook explains how to generate and run dataset-level Bronze/Silver/Gold assets with Airflow and manual Spark execution.

## 1) Generate Layer Assets

Generate Bronze (implemented), Silver scaffold, and Gold scaffold assets:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/generate_layer_assets.py --layers all --clean --emit-spark-jobs
```

Generated outputs:

- SQL
  - `warehouse/snowflake-warehouse-setup/sql/<layer>/ddl/<layer>__<dataset>.sql`
  - `warehouse/snowflake-warehouse-setup/sql/<layer>/dml/<layer>__<dataset>.sql`
- Layer index files
  - `warehouse/snowflake-warehouse-setup/sql/<layer>/dataset_index.json`
  - `warehouse/snowflake-warehouse-setup/sql/<layer>/_index_ordered.txt`
- Spark jobs
  - `warehouse/snowflake-warehouse-setup/spark/<layer>/jobs/<layer>__<dataset>_job.py`

## 2) Configure Layer Execution

Use `warehouse/snowflake-warehouse-setup/config/local.yml` or `cloud.yml`:

- `dependency_policy: bronze_strict`
- `orchestration.mode: airflow`
- `layers.bronze.enabled: true`
- `layers.silver.enabled: false` (default scaffold state)
- `layers.gold.enabled: false` (default scaffold state)

## 3) Manual Per-Dataset Spark Run

Run one dataset job directly:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_dataset_spark_job.py --layer bronze --dataset payment_instruction --batch-id <batch_id> --profile local
```

The job emits one JSON line with standardized contract fields:

- `status`
- `layer`
- `dataset`
- `batch_id`
- `profile`
- `row_count`
- `error_message`
- `started_at_utc`
- `finished_at_utc`
- `duration_seconds`

## 4) Airflow DAG Execution

DAG:

- `airflow/dags/phase3_layer_dataset_orchestration.py`

Behavior:

- creates one Bronze task per dataset
- enforces Bronze completion gate before downstream groups
- keeps Silver/Gold groups present but disabled by default through config

Trigger with a batch id in `dag_run.conf`, for example:

- `{"batch_id": "20260501_010203"}`

Local Bronze Spark + Hive validation DAG:

- `airflow/dags/phase3_bronze_local_hive_validation.py`

Purpose:

- validates per-dataset Bronze Spark job contracts
- executes local Hive Bronze DDL/DML checks using Beeline

Environment variables used by this DAG:

- `HIVE_CMD`
- `HIVE_JDBC_URL`
- `HIVE_USER`
- `HIVE_PASSWORD`
- `HIVE_DATABASE`
- `BRONZE_LOCAL_SPARK_CMD`

## 5) Bronze SQL Execution

Apply shared setup first:

1. `warehouse/snowflake-warehouse-setup/sql/ddl/create_database_and_schemas.sql`
2. `warehouse/snowflake-warehouse-setup/sql/ddl/create_roles_and_grants.sql`
3. `warehouse/snowflake-warehouse-setup/sql/staging/create_csv_file_format.sql`
4. `warehouse/snowflake-warehouse-setup/sql/staging/create_minio_external_stage.sql`

Then execute per-dataset Bronze SQL in the order defined by:

- `warehouse/snowflake-warehouse-setup/sql/bronze/_index_ordered.txt`
