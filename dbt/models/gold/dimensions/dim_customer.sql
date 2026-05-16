{{ config(alias='GOLD_DIM_CUSTOMER', tags=['gold', 'dim']) }}

with current_assignment as (
    select
        poa.party_id as customer_id,
        poa.business_unit_id,
        bu.business_unit_code,
        bu.business_unit_name,
        poa.analyst_team_id,
        at.analyst_team_code,
        at.analyst_team_name,
        poa.branch_id,
        bl.branch_code,
        bl.branch_name,
        row_number() over (
            partition by poa.party_id
            order by poa.effective_from_at desc, poa.effective_to_at desc, poa.party_org_assignment_id desc
        ) as assignment_rank
    from {{ ref('slv__party_org_assignment') }} as poa
    left join {{ ref('slv__business_unit') }} as bu
        on poa.business_unit_id = bu.business_unit_id
    left join {{ ref('slv__analyst_team') }} as at
        on poa.analyst_team_id = at.analyst_team_id
    left join {{ ref('slv__branch_location') }} as bl
        on poa.branch_id = bl.branch_id
)
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
    ca.business_unit_id as current_business_unit_id,
    ca.business_unit_code as current_business_unit_code,
    ca.business_unit_name as current_business_unit_name,
    ca.analyst_team_id as current_analyst_team_id,
    ca.analyst_team_code as current_analyst_team_code,
    ca.analyst_team_name as current_analyst_team_name,
    ca.branch_id as current_branch_id,
    ca.branch_code as current_branch_code,
    ca.branch_name as current_branch_name,
    p.customer_since_at,
    p.ingestion_batch_id,
    p.source_file_name,
    p.ingested_at_utc,
    p.pipeline_processed_at_utc,
    p.lineage_run_id
from {{ ref('slv__party') }} as p
left join {{ ref('slv__region') }} as r
    on p.residency_region_id = r.region_id
left join current_assignment as ca
    on p.party_id = ca.customer_id
   and ca.assignment_rank = 1
