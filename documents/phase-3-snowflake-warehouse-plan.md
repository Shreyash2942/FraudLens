# Phase 3 Snowflake Warehouse Plan

## Purpose

Phase 3 initializes Snowflake as the analytical warehouse foundation and implements the Bronze layer for raw ingestion from object storage.

This plan converts the milestone into an execution-ready sequence so implementation can proceed with clear scope, acceptance checks, and handoff artifacts.

## Milestone Summary

- phase: `Phase 3 - Snowflake Warehouse Setup`
- goal: create a fully configured Snowflake environment with Bronze data loaded from MinIO-backed batch outputs
- issue set: `#39` to `#46`

## Scope

In scope:

- Snowflake access setup and environment validation
- database and schema structure (`BRONZE`, `SILVER`, `GOLD`)
- naming and governance standards for warehouse objects
- Bronze table creation for raw landing data
- ingestion flow from object storage to Snowflake
- staging and file format patterns
- data-load validation and initial performance baseline
- operator-facing setup documentation

Out of scope for Phase 3:

- full Silver/Gold transformation modeling
- business KPI layer
- production orchestration and scheduling

## Design Assumptions

- Snowflake remains the target warehouse platform.
- Synthetic data already exists under `data/batches/<batch_id>/`.
- MinIO remains the local object store in the Data-Lab runtime.
- Bronze should preserve raw shape with minimal transformation.

## Environment Strategy (Local First, Cloud Ready)

To control cost in early Phase 3 while preserving cloud parity:

- local runtime executes ingestion and validation against local stack components
- the same repository script structure supports Snowflake cloud cutover later
- environment-specific behavior is configuration-driven, not hardcoded

Configuration model:

- non-secret environment profiles in YAML:
  - `config/environments/local.yml`
  - `config/environments/cloud.yml`
- secrets in local env files (not committed):
  - `.env.local`
  - `.env.cloud`

Key rule:

- use one logical pipeline contract with two execution targets (`local` and `cloud`)
- keep dataset names, object names, and validation rules consistent across both targets

## Workstream Plan

### Workstream 1 - Setup Snowflake Environment And Access (`#39`)

Deliver:

- account connectivity check (`snowsql` or Snowflake Python connector)
- role, user, warehouse, and authentication setup guidance
- local secret contract documented (no credentials committed)

Acceptance focus:

- authenticated connection succeeds
- active role and warehouse can run `SELECT 1`

### Workstream 2 - Define Warehouse Structure And Naming Standards (`#40`)

Deliver:

- database and schema naming convention
- object naming standards for tables, stages, file formats, and pipes
- required metadata columns for Bronze auditability

Acceptance focus:

- naming conventions are documented and used consistently in SQL

### Workstream 3 - Create Bronze Layer Tables (`#41`)

Deliver:

- Bronze tables for Phase 2 exported datasets
- raw-compatible types and load-friendly defaults
- load audit columns (for example: `ingestion_batch_id`, `ingested_at_utc`, `source_file_name`)

Acceptance focus:

- tables exist and are queryable
- at least one batch is loadable into each required Bronze table set

### Workstream 4 - Configure Data Ingestion From MinIO (`#42`)

Deliver:

- ingestion path from MinIO-backed files into Snowflake Bronze
- repeatable load command pattern by batch

Implementation note:

- keep two supported ingestion strategies:
  - `Path A`: stage files into Snowflake internal stage and `COPY INTO` Bronze
  - `Path B`: external-stage approach only where account/network policy supports the object-store endpoint

Acceptance focus:

- ingestion can be executed repeatedly without manual ad-hoc edits

### Workstream 5 - Implement Staging And File Format Handling (`#43`)

Deliver:

- standard CSV file format object(s)
- stage naming and folder conventions mapped to FraudLens batch layout
- `COPY INTO` templates for dataset groups

Acceptance focus:

- file format handles header, delimiter, null, and quote behavior correctly
- staged files are visible and loadable with deterministic SQL patterns

### Workstream 6 - Validate Data Load And Integrity (`#44`)

Deliver:

- row-count validation checks per dataset
- basic null/key sanity checks on Bronze loads
- load summary report script or SQL bundle

Acceptance focus:

- loaded counts align with `manifest.json` row counts
- no critical load failures in required Bronze datasets

### Workstream 7 - Optimize Initial Load Performance (`#45`)

Deliver:

- initial warehouse sizing guidance for dev workloads
- batch-wise load strategy and parallelization notes
- baseline timing capture for first complete load

Acceptance focus:

- load completes within a practical dev-time target
- documented tuning knobs exist for reruns

### Workstream 8 - Document Warehouse Setup (`#46`)

Deliver:

- operator runbook for end-to-end setup and first load
- troubleshooting section for connectivity, stage access, and `COPY` errors
- references to standards and contracts used by Bronze loads

Acceptance focus:

- a new developer can reproduce environment setup and load without tribal knowledge

## Script And Asset Plan (Required For Implementation)

This section defines the concrete script inventory to be created in Phase 3 so implementation is reusable in both local and cloud modes.

### Directory Blueprint

- `warehouse/snowflake-warehouse-setup/sql/ddl/`
- `warehouse/snowflake-warehouse-setup/sql/dml/`
- `warehouse/snowflake-warehouse-setup/sql/staging/`
- `warehouse/snowflake-warehouse-setup/sql/validation/`
- `warehouse/snowflake-warehouse-setup/scripts/`
- `warehouse/snowflake-warehouse-setup/spark/`
- `warehouse/snowflake-warehouse-setup/config/`

### 1) Environment And Access Scripts (`#39`)

