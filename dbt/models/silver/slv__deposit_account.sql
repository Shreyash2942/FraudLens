{{ config(alias='SILVER_DEPOSIT_ACCOUNT', tags=['silver', 'conformed']) }}

with standardized as (
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
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.deposit_account_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
),
business_safe as (
    select
        ranked.deposit_account_id,
        ranked.account_status,
        ranked.product_type_code,
        ranked.primary_party_id,
        ranked.account_currency_code,
        ranked.available_balance_amount,
        ranked.opened_at,
        ranked.opened_branch_id,
        ranked.servicing_business_unit_id,
        ranked.account_region_id,
        case
            when ranked.closed_at is not null
             and ranked.opened_at is not null
             and ranked.closed_at < ranked.opened_at then null
            else ranked.closed_at
        end as closed_at,
        ranked.ingestion_batch_id,
        ranked.source_file_name,
        ranked.ingested_at_utc,
        ranked.pipeline_processed_at_utc,
        ranked.lineage_run_id
    from ranked
    where ranked.dedup_rank = 1
)
select
    business_safe.deposit_account_id,
    business_safe.account_status,
    business_safe.product_type_code,
    business_safe.primary_party_id,
    business_safe.account_currency_code,
    business_safe.available_balance_amount,
    business_safe.opened_at,
    business_safe.opened_branch_id,
    business_safe.servicing_business_unit_id,
    business_safe.account_region_id,
    business_safe.closed_at,
    business_safe.ingestion_batch_id,
    business_safe.source_file_name,
    business_safe.ingested_at_utc,
    business_safe.pipeline_processed_at_utc,
    business_safe.lineage_run_id
from business_safe
