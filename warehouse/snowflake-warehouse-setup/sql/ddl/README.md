# Phase 3 DDL

DDL scripts for Stage 2 (`#40`) and later warehouse object creation.

## Files

- `create_database_and_schemas.sql`
  - creates `FRAUDLENS` database and `BRONZE`, `SILVER`, `GOLD` schemas
- `create_roles_and_grants.sql`
  - creates baseline engineering role and grants required usage/create privileges

## Execution Notes

- run with a privileged Snowflake role
- execute `create_database_and_schemas.sql` before `create_roles_and_grants.sql`
- keep scripts idempotent (`CREATE ... IF NOT EXISTS`)
