{{ config(alias='BRONZE_STG_BRANCH_TERRITORY', tags=['bronze', 'staging_raw']) }}

select
    src.BRANCH_TERRITORY_ID as branch_territory_id,
    src.BRANCH_TERRITORY_CODE as branch_territory_code,
    src.BRANCH_TERRITORY_NAME as branch_territory_name,
    src.REGION_ID as region_id,
    src.IS_ACTIVE as is_active,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'branch_territory') }} as src
{{ fraudlens_batch_where('src') }}
