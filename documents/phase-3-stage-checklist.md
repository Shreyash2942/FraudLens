# Phase 3 Stage Checklist

This checklist tracks implementation progress for the Phase 3 milestone and keeps GitHub issue execution aligned with repository assets.

## Stage 1 (`#39`) Environment And Access

- [ ] `warehouse/snowflake-warehouse-setup/config/local.yml` finalized
- [ ] `warehouse/snowflake-warehouse-setup/config/cloud.yml` finalized
- [ ] secrets contract prepared from `warehouse/snowflake-warehouse-setup/config/env.example`
- [ ] `warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py` validated
- [ ] `warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py` passing in chosen environment

## Stage 2 (`#40`) Structure And Naming Standards

- [ ] `warehouse/snowflake-warehouse-setup/sql/ddl/create_database_and_schemas.sql` reviewed and executed
- [ ] `warehouse/snowflake-warehouse-setup/sql/ddl/create_roles_and_grants.sql` reviewed and executed
- [ ] naming conventions approved from `warehouse/snowflake-warehouse-setup/sql/naming/naming_convention_reference.sql`
- [ ] structure and naming references documented in Phase 3 runbook

## Stage 3 (`#41`) Bronze Tables

- [x] Bronze DDL scripts created
- [ ] Bronze tables deployed

## Stage 4 (`#43`) Staging And File Formats

- [x] file format SQL created
- [x] stage SQL created

## Stage 5 (`#42`) Ingestion From MinIO

- [x] batch load scripts created
- [ ] first dataset loaded end-to-end

## Stage 6 (`#44`) Validation

- [ ] row-count reconciliation checks added
- [ ] null/key/domain checks added

## Stage 7 (`#45`) Initial Performance

- [ ] baseline load benchmark captured
- [ ] first tuning notes documented

## Stage 8 (`#46`) Documentation

- [ ] setup runbook completed
- [ ] troubleshooting notes completed


