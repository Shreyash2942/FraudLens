# Warehouse Layer Foundation (Phase 3)

Status date: `2026-05-25`
Milestone scope: `#38` with sub-issues `#39`-`#46`

## Purpose

This document consolidates Phase 3 planning, execution sequencing, operations runbooks, and readiness guidance into one warehouse implementation artifact.

## Primary Phase File

Use this as the primary Phase 3 review and handoff file in `documents/`.

## Scope Consolidated

- `#39` Setup Snowflake environment and access
- `#40` Define warehouse structure and naming standards
- `#41` Create Bronze layer tables
- `#42` Configure data ingestion from MinIO
- `#43` Implement staging and file format handling
- `#44` Validate data load and integrity
- `#45` Optimize initial load performance
- `#46` Document warehouse setup

## Executive Outcome

Phase 3 established the warehouse loading foundation and operational pattern for Bronze ingestion:

- local-first Spark/Hive validation path preserved for cost control
- Snowflake-targeted structure, naming, staging, and loading plan defined
- Bronze DDL and ingestion sequencing aligned to governed dataset contracts
- runbooks and troubleshooting guidance created for operators
- validation and performance baseline approach defined for repeatable execution

## Architecture and Environment Strategy

- target analytics platform remains Snowflake
- local Spark/Hive path is used as the lower-cost development and early validation surrogate
- generated Phase 2 batches are promoted through staged load assets and validation steps
- scripts and SQL assets are organized to support staged handoff from local validation to Snowflake execution

## Workstream Delivery Map

### Workstreams 1-3 (`#39` to `#41`)

- environment/profile setup and connectivity checks
- warehouse naming and schema structure standardization
- Bronze table creation aligned to governed contracts

### Workstreams 4-6 (`#42` to `#44`)

- staging/file-format handling and ingestion flow from MinIO
- load execution controls and manifest-driven batch handling
- load validation checks for row counts, structure, and integrity

### Workstreams 7-8 (`#45` to `#46`)

- baseline performance capture for initial load patterns
- operator-facing setup, execution, and troubleshooting documentation

## Operational Runbook Summary

### Standard Execution Sequence

1. validate runtime profile and service reachability
2. generate layer assets and SQL bundles
3. apply shared setup SQL and stage configuration
4. execute batch load SQL and Bronze jobs
5. run validation queries and checks
6. capture performance baseline and issue evidence
7. complete handoff checklist

### Layer Orchestration Coverage

- per-dataset local Spark execution path
- Airflow DAG path for orchestrated runs
- Bronze SQL execution path for warehouse-aligned runs

## Troubleshooting Baseline

Primary failure classes and first-response handling are consolidated for:

- connectivity and credential issues
- missing batch manifests
- dataset contract mismatch errors
- stage/COPY execution failures
- Spark runtime failures
- validation mismatches and benchmark failures

## Delivery Governance

- issue-to-commit traceability maintained in phase commit summary
- stage checklist aligns each workstream to execution gates
- standards and contracts are treated as blocking controls, not advisory guidance

## Consolidation Note

Earlier Phase 3 working documents were consolidated into this file and are not retained separately
in the root `documents/` directory.

## Reviewer Notes

Use this as the only retained Phase 3 document in `documents/`.
