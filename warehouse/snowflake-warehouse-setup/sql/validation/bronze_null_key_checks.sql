-- Phase 3 Stage 6 (#44): Bronze null and key checks
-- Parameter: :batch_id

WITH checks AS (
  SELECT 'primary_key_null' AS check_type, 'calendar_day' AS dataset_name, 'calendar_date' AS column_name, COUNT_IF(CALENDAR_DATE IS NULL OR TRIM(CALENDAR_DATE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'calendar_day' AS dataset_name, 'calendar_date' AS column_name, GREATEST(COUNT_IF(CALENDAR_DATE IS NOT NULL) - COUNT(DISTINCT CALENDAR_DATE), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'region' AS dataset_name, 'region_id' AS column_name, COUNT_IF(REGION_ID IS NULL OR TRIM(REGION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'region' AS dataset_name, 'region_id' AS column_name, GREATEST(COUNT_IF(REGION_ID IS NOT NULL) - COUNT(DISTINCT REGION_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'branch_territory' AS dataset_name, 'branch_territory_id' AS column_name, COUNT_IF(BRANCH_TERRITORY_ID IS NULL OR TRIM(BRANCH_TERRITORY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'branch_territory' AS dataset_name, 'branch_territory_id' AS column_name, GREATEST(COUNT_IF(BRANCH_TERRITORY_ID IS NOT NULL) - COUNT(DISTINCT BRANCH_TERRITORY_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'branch_location' AS dataset_name, 'branch_id' AS column_name, COUNT_IF(BRANCH_ID IS NULL OR TRIM(BRANCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'branch_location' AS dataset_name, 'branch_id' AS column_name, GREATEST(COUNT_IF(BRANCH_ID IS NOT NULL) - COUNT(DISTINCT BRANCH_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'business_unit' AS dataset_name, 'business_unit_id' AS column_name, COUNT_IF(BUSINESS_UNIT_ID IS NULL OR TRIM(BUSINESS_UNIT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'business_unit' AS dataset_name, 'business_unit_id' AS column_name, GREATEST(COUNT_IF(BUSINESS_UNIT_ID IS NOT NULL) - COUNT(DISTINCT BUSINESS_UNIT_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'analyst_team' AS dataset_name, 'analyst_team_id' AS column_name, COUNT_IF(ANALYST_TEAM_ID IS NULL OR TRIM(ANALYST_TEAM_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'analyst_team' AS dataset_name, 'analyst_team_id' AS column_name, GREATEST(COUNT_IF(ANALYST_TEAM_ID IS NOT NULL) - COUNT(DISTINCT ANALYST_TEAM_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'party' AS dataset_name, 'party_id' AS column_name, COUNT_IF(PARTY_ID IS NULL OR TRIM(PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'party' AS dataset_name, 'party_id' AS column_name, GREATEST(COUNT_IF(PARTY_ID IS NOT NULL) - COUNT(DISTINCT PARTY_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'party_org_assignment' AS dataset_name, 'party_org_assignment_id' AS column_name, COUNT_IF(PARTY_ORG_ASSIGNMENT_ID IS NULL OR TRIM(PARTY_ORG_ASSIGNMENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'party_org_assignment' AS dataset_name, 'party_org_assignment_id' AS column_name, GREATEST(COUNT_IF(PARTY_ORG_ASSIGNMENT_ID IS NOT NULL) - COUNT(DISTINCT PARTY_ORG_ASSIGNMENT_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'deposit_account' AS dataset_name, 'deposit_account_id' AS column_name, COUNT_IF(DEPOSIT_ACCOUNT_ID IS NULL OR TRIM(DEPOSIT_ACCOUNT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'deposit_account' AS dataset_name, 'deposit_account_id' AS column_name, GREATEST(COUNT_IF(DEPOSIT_ACCOUNT_ID IS NOT NULL) - COUNT(DISTINCT DEPOSIT_ACCOUNT_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'payment_card' AS dataset_name, 'card_id' AS column_name, COUNT_IF(CARD_ID IS NULL OR TRIM(CARD_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'payment_card' AS dataset_name, 'card_id' AS column_name, GREATEST(COUNT_IF(CARD_ID IS NOT NULL) - COUNT(DISTINCT CARD_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'device_profile' AS dataset_name, 'device_id' AS column_name, COUNT_IF(DEVICE_ID IS NULL OR TRIM(DEVICE_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'device_profile' AS dataset_name, 'device_id' AS column_name, GREATEST(COUNT_IF(DEVICE_ID IS NOT NULL) - COUNT(DISTINCT DEVICE_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'channel_event' AS dataset_name, 'channel_event_id' AS column_name, COUNT_IF(CHANNEL_EVENT_ID IS NULL OR TRIM(CHANNEL_EVENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'channel_event' AS dataset_name, 'channel_event_id' AS column_name, GREATEST(COUNT_IF(CHANNEL_EVENT_ID IS NOT NULL) - COUNT(DISTINCT CHANNEL_EVENT_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'payment_instruction' AS dataset_name, 'payment_instruction_id' AS column_name, COUNT_IF(PAYMENT_INSTRUCTION_ID IS NULL OR TRIM(PAYMENT_INSTRUCTION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'payment_instruction' AS dataset_name, 'payment_instruction_id' AS column_name, GREATEST(COUNT_IF(PAYMENT_INSTRUCTION_ID IS NOT NULL) - COUNT(DISTINCT PAYMENT_INSTRUCTION_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'payment_transaction' AS dataset_name, 'payment_transaction_id' AS column_name, COUNT_IF(PAYMENT_TRANSACTION_ID IS NULL OR TRIM(PAYMENT_TRANSACTION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'payment_transaction' AS dataset_name, 'payment_transaction_id' AS column_name, GREATEST(COUNT_IF(PAYMENT_TRANSACTION_ID IS NOT NULL) - COUNT(DISTINCT PAYMENT_TRANSACTION_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'risk_signal' AS dataset_name, 'risk_signal_id' AS column_name, COUNT_IF(RISK_SIGNAL_ID IS NULL OR TRIM(RISK_SIGNAL_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'risk_signal' AS dataset_name, 'risk_signal_id' AS column_name, GREATEST(COUNT_IF(RISK_SIGNAL_ID IS NOT NULL) - COUNT(DISTINCT RISK_SIGNAL_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'fraud_alert' AS dataset_name, 'fraud_alert_id' AS column_name, COUNT_IF(FRAUD_ALERT_ID IS NULL OR TRIM(FRAUD_ALERT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'fraud_alert' AS dataset_name, 'fraud_alert_id' AS column_name, GREATEST(COUNT_IF(FRAUD_ALERT_ID IS NOT NULL) - COUNT(DISTINCT FRAUD_ALERT_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'fraud_case' AS dataset_name, 'fraud_case_id' AS column_name, COUNT_IF(FRAUD_CASE_ID IS NULL OR TRIM(FRAUD_CASE_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'fraud_case' AS dataset_name, 'fraud_case_id' AS column_name, GREATEST(COUNT_IF(FRAUD_CASE_ID IS NOT NULL) - COUNT(DISTINCT FRAUD_CASE_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'investigation_event' AS dataset_name, 'investigation_event_id' AS column_name, COUNT_IF(INVESTIGATION_EVENT_ID IS NULL OR TRIM(INVESTIGATION_EVENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'investigation_event' AS dataset_name, 'investigation_event_id' AS column_name, GREATEST(COUNT_IF(INVESTIGATION_EVENT_ID IS NOT NULL) - COUNT(DISTINCT INVESTIGATION_EVENT_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'decision_record' AS dataset_name, 'decision_id' AS column_name, COUNT_IF(DECISION_ID IS NULL OR TRIM(DECISION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'decision_record' AS dataset_name, 'decision_id' AS column_name, GREATEST(COUNT_IF(DECISION_ID IS NOT NULL) - COUNT(DISTINCT DECISION_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_null' AS check_type, 'case_disposition' AS dataset_name, 'disposition_id' AS column_name, COUNT_IF(DISPOSITION_ID IS NULL OR TRIM(DISPOSITION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'primary_key_duplicate' AS check_type, 'case_disposition' AS dataset_name, 'disposition_id' AS column_name, GREATEST(COUNT_IF(DISPOSITION_ID IS NOT NULL) - COUNT(DISTINCT DISPOSITION_ID), 0) AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'code_set_name' AS column_name, COUNT_IF(CODE_SET_NAME IS NULL OR TRIM(CODE_SET_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'code_value' AS column_name, COUNT_IF(CODE_VALUE IS NULL OR TRIM(CODE_VALUE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'code_description' AS column_name, COUNT_IF(CODE_DESCRIPTION IS NULL OR TRIM(CODE_DESCRIPTION::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'is_active' AS column_name, COUNT_IF(IS_ACTIVE IS NULL OR TRIM(IS_ACTIVE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'calendar_day' AS dataset_name, 'calendar_date' AS column_name, COUNT_IF(CALENDAR_DATE IS NULL OR TRIM(CALENDAR_DATE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'calendar_day' AS dataset_name, 'calendar_year' AS column_name, COUNT_IF(CALENDAR_YEAR IS NULL OR TRIM(CALENDAR_YEAR::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'calendar_day' AS dataset_name, 'calendar_month' AS column_name, COUNT_IF(CALENDAR_MONTH IS NULL OR TRIM(CALENDAR_MONTH::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'calendar_day' AS dataset_name, 'week_of_year' AS column_name, COUNT_IF(WEEK_OF_YEAR IS NULL OR TRIM(WEEK_OF_YEAR::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'region' AS dataset_name, 'region_id' AS column_name, COUNT_IF(REGION_ID IS NULL OR TRIM(REGION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'region' AS dataset_name, 'region_code' AS column_name, COUNT_IF(REGION_CODE IS NULL OR TRIM(REGION_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'region' AS dataset_name, 'region_name' AS column_name, COUNT_IF(REGION_NAME IS NULL OR TRIM(REGION_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'region' AS dataset_name, 'country_group_code' AS column_name, COUNT_IF(COUNTRY_GROUP_CODE IS NULL OR TRIM(COUNTRY_GROUP_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'region' AS dataset_name, 'is_active' AS column_name, COUNT_IF(IS_ACTIVE IS NULL OR TRIM(IS_ACTIVE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_territory' AS dataset_name, 'branch_territory_id' AS column_name, COUNT_IF(BRANCH_TERRITORY_ID IS NULL OR TRIM(BRANCH_TERRITORY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_territory' AS dataset_name, 'branch_territory_code' AS column_name, COUNT_IF(BRANCH_TERRITORY_CODE IS NULL OR TRIM(BRANCH_TERRITORY_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_territory' AS dataset_name, 'region_id' AS column_name, COUNT_IF(REGION_ID IS NULL OR TRIM(REGION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_location' AS dataset_name, 'branch_id' AS column_name, COUNT_IF(BRANCH_ID IS NULL OR TRIM(BRANCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_location' AS dataset_name, 'branch_code' AS column_name, COUNT_IF(BRANCH_CODE IS NULL OR TRIM(BRANCH_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_location' AS dataset_name, 'branch_territory_id' AS column_name, COUNT_IF(BRANCH_TERRITORY_ID IS NULL OR TRIM(BRANCH_TERRITORY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_location' AS dataset_name, 'region_id' AS column_name, COUNT_IF(REGION_ID IS NULL OR TRIM(REGION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'branch_location' AS dataset_name, 'country_code' AS column_name, COUNT_IF(COUNTRY_CODE IS NULL OR TRIM(COUNTRY_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'business_unit' AS dataset_name, 'business_unit_id' AS column_name, COUNT_IF(BUSINESS_UNIT_ID IS NULL OR TRIM(BUSINESS_UNIT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'business_unit' AS dataset_name, 'business_unit_code' AS column_name, COUNT_IF(BUSINESS_UNIT_CODE IS NULL OR TRIM(BUSINESS_UNIT_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'business_unit' AS dataset_name, 'business_unit_name' AS column_name, COUNT_IF(BUSINESS_UNIT_NAME IS NULL OR TRIM(BUSINESS_UNIT_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'business_unit' AS dataset_name, 'business_unit_type' AS column_name, COUNT_IF(BUSINESS_UNIT_TYPE IS NULL OR TRIM(BUSINESS_UNIT_TYPE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'business_unit' AS dataset_name, 'region_id' AS column_name, COUNT_IF(REGION_ID IS NULL OR TRIM(REGION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'analyst_team' AS dataset_name, 'analyst_team_id' AS column_name, COUNT_IF(ANALYST_TEAM_ID IS NULL OR TRIM(ANALYST_TEAM_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'analyst_team' AS dataset_name, 'analyst_team_code' AS column_name, COUNT_IF(ANALYST_TEAM_CODE IS NULL OR TRIM(ANALYST_TEAM_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'analyst_team' AS dataset_name, 'analyst_team_name' AS column_name, COUNT_IF(ANALYST_TEAM_NAME IS NULL OR TRIM(ANALYST_TEAM_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'analyst_team' AS dataset_name, 'business_unit_id' AS column_name, COUNT_IF(BUSINESS_UNIT_ID IS NULL OR TRIM(BUSINESS_UNIT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'analyst_team' AS dataset_name, 'region_id' AS column_name, COUNT_IF(REGION_ID IS NULL OR TRIM(REGION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party' AS dataset_name, 'party_id' AS column_name, COUNT_IF(PARTY_ID IS NULL OR TRIM(PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party' AS dataset_name, 'party_type' AS column_name, COUNT_IF(PARTY_TYPE IS NULL OR TRIM(PARTY_TYPE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party' AS dataset_name, 'party_status' AS column_name, COUNT_IF(PARTY_STATUS IS NULL OR TRIM(PARTY_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'party_org_assignment_id' AS column_name, COUNT_IF(PARTY_ORG_ASSIGNMENT_ID IS NULL OR TRIM(PARTY_ORG_ASSIGNMENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'party_id' AS column_name, COUNT_IF(PARTY_ID IS NULL OR TRIM(PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'assignment_role_code' AS column_name, COUNT_IF(ASSIGNMENT_ROLE_CODE IS NULL OR TRIM(ASSIGNMENT_ROLE_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'effective_from_at' AS column_name, COUNT_IF(EFFECTIVE_FROM_AT IS NULL OR TRIM(EFFECTIVE_FROM_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'deposit_account' AS dataset_name, 'deposit_account_id' AS column_name, COUNT_IF(DEPOSIT_ACCOUNT_ID IS NULL OR TRIM(DEPOSIT_ACCOUNT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'deposit_account' AS dataset_name, 'account_status' AS column_name, COUNT_IF(ACCOUNT_STATUS IS NULL OR TRIM(ACCOUNT_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'deposit_account' AS dataset_name, 'product_type_code' AS column_name, COUNT_IF(PRODUCT_TYPE_CODE IS NULL OR TRIM(PRODUCT_TYPE_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'deposit_account' AS dataset_name, 'primary_party_id' AS column_name, COUNT_IF(PRIMARY_PARTY_ID IS NULL OR TRIM(PRIMARY_PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'deposit_account' AS dataset_name, 'account_currency_code' AS column_name, COUNT_IF(ACCOUNT_CURRENCY_CODE IS NULL OR TRIM(ACCOUNT_CURRENCY_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'deposit_account' AS dataset_name, 'opened_at' AS column_name, COUNT_IF(OPENED_AT IS NULL OR TRIM(OPENED_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_card' AS dataset_name, 'card_id' AS column_name, COUNT_IF(CARD_ID IS NULL OR TRIM(CARD_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_card' AS dataset_name, 'linked_account_id' AS column_name, COUNT_IF(LINKED_ACCOUNT_ID IS NULL OR TRIM(LINKED_ACCOUNT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_card' AS dataset_name, 'card_status' AS column_name, COUNT_IF(CARD_STATUS IS NULL OR TRIM(CARD_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'device_profile' AS dataset_name, 'device_id' AS column_name, COUNT_IF(DEVICE_ID IS NULL OR TRIM(DEVICE_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'device_profile' AS dataset_name, 'device_status' AS column_name, COUNT_IF(DEVICE_STATUS IS NULL OR TRIM(DEVICE_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'channel_event' AS dataset_name, 'channel_event_id' AS column_name, COUNT_IF(CHANNEL_EVENT_ID IS NULL OR TRIM(CHANNEL_EVENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'channel_event' AS dataset_name, 'channel_code' AS column_name, COUNT_IF(CHANNEL_CODE IS NULL OR TRIM(CHANNEL_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'channel_event' AS dataset_name, 'event_at' AS column_name, COUNT_IF(EVENT_AT IS NULL OR TRIM(EVENT_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'payment_instruction_id' AS column_name, COUNT_IF(PAYMENT_INSTRUCTION_ID IS NULL OR TRIM(PAYMENT_INSTRUCTION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'instruction_status' AS column_name, COUNT_IF(INSTRUCTION_STATUS IS NULL OR TRIM(INSTRUCTION_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'debtor_account_id' AS column_name, COUNT_IF(DEBTOR_ACCOUNT_ID IS NULL OR TRIM(DEBTOR_ACCOUNT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'debtor_party_id' AS column_name, COUNT_IF(DEBTOR_PARTY_ID IS NULL OR TRIM(DEBTOR_PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'creditor_party_id' AS column_name, COUNT_IF(CREDITOR_PARTY_ID IS NULL OR TRIM(CREDITOR_PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'instructed_amount' AS column_name, COUNT_IF(INSTRUCTED_AMOUNT IS NULL OR TRIM(INSTRUCTED_AMOUNT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'instructed_currency_code' AS column_name, COUNT_IF(INSTRUCTED_CURRENCY_CODE IS NULL OR TRIM(INSTRUCTED_CURRENCY_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'channel_event_id' AS column_name, COUNT_IF(CHANNEL_EVENT_ID IS NULL OR TRIM(CHANNEL_EVENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'event_at' AS column_name, COUNT_IF(EVENT_AT IS NULL OR TRIM(EVENT_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'payment_transaction_id' AS column_name, COUNT_IF(PAYMENT_TRANSACTION_ID IS NULL OR TRIM(PAYMENT_TRANSACTION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'payment_instruction_id' AS column_name, COUNT_IF(PAYMENT_INSTRUCTION_ID IS NULL OR TRIM(PAYMENT_INSTRUCTION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'transaction_status' AS column_name, COUNT_IF(TRANSACTION_STATUS IS NULL OR TRIM(TRANSACTION_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'booking_amount' AS column_name, COUNT_IF(BOOKING_AMOUNT IS NULL OR TRIM(BOOKING_AMOUNT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'transaction_currency_code' AS column_name, COUNT_IF(TRANSACTION_CURRENCY_CODE IS NULL OR TRIM(TRANSACTION_CURRENCY_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'risk_signal' AS dataset_name, 'risk_signal_id' AS column_name, COUNT_IF(RISK_SIGNAL_ID IS NULL OR TRIM(RISK_SIGNAL_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'risk_signal' AS dataset_name, 'payment_instruction_id' AS column_name, COUNT_IF(PAYMENT_INSTRUCTION_ID IS NULL OR TRIM(PAYMENT_INSTRUCTION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'risk_signal' AS dataset_name, 'signal_type_code' AS column_name, COUNT_IF(SIGNAL_TYPE_CODE IS NULL OR TRIM(SIGNAL_TYPE_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'risk_signal' AS dataset_name, 'risk_level' AS column_name, COUNT_IF(RISK_LEVEL IS NULL OR TRIM(RISK_LEVEL::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'risk_signal' AS dataset_name, 'event_at' AS column_name, COUNT_IF(EVENT_AT IS NULL OR TRIM(EVENT_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'fraud_alert_id' AS column_name, COUNT_IF(FRAUD_ALERT_ID IS NULL OR TRIM(FRAUD_ALERT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'risk_signal_id' AS column_name, COUNT_IF(RISK_SIGNAL_ID IS NULL OR TRIM(RISK_SIGNAL_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'alert_status' AS column_name, COUNT_IF(ALERT_STATUS IS NULL OR TRIM(ALERT_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'alert_severity' AS column_name, COUNT_IF(ALERT_SEVERITY IS NULL OR TRIM(ALERT_SEVERITY::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'created_at' AS column_name, COUNT_IF(CREATED_AT IS NULL OR TRIM(CREATED_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_case' AS dataset_name, 'fraud_case_id' AS column_name, COUNT_IF(FRAUD_CASE_ID IS NULL OR TRIM(FRAUD_CASE_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_case' AS dataset_name, 'primary_alert_id' AS column_name, COUNT_IF(PRIMARY_ALERT_ID IS NULL OR TRIM(PRIMARY_ALERT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_case' AS dataset_name, 'case_status' AS column_name, COUNT_IF(CASE_STATUS IS NULL OR TRIM(CASE_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'fraud_case' AS dataset_name, 'opened_at' AS column_name, COUNT_IF(OPENED_AT IS NULL OR TRIM(OPENED_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'investigation_event' AS dataset_name, 'investigation_event_id' AS column_name, COUNT_IF(INVESTIGATION_EVENT_ID IS NULL OR TRIM(INVESTIGATION_EVENT_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'investigation_event' AS dataset_name, 'fraud_case_id' AS column_name, COUNT_IF(FRAUD_CASE_ID IS NULL OR TRIM(FRAUD_CASE_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'investigation_event' AS dataset_name, 'investigation_event_type' AS column_name, COUNT_IF(INVESTIGATION_EVENT_TYPE IS NULL OR TRIM(INVESTIGATION_EVENT_TYPE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'investigation_event' AS dataset_name, 'actor_party_id' AS column_name, COUNT_IF(ACTOR_PARTY_ID IS NULL OR TRIM(ACTOR_PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'investigation_event' AS dataset_name, 'event_at' AS column_name, COUNT_IF(EVENT_AT IS NULL OR TRIM(EVENT_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'decision_record' AS dataset_name, 'decision_id' AS column_name, COUNT_IF(DECISION_ID IS NULL OR TRIM(DECISION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'decision_record' AS dataset_name, 'fraud_case_id' AS column_name, COUNT_IF(FRAUD_CASE_ID IS NULL OR TRIM(FRAUD_CASE_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'decision_record' AS dataset_name, 'decision_type' AS column_name, COUNT_IF(DECISION_TYPE IS NULL OR TRIM(DECISION_TYPE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'decision_record' AS dataset_name, 'decision_status' AS column_name, COUNT_IF(DECISION_STATUS IS NULL OR TRIM(DECISION_STATUS::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'decision_record' AS dataset_name, 'decision_maker_party_id' AS column_name, COUNT_IF(DECISION_MAKER_PARTY_ID IS NULL OR TRIM(DECISION_MAKER_PARTY_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'decision_record' AS dataset_name, 'decided_at' AS column_name, COUNT_IF(DECIDED_AT IS NULL OR TRIM(DECIDED_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'case_disposition' AS dataset_name, 'disposition_id' AS column_name, COUNT_IF(DISPOSITION_ID IS NULL OR TRIM(DISPOSITION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'case_disposition' AS dataset_name, 'decision_id' AS column_name, COUNT_IF(DECISION_ID IS NULL OR TRIM(DECISION_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'case_disposition' AS dataset_name, 'disposition_code' AS column_name, COUNT_IF(DISPOSITION_CODE IS NULL OR TRIM(DISPOSITION_CODE::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'required_field_null' AS check_type, 'case_disposition' AS dataset_name, 'outcome_at' AS column_name, COUNT_IF(OUTCOME_AT IS NULL OR TRIM(OUTCOME_AT::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'reference_data_catalog' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REFERENCE_DATA_CATALOG WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'calendar_day' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'calendar_day' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'calendar_day' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CALENDAR_DAY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'region' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'region' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'region' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_REGION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'branch_territory' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'branch_territory' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'branch_territory' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_TERRITORY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'branch_location' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'branch_location' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'branch_location' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BRANCH_LOCATION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'business_unit' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'business_unit' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'business_unit' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_BUSINESS_UNIT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'analyst_team' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'analyst_team' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'analyst_team' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_ANALYST_TEAM WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'party' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'party' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'party' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'party_org_assignment' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PARTY_ORG_ASSIGNMENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'deposit_account' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'deposit_account' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'deposit_account' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEPOSIT_ACCOUNT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_card' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_card' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_card' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_CARD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'device_profile' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'device_profile' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'device_profile' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DEVICE_PROFILE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'channel_event' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'channel_event' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'channel_event' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CHANNEL_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_instruction' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_INSTRUCTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'payment_transaction' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_PAYMENT_TRANSACTION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'risk_signal' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'risk_signal' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'risk_signal' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_RISK_SIGNAL WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'fraud_alert' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_ALERT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'fraud_case' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'fraud_case' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'fraud_case' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_FRAUD_CASE WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'investigation_event' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'investigation_event' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'investigation_event' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_INVESTIGATION_EVENT WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'decision_record' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'decision_record' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'decision_record' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_DECISION_RECORD WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'case_disposition' AS dataset_name, 'ingestion_batch_id' AS column_name, COUNT_IF(INGESTION_BATCH_ID IS NULL OR TRIM(INGESTION_BATCH_ID::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'case_disposition' AS dataset_name, 'source_file_name' AS column_name, COUNT_IF(SOURCE_FILE_NAME IS NULL OR TRIM(SOURCE_FILE_NAME::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
  UNION ALL
  SELECT 'audit_field_null' AS check_type, 'case_disposition' AS dataset_name, 'ingested_at_utc' AS column_name, COUNT_IF(INGESTED_AT_UTC IS NULL OR TRIM(INGESTED_AT_UTC::STRING) = '') AS failed_count, COUNT(*) AS row_count FROM FRAUDLENS.BRONZE.BRONZE_CASE_DISPOSITION WHERE INGESTION_BATCH_ID = :batch_id
)
SELECT
  check_type,
  dataset_name,
  column_name,
  row_count,
  failed_count,
  CASE WHEN failed_count = 0 THEN 'pass' ELSE 'fail' END AS check_status
FROM checks
ORDER BY check_type, dataset_name, column_name;
