{{ config(alias='bronze_stg_channel_event', tags=['bronze', 'staging_raw']) }}

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
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'channel_event') }} as src
{{ fraudlens_batch_where('src') }}
