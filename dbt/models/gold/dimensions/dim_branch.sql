{{ config(alias='GOLD_DIM_BRANCH', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['bl.branch_id']) }} as dim_branch_sk,
    bl.branch_id,
    bl.branch_code,
    bl.branch_name,
    bl.branch_territory_id,
    bt.branch_territory_code,
    bt.branch_territory_name,
    coalesce(bl.region_id, bt.region_id) as region_id,
    r.region_code,
    r.region_name,
    bt.is_active as branch_territory_is_active,
    r.is_active as region_is_active,
    case
        when bl.is_active and coalesce(bt.is_active, true) and coalesce(r.is_active, true) then true
        else false
    end as is_hierarchy_active,
    bl.country_code,
    bl.city_name,
    bl.is_active,
    bl.ingestion_batch_id,
    bl.source_file_name,
    bl.ingested_at_utc,
    bl.pipeline_processed_at_utc,
    bl.lineage_run_id
from {{ ref('slv__branch_location') }} as bl
left join {{ ref('slv__branch_territory') }} as bt
    on bl.branch_territory_id = bt.branch_territory_id
left join {{ ref('slv__region') }} as r
    on coalesce(bl.region_id, bt.region_id) = r.region_id
