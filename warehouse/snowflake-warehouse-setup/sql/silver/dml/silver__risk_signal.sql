-- Scaffold-only SILVER DML for dataset: risk_signal
-- TODO: replace placeholder select with curated transform logic.
SET BATCH_ID = '<replace_with_batch_id>';

INSERT INTO FRAUDLENS.SILVER.SILVER_RISK_SIGNAL (
  PLACEHOLDER_RECORD_ID,
  SOURCE_BATCH_ID
)
SELECT
  'TODO_RECORD_ID',
  $BATCH_ID
FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL
WHERE INGESTION_BATCH_ID = $BATCH_ID
LIMIT 1;
