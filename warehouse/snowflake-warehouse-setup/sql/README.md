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
- `validation/`: reconciliation, quality, and performance report SQL (`#44`, `#45`)
  - `bronze_row_count_reconciliation.sql`
  - `bronze_null_key_checks.sql`
  - `bronze_domain_sanity_checks.sql`
  - `bronze_load_performance_report.sql`
