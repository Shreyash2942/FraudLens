{{ config(alias='bronze_stg_analyst_team', tags=['bronze', 'staging_raw']) }}

select
    src.ANALYST_TEAM_ID as analyst_team_id,
    src.ANALYST_TEAM_CODE as analyst_team_code,
    src.ANALYST_TEAM_NAME as analyst_team_name,
    src.BUSINESS_UNIT_ID as business_unit_id,
    src.REGION_ID as region_id,
    src.IS_ACTIVE as is_active,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'analyst_team') }} as src
{{ fraudlens_batch_where('src') }}
