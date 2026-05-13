{{ config(alias='BRONZE_STG_CHANNEL_EVENT', tags=['bronze', 'staging_raw']) }}

select
    src.CHANNEL_EVENT_ID as channel_event_id,
    src.CHANNEL_CODE as channel_code,
    src.SESSION_ID as session_id,
    src.BRANCH_ID as branch_id,
    src.EVENT_AT as event_at,
    src.EVENT_COUNTRY_CODE as event_country_code,
    src.IP_COUNTRY_CODE as ip_country_code,
    src.AUTHENTICATION_RESULT_CODE as authentication_result_code,
    src.SESSION_RISK_CODE as session_risk_code,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'channel_event') }} as src
{{ fraudlens_batch_where('src') }}
