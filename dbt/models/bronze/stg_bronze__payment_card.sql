{{ config(alias='BRONZE_STG_PAYMENT_CARD', tags=['bronze', 'staging_raw']) }}

select
    src.CARD_ID as card_id,
    src.LINKED_ACCOUNT_ID as linked_account_id,
    src.CARD_STATUS as card_status,
    src.CARD_NETWORK_CODE as card_network_code,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'payment_card') }} as src
{{ fraudlens_batch_where('src') }}
