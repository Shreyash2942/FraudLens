# Phase 3 DDL

DDL scripts for Stage 2 (`#40`) and later warehouse object creation.

## Files

- `create_database_and_schemas.sql`
  - creates `FRAUDLENS` database and `BRONZE`, `SILVER`, `GOLD` schemas
- `create_roles_and_grants.sql`
  - creates baseline engineering role and grants required usage/create privileges
- `create_bronze_tables_dimensions.sql`
  - creates Bronze dimension landing tables from governed synthetic dataset contract
- `create_bronze_tables_core.sql`
  - creates Bronze core/fraud operation landing tables from governed synthetic dataset contract

## Execution Notes

- run with a privileged Snowflake role
- execute `create_database_and_schemas.sql` before `create_roles_and_grants.sql`
- execute Bronze table scripts after schema creation
- keep scripts idempotent (`CREATE ... IF NOT EXISTS`)
