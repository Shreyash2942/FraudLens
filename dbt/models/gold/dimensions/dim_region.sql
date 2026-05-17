{{ config(alias='GOLD_DIM_REGION', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['r.region_id']) }} as dim_region_sk,
    r.region_id,
    r.region_code,
    r.region_name,
    r.country_group_code,
    r.is_active,
    r.ingestion_batch_id,
    r.source_file_name,
    r.ingested_at_utc,
    r.pipeline_processed_at_utc,
    r.lineage_run_id
from {{ ref('slv__region') }} as r
