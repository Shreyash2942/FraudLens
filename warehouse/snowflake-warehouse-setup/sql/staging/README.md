# Phase 3 Staging SQL

This folder contains Stage 4 (`#42`) SQL assets for MinIO-to-Snowflake staging setup.

## Files

- `create_csv_file_format.sql`
  - standard Bronze CSV load options (header skip, null handling, quote handling)
- `create_minio_external_stage.sql`
  - S3-compatible external stage template for MinIO
  - includes placeholder endpoint/credential values that should be replaced from local secrets

## Execution Notes

- run after database/schema setup and role grants
- create file format before creating the external stage
- validate stage access with a `LIST @<stage_name>;` query before running COPY statements
