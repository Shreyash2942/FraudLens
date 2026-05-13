{{ config(alias='BRONZE_STG_INVESTIGATION_EVENT', tags=['bronze', 'staging_raw']) }}

select
    src.INVESTIGATION_EVENT_ID as investigation_event_id,
    src.FRAUD_CASE_ID as fraud_case_id,
    src.INVESTIGATION_EVENT_TYPE as investigation_event_type,
    src.ACTOR_PARTY_ID as actor_party_id,
    src.EVENT_AT as event_at,
    src.EVENT_RESULT_CODE as event_result_code,
    src.ELAPSED_MINUTES as elapsed_minutes,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'investigation_event') }} as src
{{ fraudlens_batch_where('src') }}
