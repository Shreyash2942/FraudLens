{{ config(alias='SILVER_PAYMENT_TRANSACTION', tags=['silver', 'conformed']) }}

with standardized as (
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
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.payment_transaction_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
)
select
    ranked.payment_transaction_id,
    ranked.payment_instruction_id,
    ranked.transaction_status,
    ranked.booking_amount,
    ranked.transaction_currency_code,
    ranked.settlement_at,
    ranked.merchant_category_code,
    ranked.reversal_reason_code,
    ranked.posted_date,
    ranked.value_date,
    ranked.transaction_direction_code,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked.dedup_rank = 1
