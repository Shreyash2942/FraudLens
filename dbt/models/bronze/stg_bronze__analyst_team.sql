{{ config(alias='BRONZE_STG_ANALYST_TEAM', tags=['bronze', 'staging_raw']) }}

select
    src.ANALYST_TEAM_ID as analyst_team_id,
    src.ANALYST_TEAM_CODE as analyst_team_code,
    src.ANALYST_TEAM_NAME as analyst_team_name,
    src.BUSINESS_UNIT_ID as business_unit_id,
    src.REGION_ID as region_id,
    src.IS_ACTIVE as is_active,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'analyst_team') }} as src
{{ fraudlens_batch_where('src') }}
