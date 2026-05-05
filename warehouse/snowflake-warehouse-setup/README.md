# Phase 3 Warehouse Assets

This directory contains executable assets for Phase 3 (`#39` to `#46`) with local-first and cloud-ready configuration patterns.

## Stage 1 to Stage 8 Scope

- Stage 1 (`#39`): environment config and access checks
- Stage 2 (`#40`): warehouse structure and naming standards
- Stage 3 (`#41`): Bronze table creation assets
- Stage 4 (`#42`): MinIO ingestion SQL patterns and execution helpers
- Stage 5 (`#43`): stage and file-format handling
- Stage 6 (`#44`): validation SQL patterns
- Stage 7 (`#45`): baseline load performance benchmarking
- Stage 8 (`#46`): runbook and troubleshooting documentation

## Directory Layout

- `config/` environment profile files
- `scripts/` executable helpers (connectivity, SQL generation, load SQL builders)
- `sql/bronze/` dataset-level Bronze SQL
- `sql/silver/` dataset-level Silver scaffold SQL
- `sql/gold/` dataset-level Gold scaffold SQL
- `sql/ddl/` shared/admin DDL (database/schema/roles/grants)
- `sql/staging/` file format and external stage SQL
- `sql/dml/` legacy grouped Bronze `COPY INTO` SQL (migration path)
- `sql/naming/` naming standard reference SQL
- `sql/validation/` load validation and benchmark reporting SQL
- `spark/` layer-first Spark job assets and shared job contracts

## Scripts

The `scripts/` folder contains reusable execution helpers through Stage 7.

- `_config_loader.py`
  - shared loader used by other scripts
  - reads `config/local.yml` or `config/cloud.yml`
  - resolves environment variables for secret values
- `print_runtime_config.py`
  - prints resolved runtime configuration as JSON
  - use for profile/debug checks before setup or load runs
- `check_connectivity.py`
  - validates environment readiness
  - local mode checks Trino/MinIO endpoint reachability
  - cloud mode checks required `SNOWFLAKE_*` variables are set
- `generate_bronze_assets.py`
  - compatibility wrapper for bronze-only generation
- `generate_layer_assets.py`
  - generates dataset-level SQL and Spark job assets for Bronze/Silver/Gold
- `load_one_dataset.py`
  - emits one dataset-specific `COPY INTO` statement for a batch id
- `load_batch.py`
  - emits ordered `COPY INTO` statements for all datasets in a batch manifest
- `run_dataset_spark_job.py`
  - runs one layer/dataset Spark job with standard contract args
- `run_local_hive_bronze_check.py`
  - validates one Bronze dataset in local Hive by executing generated DDL/DML checks
- `validate_load.py`
  - generates batch-specific row-count reconciliation SQL and validation inputs from manifest metadata
- `benchmark_load.py`
  - executes repeatable dataset-run benchmarks and writes runtime performance reports

Example usage:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py local
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
py warehouse/snowflake-warehouse-setup/scripts/generate_layer_assets.py --layers bronze --clean --emit-spark-jobs
```

## Execution Order

1. review and adapt `config/local.yml` or `config/cloud.yml`
2. run `scripts/print_runtime_config.py` to confirm resolved values
3. run `scripts/check_connectivity.py` for environment validation
4. generate layer assets with `scripts/generate_layer_assets.py`
5. apply DDL and staging files in `sql/ddl/`, `sql/staging/`, and `sql/bronze/`
6. execute dataset-level Bronze SQL or build runtime SQL with `scripts/load_batch.py`
7. run per-dataset Spark jobs using `scripts/run_dataset_spark_job.py`
8. run local Bronze Hive validation using `scripts/run_local_hive_bronze_check.py` or Airflow DAG `airflow/dags/phase3_bronze_local_hive_validation.py`
9. generate/execute validation SQL using `scripts/validate_load.py` and `sql/validation/`
10. capture baseline benchmark outputs using `scripts/benchmark_load.py`
