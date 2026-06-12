{{ config(alias='bronze_stg_region', tags=['bronze', 'staging_raw']) }}

select
    src.REGION_ID as region_id,
    src.REGION_CODE as region_code,
    src.REGION_NAME as region_name,
    src.COUNTRY_GROUP_CODE as country_group_code,
    src.IS_ACTIVE as is_active,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'region') }} as src
{{ fraudlens_batch_where('src') }}
