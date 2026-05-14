{{ config(alias='SILVER_DEPOSIT_ACCOUNT', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_text('src.deposit_account_id') }} as deposit_account_id,
    {{ fraudlens_clean_text('src.account_status', uppercase=true) }} as account_status,
    {{ fraudlens_clean_text('src.product_type_code', uppercase=true) }} as product_type_code,
    {{ fraudlens_clean_text('src.primary_party_id') }} as primary_party_id,
    {{ fraudlens_clean_text('src.account_currency_code', uppercase=true) }} as account_currency_code,
    {{ fraudlens_clean_decimal('src.available_balance_amount') }} as available_balance_amount,
    {{ fraudlens_clean_timestamp('src.opened_at') }} as opened_at,
    {{ fraudlens_clean_text('src.opened_branch_id') }} as opened_branch_id,
    {{ fraudlens_clean_text('src.servicing_business_unit_id') }} as servicing_business_unit_id,
    {{ fraudlens_clean_text('src.account_region_id') }} as account_region_id,
    {{ fraudlens_clean_timestamp('src.closed_at') }} as closed_at,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__deposit_account') }} as src
{{ fraudlens_batch_where('src') }}