- `warehouse/snowflake-warehouse-setup/config/local.yml`
- `warehouse/snowflake-warehouse-setup/config/cloud.yml`
- `warehouse/snowflake-warehouse-setup/scripts/check_connectivity.py`
- `warehouse/snowflake-warehouse-setup/scripts/print_runtime_config.py`

Purpose:

- validate config resolution
- verify account/role/warehouse reachability (cloud mode)
- verify local runtime dependency endpoints (local mode)

### 2) Naming And Structure Scripts (`#40`)

- `warehouse/snowflake-warehouse-setup/sql/ddl/create_database_and_schemas.sql`
- `warehouse/snowflake-warehouse-setup/sql/ddl/create_roles_and_grants.sql`
- `warehouse/snowflake-warehouse-setup/sql/ddl/naming_convention_reference.sql` (commented reference SQL)

Purpose:

- enforce consistent database/schema/object naming
- standardize grants and role usage patterns

### 3) Bronze DDL Scripts (`#41`)

- `warehouse/snowflake-warehouse-setup/sql/ddl/10_create_bronze_tables_core.sql`
- `warehouse/snowflake-warehouse-setup/sql/ddl/11_create_bronze_tables_dimensions.sql`
- `warehouse/snowflake-warehouse-setup/sql/ddl/12_create_bronze_audit_tables.sql`

Purpose:

- create Bronze tables for all governed Phase 2 datasets
- include audit metadata columns and load-traceability columns

### 4) Staging And File Format Scripts (`#43`)

- `warehouse/snowflake-warehouse-setup/sql/staging/20_create_file_formats.sql`
- `warehouse/snowflake-warehouse-setup/sql/staging/21_create_stages.sql`
- `warehouse/snowflake-warehouse-setup/sql/staging/22_list_stage_files.sql`

Purpose:

- standardize CSV file format handling
- define stage objects and folder/path conventions

### 5) Ingestion Scripts (MinIO + Load) (`#42`)

Cloud/Snowflake-oriented SQL:

- `warehouse/snowflake-warehouse-setup/sql/dml/30_copy_into_bronze_core.sql`
- `warehouse/snowflake-warehouse-setup/sql/dml/31_copy_into_bronze_dimensions.sql`

Local execution helpers:

- `warehouse/snowflake-warehouse-setup/scripts/load_batch.py`
- `warehouse/snowflake-warehouse-setup/scripts/load_one_dataset.py`
- `warehouse/snowflake-warehouse-setup/scripts/retry_failed_loads.py`

Spark local-ingestion support:

- `warehouse/snowflake-warehouse-setup/spark/bronze_ingest_job.py`
- `warehouse/snowflake-warehouse-setup/spark/bronze_manifest_loader.py`

Purpose:

- load MinIO-backed files into Bronze targets with batch-aware execution
- support first local-only execution while keeping cloud SQL artifacts ready

### 6) Validation Scripts (`#44`)

- `warehouse/snowflake-warehouse-setup/sql/validation/40_row_count_reconciliation.sql`
- `warehouse/snowflake-warehouse-setup/sql/validation/41_null_and_key_checks.sql`
- `warehouse/snowflake-warehouse-setup/sql/validation/42_domain_sanity_checks.sql`
- `warehouse/snowflake-warehouse-setup/scripts/validate_load.py`

Purpose:

- reconcile loaded rows against `manifest.json`
- enforce essential quality and integrity checks

### 7) Performance Baseline Scripts (`#45`)

- `warehouse/snowflake-warehouse-setup/scripts/benchmark_load.py`
- `warehouse/snowflake-warehouse-setup/sql/validation/50_load_performance_report.sql`

Purpose:

- capture baseline elapsed times and throughput
- compare runs by dataset and batch

### 8) Documentation And Ops Assets (`#46`)

- `documents/phase-3-warehouse-setup-runbook.md`
- `documents/phase-3-troubleshooting.md`

Purpose:

- provide reproducible setup and run instructions
- capture common failure patterns and fixes

## Execution Order

1. Access and environment validation (`#39`)
2. Naming and structural standards (`#40`)
3. Bronze DDL foundation (`#41`)
4. Stage and file-format setup (`#43`)
5. MinIO-to-Snowflake ingestion flow (`#42`)
6. Validation checks and reconciliation (`#44`)
7. Initial performance tuning (`#45`)
8. Finalized setup and runbook documentation (`#46`)

## Definition Of Done Mapping

- Snowflake environment accessible and configured: `#39`
- database and schemas created: `#40` + `#41`
- Bronze tables created and populated: `#41` + `#42` + `#43`
- data successfully loaded from MinIO path: `#42` + `#43`
- data integrity validated: `#44`
- basic performance considerations applied: `#45`
- setup documentation complete: `#46`

## Deliverable Artifacts For Phase 3

- warehouse SQL assets under `warehouse/` (DDL, stages, file formats, load SQL)
- Spark ingestion helpers for local-first execution
- environment profiles for local and cloud execution modes
- validation SQL/check outputs for load reconciliation
- Phase 3 setup runbook under `documents/`

## Risks And Mitigations

- Risk: object-store connectivity constraints between Snowflake and local MinIO.
  - Mitigation: keep internal-stage load path as default-safe fallback.
- Risk: schema drift between generated CSVs and Bronze DDL.
  - Mitigation: tie table definitions and validation checks to current generator manifest and dataset catalog.
- Risk: performance regressions during full-batch loads.
  - Mitigation: capture baseline timings and parameterized load settings early.

## Branch And Delivery Strategy

- implement Phase 3 on `snowflake-warehouse-setup`
- merge from `main` before starting each major workstream
- keep one focused PR per workstream or tightly related workstream pair


