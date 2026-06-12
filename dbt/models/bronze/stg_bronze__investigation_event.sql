{{ config(alias='bronze_stg_investigation_event', tags=['bronze', 'staging_raw']) }}

select
    src.INVESTIGATION_EVENT_ID as investigation_event_id,
    src.FRAUD_CASE_ID as fraud_case_id,
    src.INVESTIGATION_EVENT_TYPE as investigation_event_type,
    src.ACTOR_PARTY_ID as actor_party_id,
    src.EVENT_AT as event_at,
    src.EVENT_RESULT_CODE as event_result_code,
    src.ELAPSED_MINUTES as elapsed_minutes,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'investigation_event') }} as src
{{ fraudlens_batch_where('src') }}
