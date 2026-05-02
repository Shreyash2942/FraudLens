-- Scaffold-only GOLD DML for dataset: device_profile
-- TODO: replace placeholder select with curated transform logic.
SET BATCH_ID = '<replace_with_batch_id>';

INSERT INTO FRAUDLENS.GOLD.GOLD_DEVICE_PROFILE (
  PLACEHOLDER_RECORD_ID,
  SOURCE_BATCH_ID
)
SELECT
  'TODO_RECORD_ID',
  $BATCH_ID
FROM FRAUDLENS.SILVER.SILVER_DEVICE_PROFILE
WHERE INGESTION_BATCH_ID = $BATCH_ID
LIMIT 1;
