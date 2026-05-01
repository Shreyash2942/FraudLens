# Phase 3 Warehouse Assets

This directory contains executable assets for Phase 3 (`#39` to `#46`) with local-first and cloud-ready configuration patterns.

## Stage 1 and Stage 2 Scope

- Stage 1 (`#39`): environment config and access checks
- Stage 2 (`#40`): warehouse structure and naming standards

## Directory Layout

- `config/` environment profile files
- `scripts/` executable helpers (connectivity and config inspection)
- `sql/ddl/` database/schema and role/grant DDL
- `sql/naming/` naming standard reference SQL

## Scripts

The `scripts/` folder is the Stage 1 execution helper layer. It validates runtime configuration before applying warehouse SQL.

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

Example usage:

```powershell
py warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py local
py warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py
```

## Execution Order

1. review and adapt `config/local.yml` or `config/cloud.yml`
2. run `scripts/print_runtime_config.py` to confirm resolved values
3. run `scripts/check_connectivity.py` for environment validation
4. apply DDL files in `sql/ddl/`
5. review naming reference in `sql/naming/`
