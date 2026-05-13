{{ config(alias='BRONZE_STG_DEVICE_PROFILE', tags=['bronze', 'staging_raw']) }}

select
    src.DEVICE_ID as device_id,
    src.DEVICE_STATUS as device_status,
    src.OPERATING_SYSTEM_CODE as operating_system_code,
    src.DEVICE_RISK_BAND as device_risk_band,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'device_profile') }} as src
{{ fraudlens_batch_where('src') }}
