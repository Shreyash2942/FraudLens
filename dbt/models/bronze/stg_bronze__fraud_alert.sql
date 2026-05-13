{{ config(alias='BRONZE_STG_FRAUD_ALERT', tags=['bronze', 'staging_raw']) }}

select
    src.FRAUD_ALERT_ID as fraud_alert_id,
    src.RISK_SIGNAL_ID as risk_signal_id,
    src.ALERT_STATUS as alert_status,
    src.ALERT_SEVERITY as alert_severity,
    src.QUEUE_CODE as queue_code,
    src.CREATED_AT as created_at,
    src.ALERT_TYPE_CODE as alert_type_code,
    src.ALERT_SOURCE_CODE as alert_source_code,
    src.OWNING_BUSINESS_UNIT_ID as owning_business_unit_id,
    src.OWNING_ANALYST_TEAM_ID as owning_analyst_team_id,
    src.SERVICE_LEVEL_DUE_AT as service_level_due_at,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'fraud_alert') }} as src
{{ fraudlens_batch_where('src') }}
