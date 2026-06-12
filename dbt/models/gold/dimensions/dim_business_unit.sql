{{ config(alias='gold_dim_business_unit', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['bu.business_unit_id']) }} as dim_business_unit_sk,
    bu.business_unit_id,
    bu.business_unit_code,
    bu.business_unit_name,
    bu.business_unit_type,
    bu.region_id,
    r.region_code,
    r.region_name,
    bu.is_active,
    bu.ingestion_batch_id,
    bu.source_file_name,
    bu.ingested_at_utc,
    bu.pipeline_processed_at_utc,
    bu.lineage_run_id
from {{ ref('slv__business_unit') }} as bu
left join {{ ref('slv__region') }} as r
    on bu.region_id = r.region_id
