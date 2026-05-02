# Phase 3 Warehouse Assets

This directory contains executable assets for Phase 3 (`#39` to `#46`) with local-first and cloud-ready configuration patterns.

## Stage 1 to Stage 4 Scope

- Stage 1 (`#39`): environment config and access checks
- Stage 2 (`#40`): warehouse structure and naming standards
- Stage 3 (`#41`): Bronze table creation assets
- Stage 4 (`#42`): MinIO ingestion SQL patterns and execution helpers

## Directory Layout

- `config/` environment profile files
- `scripts/` executable helpers (connectivity, SQL generation, load SQL builders)
- `sql/ddl/` database/schema, role/grant, and Bronze DDL
- `sql/staging/` file format and external stage SQL
- `sql/dml/` batch ingestion `COPY INTO` SQL bundles
- `sql/naming/` naming standard reference SQL

## Scripts

The `scripts/` folder contains reusable execution helpers through Stage 4.

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
  - generates Bronze DDL and ingestion SQL from governed dataset contracts
- `load_one_dataset.py`
  - emits one dataset-specific `COPY INTO` statement for a batch id
- `load_batch.py`
  - emits ordered `COPY INTO` statements for all datasets in a batch manifest

Example usage:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py local
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
```

## Execution Order

1. review and adapt `config/local.yml` or `config/cloud.yml`
2. run `scripts/print_runtime_config.py` to confirm resolved values
3. run `scripts/check_connectivity.py` for environment validation
4. generate Stage 3/4 SQL with `scripts/generate_bronze_assets.py`
5. apply DDL and staging files in `sql/ddl/` and `sql/staging/`
6. execute load SQL from `sql/dml/` or build runtime SQL with `scripts/load_batch.py`
