{{ config(alias='GOLD_DIM_CARD', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['pc.card_id']) }} as dim_card_sk,
    pc.card_id,
    pc.linked_account_id as account_id,
    da.primary_party_id as customer_id,
    pc.card_status,
    pc.card_network_code,
    da.account_currency_code as linked_account_currency_code,
    pc.ingestion_batch_id,
    pc.source_file_name,
    pc.ingested_at_utc,
    pc.pipeline_processed_at_utc,
    pc.lineage_run_id
from {{ ref('slv__payment_card') }} as pc
left join {{ ref('slv__deposit_account') }} as da
    on pc.linked_account_id = da.deposit_account_id
