# Phase 3 Warehouse Setup Runbook

This runbook is the operator path for setting up Phase 3 warehouse assets and running the first Bronze batch load.

## Scope

- stage 1 (`#39`) environment and access checks
- stage 2 (`#40`) warehouse structure and naming
- stage 3 (`#41`) Bronze table foundation
- stage 4 (`#42`) MinIO-to-Bronze ingestion setup
- stage 5 (`#43`) file format and stage handling
- stage 6 (`#44`) validation checks
- stage 7 (`#45`) initial performance baseline

## Prerequisites

- repository cloned locally
- Python environment with project dependencies installed
- at least one generated batch under `data/batches/<batch_id>/`
- `.env` configured from `warehouse/snowflake-warehouse-setup/config/env.example`
- local mode default: `PHASE3_ENV=local`

## 1) Validate Runtime Profile

```powershell
py warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py local
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
```

Expected:

- profile resolves without errors
- local mode checks report reachable MinIO and Trino endpoints

## 2) Generate Layer Assets

```powershell
py warehouse/snowflake-warehouse-setup/scripts/generate_layer_assets.py --layers bronze --clean --emit-spark-jobs
```

Outputs include:

- `warehouse/snowflake-warehouse-setup/sql/bronze/ddl/`
- `warehouse/snowflake-warehouse-setup/sql/bronze/dml/`
- `warehouse/snowflake-warehouse-setup/sql/bronze/_index_ordered.txt`
- `warehouse/snowflake-warehouse-setup/spark/bronze/jobs/`

## 3) Apply Shared SQL Setup

Execute in this order:

1. `warehouse/snowflake-warehouse-setup/sql/ddl/create_database_and_schemas.sql`
2. `warehouse/snowflake-warehouse-setup/sql/ddl/create_roles_and_grants.sql`
3. `warehouse/snowflake-warehouse-setup/sql/staging/create_csv_file_format.sql`
4. `warehouse/snowflake-warehouse-setup/sql/staging/create_minio_external_stage.sql`

Then execute dataset Bronze DDL in:

- `warehouse/snowflake-warehouse-setup/sql/bronze/ddl/`

## 4) Build Batch Load SQL

For a full batch:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_batch.py --batch-id <batch_id>
```

For one dataset:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_one_dataset.py --batch-id <batch_id> --dataset payment_instruction --write-sql
```

## 5) Execute Bronze Jobs (Local Validation Path)

Single dataset contract run:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_dataset_spark_job.py --layer bronze --dataset region --batch-id <batch_id> --profile local --spark-submit-cmd python
```

Optional local Hive check:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_local_hive_bronze_check.py --dataset region --batch-id latest --execute --dml-mode explain
```

## 6) Run Validation SQL

Generate batch-specific row-count reconciliation SQL from the manifest:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/validate_load.py --batch-id <batch_id> --emit-row-count-sql
```

Run validation bundles after load:

- `warehouse/snowflake-warehouse-setup/sql/runtime/validation/bronze_row_count_reconciliation_<batch_id>.sql` (generated)
- `warehouse/snowflake-warehouse-setup/sql/validation/bronze_null_key_checks.sql`
- `warehouse/snowflake-warehouse-setup/sql/validation/bronze_domain_sanity_checks.sql`

Use the load manifest under `data/batches/<batch_id>/control/manifest.json` as the row-count reference.

## 7) Capture Baseline Performance (`#45`)

Run benchmark for all datasets in latest batch:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/benchmark_load.py --batch-id latest --profile local --runs 1 --spark-submit-cmd python
```

Artifacts:

- `warehouse/snowflake-warehouse-setup/sql/runtime/performance/benchmark_<batch_id>_<timestamp>.json`
- `warehouse/snowflake-warehouse-setup/sql/runtime/performance/benchmark_<batch_id>_<timestamp>.md`

Optional Snowflake report SQL:

- `warehouse/snowflake-warehouse-setup/sql/validation/bronze_load_performance_report.sql`

## 8) Handoff Checklist

- environment checks pass
- Bronze DDL deployed
- one full batch load SQL bundle generated
- at least one dataset contract run completed
- validation SQL executed
- baseline benchmark artifact captured and retained
