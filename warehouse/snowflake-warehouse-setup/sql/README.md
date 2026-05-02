# Phase 3 SQL

This folder contains SQL assets for Snowflake warehouse setup and loading patterns.

## Subfolders

- `bronze/`: dataset-level Bronze SQL (`ddl/` + `dml/`)
- `silver/`: dataset-level Silver scaffold SQL (`ddl/` + `dml/`)
- `gold/`: dataset-level Gold scaffold SQL (`ddl/` + `dml/`)
- `ddl/`: shared/admin DDL (database, schema, role, grants)
- `staging/`: stage and file-format SQL
- `dml/`: legacy grouped Bronze load SQL (to be retired after migration)
- `naming/`: naming and standardization reference SQL
- `validation/`: reconciliation and quality SQL (future stage)
