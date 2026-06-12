{{ config(alias='gold_dim_account', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['da.deposit_account_id']) }} as dim_account_sk,
    da.deposit_account_id as account_id,
    da.account_status,
    da.product_type_code,
    da.primary_party_id as customer_id,
    p.customer_type_code,
    p.customer_segment_code,
    da.account_currency_code,
    da.available_balance_amount,
    da.opened_at,
    da.closed_at,
    da.opened_branch_id as branch_id,
    bl.branch_code,
    bl.branch_name,
    da.servicing_business_unit_id as business_unit_id,
    bu.business_unit_code,
    bu.business_unit_name,
    da.account_region_id as region_id,
    r.region_code,
    r.region_name,
    da.ingestion_batch_id,
    da.source_file_name,
    da.ingested_at_utc,
    da.pipeline_processed_at_utc,
    da.lineage_run_id
from {{ ref('slv__deposit_account') }} as da
left join {{ ref('slv__party') }} as p
    on da.primary_party_id = p.party_id
left join {{ ref('slv__branch_location') }} as bl
    on da.opened_branch_id = bl.branch_id
left join {{ ref('slv__business_unit') }} as bu
    on da.servicing_business_unit_id = bu.business_unit_id
left join {{ ref('slv__region') }} as r
    on da.account_region_id = r.region_id
