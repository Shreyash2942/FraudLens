-- Stage 4 (#42): MinIO S3-compatible external stage template
-- Replace placeholder credentials/endpoints with secure values from your runtime secrets.

SET MINIO_ENDPOINT = '<minio-host:port>';
SET MINIO_BUCKET = '<bucket-name>';
SET MINIO_PREFIX = '<prefix-root>'; -- example: fraudlens/synthetic_data/batches
SET MINIO_ACCESS_KEY = '<access-key>';
SET MINIO_SECRET_KEY = '<secret-key>';

CREATE STAGE IF NOT EXISTS FRAUDLENS.BRONZE.STG_BRONZE_MINIO_RAW
  URL = 's3compat://<bucket-name>/<prefix-root>/'
  ENDPOINT = '<minio-host:port>'
  CREDENTIALS = (AWS_KEY_ID = '<access-key>' AWS_SECRET_KEY = '<secret-key>')
  FILE_FORMAT = FRAUDLENS.BRONZE.FF_BRONZE_CSV_V1;
