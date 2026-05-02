-- Scaffold-only GOLD DML for dataset: fraud_case
-- TODO: replace placeholder select with curated transform logic.
SET BATCH_ID = '<replace_with_batch_id>';

INSERT INTO FRAUDLENS.GOLD.GOLD_FRAUD_CASE (
  PLACEHOLDER_RECORD_ID,
  SOURCE_BATCH_ID
)
SELECT
  'TODO_RECORD_ID',
  $BATCH_ID
FROM FRAUDLENS.SILVER.SILVER_FRAUD_CASE
WHERE INGESTION_BATCH_ID = $BATCH_ID
LIMIT 1;
