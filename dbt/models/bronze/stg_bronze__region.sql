{{ config(alias='BRONZE_STG_REGION', tags=['bronze', 'staging_raw']) }}

select
    src.REGION_ID as region_id,
    src.REGION_CODE as region_code,
    src.REGION_NAME as region_name,
    src.COUNTRY_GROUP_CODE as country_group_code,
    src.IS_ACTIVE as is_active,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'region') }} as src
{{ fraudlens_batch_where('src') }}
