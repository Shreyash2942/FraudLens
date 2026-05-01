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

## Execution Order

1. review and adapt `config/local.yml` or `config/cloud.yml`
2. run `scripts/print_runtime_config.py` to confirm resolved values
3. run `scripts/check_connectivity.py` for environment validation
4. apply DDL files in `sql/ddl/`
5. review naming reference in `sql/naming/`
