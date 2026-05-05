# Phase 3 Scripts

This folder contains runtime helper scripts for Phase 3 (`#39` to `#45`) setup, layer-first asset generation, dataset-level execution, validation, and load benchmarking.

## Why These Scripts Exist

Before applying warehouse SQL or running ingestion, we need a reliable way to:

- resolve the active environment profile (`local` or `cloud`)
- inspect the effective runtime config
- verify required services/secrets are available

## Scripts

### `_config_loader.py`

Shared utility module used by the other scripts.

Responsibilities:

- load `warehouse/snowflake-warehouse-setup/config/local.yml` or `cloud.yml`
- validate profile selection from `PHASE3_ENV`
- read secret values from environment variables

### `print_runtime_config.py`

Prints the resolved runtime configuration as JSON.

Use this to confirm profile values before setup/load steps.

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py local
```

### `check_connectivity.py`

Runs readiness checks based on selected environment:

- local mode:
  - checks Trino host/port reachability
  - checks MinIO endpoint reachability
- cloud mode:
  - validates required `SNOWFLAKE_*` environment variables are set

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
```

### `_dataset_layout.py`

Shared dataset contract adapter for Stage 3 and Stage 4.

Responsibilities:

- reads governed dataset order and CSV field definitions from `synthetic_generator/contracts.py`
- classifies core vs dimension datasets
- provides reusable naming/path helpers for Bronze table and stage paths

### `generate_layer_assets.py`

Generates dataset-level SQL and Spark job assets for selected layers (`bronze`, `silver`, `gold`).

Outputs:

- per-dataset SQL under `../sql/<layer>/ddl/` and `../sql/<layer>/dml/`
- per-layer ordered index files:
  - `../sql/<layer>/_index_ordered.txt`
  - `../sql/<layer>/dataset_index.json`
- optional per-dataset Spark job templates under `../spark/<layer>/jobs/`

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/generate_layer_assets.py --layers bronze --clean --emit-spark-jobs
```

### `generate_bronze_assets.py`

Compatibility wrapper that delegates to `generate_layer_assets.py --layers bronze`.

### `load_one_dataset.py`

Builds a single-dataset `COPY INTO` statement for one batch id.

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_one_dataset.py --batch-id 20260501_010203 --dataset payment_instruction --write-sql
```

### `load_batch.py`

Builds a full batch SQL bundle by reading `data/batches/<batch_id>/control/manifest.json` and emitting ordered `COPY INTO` statements for all discovered datasets.

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/load_batch.py --batch-id 20260501_010203
```

### `run_dataset_spark_job.py`

Runs one per-dataset Spark job script with required contract args:

- `--layer`
- `--dataset`
- `--batch-id`
- `--profile`

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_dataset_spark_job.py --layer bronze --dataset payment_instruction --batch-id 20260501_010203 --profile local
```

### `run_local_hive_bronze_check.py`

Runs a local Hive validation for one Bronze dataset:

- prepares local stage file from `data/batches/<batch_id>/landing/csv/<dataset>.csv`
- generates runtime Hive DDL/DML SQL files
- optionally executes DDL, DML, and row-count verify query via `beeline`

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/run_local_hive_bronze_check.py --dataset region --batch-id 20260501_010203 --execute
```

Optional flags:

- `--batch-id latest` to auto-pick newest batch
- `--dml-mode explain` for fast DML syntax/plan validation (default)
- `--dml-mode execute` for full physical DML execution

### `validate_load.py`

Builds batch-specific validation SQL inputs from the manifest for Stage 6 checks.

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/validate_load.py --batch-id latest --emit-row-count-sql
```

Output:

- `../sql/runtime/validation/bronze_row_count_reconciliation_<batch_id>.sql`

### `benchmark_load.py`

Runs repeatable Bronze dataset job benchmarks and writes runtime performance artifacts.

Outputs:

- `../sql/runtime/performance/benchmark_<batch_id>_<timestamp>.json`
- `../sql/runtime/performance/benchmark_<batch_id>_<timestamp>.md`

Example:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/benchmark_load.py --batch-id latest --profile local --runs 1 --spark-submit-cmd python
```

## Expected Workflow

1. Set profile and secrets (`PHASE3_ENV`, `.env.local` or `.env.cloud`)
2. Run `print_runtime_config.py`
3. Run `check_connectivity.py`
4. Generate dataset-level assets with `generate_layer_assets.py`
5. Apply setup SQL in `../sql/ddl/`, `../sql/staging/`, and `../sql/bronze/`
6. Build ingestion SQL with `load_one_dataset.py` or `load_batch.py`
7. Run per-dataset Spark jobs manually with `run_dataset_spark_job.py`
8. Validate local Hive DDL/DML with `run_local_hive_bronze_check.py` or Airflow local Bronze DAG
9. Generate/execute Bronze validation SQL with `validate_load.py` and files in `../sql/validation/`
10. Capture baseline performance with `benchmark_load.py`
