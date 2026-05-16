{{ config(alias='GOLD_DIM_CUSTOMER', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['p.party_id']) }} as dim_customer_sk,
    p.party_id as customer_id,
    p.party_type,
    p.party_status,
    p.customer_type_code,
    p.customer_segment_code,
    p.risk_segment_code,
    p.industry_sector_code,
    p.domicile_country_code,
    p.residency_region_id,
    r.region_code as residency_region_code,
    r.region_name as residency_region_name,
    p.customer_since_at,
    p.ingestion_batch_id,
    p.source_file_name,
    p.ingested_at_utc,
    p.pipeline_processed_at_utc,
    p.lineage_run_id
from {{ ref('slv__party') }} as p
left join {{ ref('slv__region') }} as r
    on p.residency_region_id = r.region_id
