{{ config(alias='SILVER_PAYMENT_TRANSACTION', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.payment_transaction_id') }} as payment_transaction_id,
    {{ fraudlens_clean_text('src.payment_instruction_id') }} as payment_instruction_id,
    {{ fraudlens_clean_text('src.transaction_status', uppercase=true) }} as transaction_status,
    {{ fraudlens_clean_decimal('src.booking_amount') }} as booking_amount,
    {{ fraudlens_clean_text('src.transaction_currency_code', uppercase=true) }} as transaction_currency_code,
    {{ fraudlens_clean_timestamp('src.settlement_at') }} as settlement_at,
    {{ fraudlens_clean_text('src.merchant_category_code', uppercase=true) }} as merchant_category_code,
    {{ fraudlens_clean_text('src.reversal_reason_code', uppercase=true) }} as reversal_reason_code,
    {{ fraudlens_clean_date('src.posted_date') }} as posted_date,
    {{ fraudlens_clean_date('src.value_date') }} as value_date,
    {{ fraudlens_clean_text('src.transaction_direction_code', uppercase=true) }} as transaction_direction_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__payment_transaction') }} as src
{{ fraudlens_batch_where('src') }}
