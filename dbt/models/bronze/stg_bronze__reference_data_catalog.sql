{{ config(alias='BRONZE_STG_REFERENCE_DATA_CATALOG', tags=['bronze', 'staging_raw']) }}

select
    src.CODE_SET_NAME as code_set_name,
    src.CODE_VALUE as code_value,
    src.CODE_DESCRIPTION as code_description,
    src.IS_ACTIVE as is_active,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'reference_data_catalog') }} as src
{{ fraudlens_batch_where('src') }}
