{{ config(alias='BRONZE_STG_BUSINESS_UNIT', tags=['bronze', 'staging_raw']) }}

select
    src.BUSINESS_UNIT_ID as business_unit_id,
    src.BUSINESS_UNIT_CODE as business_unit_code,
    src.BUSINESS_UNIT_NAME as business_unit_name,
    src.BUSINESS_UNIT_TYPE as business_unit_type,
    src.REGION_ID as region_id,
    src.IS_ACTIVE as is_active,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'business_unit') }} as src
{{ fraudlens_batch_where('src') }}
