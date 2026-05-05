-- Phase 3 Stage 6 (#44): Bronze row-count reconciliation template
-- Recommended: generate a batch-specific executable SQL with
-- py warehouse/snowflake-warehouse-setup/scripts/validate_load.py --batch-id <batch_id> --emit-row-count-sql
--
-- Replace <expected_rows> placeholders using data/batches/<batch_id>/control/manifest.json

WITH expected_rows AS (
  SELECT column1::VARCHAR AS dataset_name, column2::NUMBER AS expected_row_count
  FROM VALUES
    ('reference_data_catalog', <REFERENCE_DATA_CATALOG_EXPECTED_ROWS>),
    ('calendar_day', <CALENDAR_DAY_EXPECTED_ROWS>),
    ('region', <REGION_EXPECTED_ROWS>),
    ('branch_territory', <BRANCH_TERRITORY_EXPECTED_ROWS>),
    ('branch_location', <BRANCH_LOCATION_EXPECTED_ROWS>),
    ('business_unit', <BUSINESS_UNIT_EXPECTED_ROWS>),
    ('analyst_team', <ANALYST_TEAM_EXPECTED_ROWS>),
    ('party', <PARTY_EXPECTED_ROWS>),
    ('party_org_assignment', <PARTY_ORG_ASSIGNMENT_EXPECTED_ROWS>),
    ('deposit_account', <DEPOSIT_ACCOUNT_EXPECTED_ROWS>),
    ('payment_card', <PAYMENT_CARD_EXPECTED_ROWS>),
    ('device_profile', <DEVICE_PROFILE_EXPECTED_ROWS>),
    ('channel_event', <CHANNEL_EVENT_EXPECTED_ROWS>),
    ('payment_instruction', <PAYMENT_INSTRUCTION_EXPECTED_ROWS>),
    ('payment_transaction', <PAYMENT_TRANSACTION_EXPECTED_ROWS>),
    ('risk_signal', <RISK_SIGNAL_EXPECTED_ROWS>),
    ('fraud_alert', <FRAUD_ALERT_EXPECTED_ROWS>),
    ('fraud_case', <FRAUD_CASE_EXPECTED_ROWS>),
    ('investigation_event', <INVESTIGATION_EVENT_EXPECTED_ROWS>),
    ('decision_record', <DECISION_RECORD_EXPECTED_ROWS>),
    ('case_disposition', <CASE_DISPOSITION_EXPECTED_ROWS>)
),
actual_rows AS (
  SELECT 'reference_data_catalog' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'calendar_day' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'region' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'branch_territory' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'branch_location' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'business_unit' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'analyst_team' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'party' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'party_org_assignment' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'deposit_account' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'payment_card' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'device_profile' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'channel_event' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'payment_instruction' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'payment_transaction' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'risk_signal' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'fraud_alert' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'fraud_case' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'investigation_event' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'decision_record' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'case_disposition' AS dataset_name, COUNT(*) AS actual_row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
)
SELECT
  e.dataset_name,
  e.expected_row_count,
  COALESCE(a.actual_row_count, 0) AS actual_row_count,
  COALESCE(a.actual_row_count, 0) - e.expected_row_count AS row_delta,
  CASE
    WHEN COALESCE(a.actual_row_count, 0) = e.expected_row_count THEN 'pass'
    ELSE 'fail'
  END AS check_status
FROM expected_rows e
LEFT JOIN actual_rows a ON a.dataset_name = e.dataset_name
ORDER BY e.dataset_name;
