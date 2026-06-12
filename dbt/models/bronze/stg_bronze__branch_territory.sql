{{ config(alias='bronze_stg_branch_territory', tags=['bronze', 'staging_raw']) }}

select
    src.BRANCH_TERRITORY_ID as branch_territory_id,
    src.BRANCH_TERRITORY_CODE as branch_territory_code,
    src.BRANCH_TERRITORY_NAME as branch_territory_name,
    src.REGION_ID as region_id,
    src.IS_ACTIVE as is_active,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'branch_territory') }} as src
{{ fraudlens_batch_where('src') }}
