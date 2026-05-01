# Phase 3 Scripts

This folder contains Stage 1 runtime helper scripts for Phase 3 (`#39`) environment setup and validation.

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

## Expected Workflow

1. Set profile and secrets (`PHASE3_ENV`, `.env.local` or `.env.cloud`)
2. Run `print_runtime_config.py`
3. Run `check_connectivity.py`
4. Proceed with SQL setup in `../sql/ddl/`
