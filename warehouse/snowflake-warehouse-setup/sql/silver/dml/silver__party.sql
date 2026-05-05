-- Scaffold-only SILVER DML for dataset: party
-- TODO: replace placeholder select with curated transform logic.
SET BATCH_ID = '<replace_with_batch_id>';

INSERT INTO FRAUDLENS.SILVER.SILVER_PARTY (
  PLACEHOLDER_RECORD_ID,
  SOURCE_BATCH_ID
)
SELECT
  'TODO_RECORD_ID',
  $BATCH_ID
FROM FRAUDLENS.BRONZE.BRONZE_PARTY
WHERE INGESTION_BATCH_ID = $BATCH_ID
LIMIT 1;
