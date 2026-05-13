{{ config(alias='BRONZE_STG_DEVICE_PROFILE', tags=['bronze', 'staging_raw']) }}

select
    src.DEVICE_ID as device_id,
    src.DEVICE_STATUS as device_status,
    src.OPERATING_SYSTEM_CODE as operating_system_code,
    src.DEVICE_RISK_BAND as device_risk_band,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'device_profile') }} as src
{{ fraudlens_batch_where('src') }}
