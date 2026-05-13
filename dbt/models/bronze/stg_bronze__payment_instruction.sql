{{ config(alias='BRONZE_STG_PAYMENT_INSTRUCTION', tags=['bronze', 'staging_raw']) }}

select
    src.PAYMENT_INSTRUCTION_ID as payment_instruction_id,
    src.INSTRUCTION_STATUS as instruction_status,
    src.DEBTOR_ACCOUNT_ID as debtor_account_id,
    src.DEBTOR_PARTY_ID as debtor_party_id,
    src.CREDITOR_PARTY_ID as creditor_party_id,
    src.INSTRUCTED_AMOUNT as instructed_amount,
    src.INSTRUCTED_CURRENCY_CODE as instructed_currency_code,
    src.PAYMENT_PURPOSE_CODE as payment_purpose_code,
    src.CHANNEL_EVENT_ID as channel_event_id,
    src.CARD_ID as card_id,
    src.DEVICE_ID as device_id,
    src.EVENT_AT as event_at,
    src.PAYMENT_RAIL_CODE as payment_rail_code,
    src.IS_CROSS_BORDER as is_cross_border,
    src.MERCHANT_COUNTRY_CODE as merchant_country_code,
    src.COUNTERPARTY_BANK_COUNTRY_CODE as counterparty_bank_country_code,
    src.BOOKING_DATE as booking_date,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'payment_instruction') }} as src
{{ fraudlens_batch_where('src') }}
