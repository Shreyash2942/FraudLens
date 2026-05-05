-- Phase 3 Stage 2 (#40): naming standard reference
-- This file is intentionally a reference artifact to keep naming decisions executable and reviewable.

-- Core naming pattern:
--   <LAYER>_<DOMAIN>_<ENTITY>
-- Example:
--   BRONZE_PAYMENTS_PAYMENT_INSTRUCTION

-- Supporting object naming:
--   stage:      STG_<LAYER>_<SOURCE>
--   file format: FF_<FORMAT>_<VERSION>
--   pipe/task:  P_<ACTION>_<TARGET>

-- Example object definitions:
-- CREATE OR REPLACE STAGE FRAUDLENS.BRONZE.STG_BRONZE_MINIO;
-- CREATE OR REPLACE FILE FORMAT FRAUDLENS.BRONZE.FF_CSV_V1
--   TYPE = CSV
--   SKIP_HEADER = 1
--   FIELD_DELIMITER = ','
--   FIELD_OPTIONALLY_ENCLOSED_BY = '\"'
--   NULL_IF = ('', 'NULL', 'null');

-- Recommended metadata columns for Bronze tables:
--   INGESTION_BATCH_ID STRING
--   SOURCE_FILE_NAME   STRING
--   INGESTED_AT_UTC    TIMESTAMP_NTZ
