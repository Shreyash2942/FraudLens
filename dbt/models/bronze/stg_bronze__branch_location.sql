{{ config(alias='BRONZE_STG_BRANCH_LOCATION', tags=['bronze', 'staging_raw']) }}

select
    src.BRANCH_ID as branch_id,
    src.BRANCH_CODE as branch_code,
    src.BRANCH_NAME as branch_name,
    src.BRANCH_TERRITORY_ID as branch_territory_id,
    src.REGION_ID as region_id,
    src.COUNTRY_CODE as country_code,
    src.CITY_NAME as city_name,
    src.IS_ACTIVE as is_active,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'branch_location') }} as src
{{ fraudlens_batch_where('src') }}
