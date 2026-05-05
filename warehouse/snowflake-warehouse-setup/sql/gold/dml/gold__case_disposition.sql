-- Scaffold-only GOLD DML for dataset: case_disposition
-- TODO: replace placeholder select with curated transform logic.
SET BATCH_ID = '<replace_with_batch_id>';

INSERT INTO FRAUDLENS.GOLD.GOLD_CASE_DISPOSITION (
  PLACEHOLDER_RECORD_ID,
  SOURCE_BATCH_ID
)
SELECT
  'TODO_RECORD_ID',
  $BATCH_ID
FROM FRAUDLENS.SILVER.SILVER_CASE_DISPOSITION
WHERE INGESTION_BATCH_ID = $BATCH_ID
LIMIT 1;
