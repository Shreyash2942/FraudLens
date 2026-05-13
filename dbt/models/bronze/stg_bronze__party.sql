{{ config(alias='BRONZE_STG_PARTY', tags=['bronze', 'staging_raw']) }}

select
    src.PARTY_ID as party_id,
    src.PARTY_TYPE as party_type,
    src.PARTY_STATUS as party_status,
    src.DOMICILE_COUNTRY_CODE as domicile_country_code,
    src.RISK_SEGMENT_CODE as risk_segment_code,
    src.CUSTOMER_SEGMENT_CODE as customer_segment_code,
    src.CUSTOMER_TYPE_CODE as customer_type_code,
    src.INDUSTRY_SECTOR_CODE as industry_sector_code,
    src.RESIDENCY_REGION_ID as residency_region_id,
    src.CUSTOMER_SINCE_AT as customer_since_at,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'party') }} as src
{{ fraudlens_batch_where('src') }}
