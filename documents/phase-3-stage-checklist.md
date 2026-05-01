# Phase 3 Stage Checklist

This checklist tracks implementation progress for the Phase 3 milestone and keeps GitHub issue execution aligned with repository assets.

## Stage 1 (`#39`) Environment And Access

- [ ] `warehouse/phase3/config/local.yml` finalized
- [ ] `warehouse/phase3/config/cloud.yml` finalized
- [ ] secrets contract prepared from `warehouse/phase3/config/env.example`
- [ ] `warehouse/phase3/scripts/print_runtime_config.py` validated
- [ ] `warehouse/phase3/scripts/check_connectivity.py` passing in chosen environment

## Stage 2 (`#40`) Structure And Naming Standards

- [ ] `warehouse/phase3/sql/ddl/00_create_database_and_schemas.sql` reviewed and executed
- [ ] `warehouse/phase3/sql/ddl/01_create_roles_and_grants.sql` reviewed and executed
- [ ] naming conventions approved from `warehouse/phase3/sql/naming/02_naming_convention_reference.sql`
- [ ] structure and naming references documented in Phase 3 runbook

## Stage 3 (`#41`) Bronze Tables

- [ ] Bronze DDL scripts created
- [ ] Bronze tables deployed

## Stage 4 (`#43`) Staging And File Formats

- [ ] file format SQL created
- [ ] stage SQL created

## Stage 5 (`#42`) Ingestion From MinIO

- [ ] batch load scripts created
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
