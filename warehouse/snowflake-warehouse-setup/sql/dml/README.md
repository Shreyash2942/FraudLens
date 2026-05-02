# Phase 3 DML SQL

This folder contains Stage 4 (`#42`) Bronze ingestion SQL bundles.

## Files

- `copy_into_bronze_dimensions.sql`
  - batch-aware `COPY INTO` statements for dimension datasets
- `copy_into_bronze_core.sql`
  - batch-aware `COPY INTO` statements for core banking/fraud datasets

## Execution Notes

- set `BATCH_ID` at the top of each script before running
- run dimension load first, then core load
- statements include Bronze audit fields:
  - `INGESTION_BATCH_ID`
  - `SOURCE_FILE_NAME`
  - `INGESTED_AT_UTC`
