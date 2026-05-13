{{ config(alias='BRONZE_STG_PAYMENT_TRANSACTION', tags=['bronze', 'staging_raw']) }}

select
    src.PAYMENT_TRANSACTION_ID as payment_transaction_id,
    src.PAYMENT_INSTRUCTION_ID as payment_instruction_id,
    src.TRANSACTION_STATUS as transaction_status,
    src.BOOKING_AMOUNT as booking_amount,
    src.TRANSACTION_CURRENCY_CODE as transaction_currency_code,
    src.SETTLEMENT_AT as settlement_at,
    src.MERCHANT_CATEGORY_CODE as merchant_category_code,
    src.REVERSAL_REASON_CODE as reversal_reason_code,
    src.POSTED_DATE as posted_date,
    src.VALUE_DATE as value_date,
    src.TRANSACTION_DIRECTION_CODE as transaction_direction_code,
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'payment_transaction') }} as src
{{ fraudlens_batch_where('src') }}
