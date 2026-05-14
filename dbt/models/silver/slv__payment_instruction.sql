{{ config(alias='SILVER_PAYMENT_INSTRUCTION', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.payment_instruction_id') }} as payment_instruction_id,
    {{ fraudlens_clean_text('src.instruction_status', uppercase=true) }} as instruction_status,
    {{ fraudlens_clean_text('src.debtor_account_id') }} as debtor_account_id,
    {{ fraudlens_clean_text('src.debtor_party_id') }} as debtor_party_id,
    {{ fraudlens_clean_text('src.creditor_party_id') }} as creditor_party_id,
    {{ fraudlens_clean_decimal('src.instructed_amount') }} as instructed_amount,
    {{ fraudlens_clean_text('src.instructed_currency_code', uppercase=true) }} as instructed_currency_code,
    {{ fraudlens_clean_text('src.payment_purpose_code', uppercase=true) }} as payment_purpose_code,
    {{ fraudlens_clean_text('src.channel_event_id') }} as channel_event_id,
    {{ fraudlens_clean_text('src.card_id') }} as card_id,
    {{ fraudlens_clean_text('src.device_id') }} as device_id,
    {{ fraudlens_clean_timestamp('src.event_at') }} as event_at,
    {{ fraudlens_clean_text('src.payment_rail_code', uppercase=true) }} as payment_rail_code,
    {{ fraudlens_clean_boolean('src.is_cross_border') }} as is_cross_border,
    {{ fraudlens_clean_text('src.merchant_country_code', uppercase=true) }} as merchant_country_code,
    {{ fraudlens_clean_text('src.counterparty_bank_country_code', uppercase=true) }} as counterparty_bank_country_code,
    {{ fraudlens_clean_date('src.booking_date') }} as booking_date,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__payment_instruction') }} as src
{{ fraudlens_batch_where('src') }}
