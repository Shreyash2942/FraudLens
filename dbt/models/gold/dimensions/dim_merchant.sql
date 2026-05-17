{{ config(alias='GOLD_DIM_MERCHANT', tags=['gold', 'dim']) }}

with merchant_base as (
    select
        pi.merchant_country_code,
        pt.merchant_category_code,
        pi.counterparty_bank_country_code,
        pi.payment_rail_code,
        max(pi.ingestion_batch_id) as ingestion_batch_id,
        max(pi.source_file_name) as source_file_name,
        max(pi.ingested_at_utc) as ingested_at_utc,
        max(pi.pipeline_processed_at_utc) as pipeline_processed_at_utc,
        max(pi.lineage_run_id) as lineage_run_id
    from {{ ref('slv__payment_instruction') }} as pi
    left join {{ ref('slv__payment_transaction') }} as pt
        on pi.payment_instruction_id = pt.payment_instruction_id
    where pi.merchant_country_code is not null
       or pt.merchant_category_code is not null
       or pi.counterparty_bank_country_code is not null
    group by
        pi.merchant_country_code,
        pt.merchant_category_code,
        pi.counterparty_bank_country_code,
        pi.payment_rail_code
)
select
    {{ fraudlens_fact_sk([
        'mb.merchant_country_code',
        'mb.merchant_category_code',
        'mb.counterparty_bank_country_code',
        'mb.payment_rail_code'
    ]) }} as dim_merchant_sk,
    mb.merchant_country_code,
    mb.merchant_category_code,
    mb.counterparty_bank_country_code,
    mb.payment_rail_code,
    mb.ingestion_batch_id,
    mb.source_file_name,
    mb.ingested_at_utc,
    mb.pipeline_processed_at_utc,
    mb.lineage_run_id
from merchant_base as mb
