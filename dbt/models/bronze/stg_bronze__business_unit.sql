{{ config(alias='BRONZE_STG_BUSINESS_UNIT', tags=['bronze', 'staging_raw']) }}

select
    src.BUSINESS_UNIT_ID as business_unit_id,
    src.BUSINESS_UNIT_CODE as business_unit_code,
    src.BUSINESS_UNIT_NAME as business_unit_name,
    src.BUSINESS_UNIT_TYPE as business_unit_type,
    src.REGION_ID as region_id,
    src.IS_ACTIVE as is_active,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'business_unit') }} as src
{{ fraudlens_batch_where('src') }}
