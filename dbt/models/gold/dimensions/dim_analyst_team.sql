{{ config(alias='gold_dim_analyst_team', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['at.analyst_team_id']) }} as dim_analyst_team_sk,
    at.analyst_team_id,
    at.analyst_team_code,
    at.analyst_team_name,
    at.business_unit_id,
    bu.business_unit_code,
    bu.business_unit_name,
    at.region_id,
    r.region_code,
    r.region_name,
    at.is_active,
    at.ingestion_batch_id,
    at.source_file_name,
    at.ingested_at_utc,
    at.pipeline_processed_at_utc,
    at.lineage_run_id
from {{ ref('slv__analyst_team') }} as at
left join {{ ref('slv__business_unit') }} as bu
    on at.business_unit_id = bu.business_unit_id
left join {{ ref('slv__region') }} as r
    on at.region_id = r.region_id
