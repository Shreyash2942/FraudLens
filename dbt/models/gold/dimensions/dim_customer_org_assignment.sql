{{ config(alias='gold_dim_customer_org_assignment', tags=['gold', 'dim']) }}

with base as (
    select
        poa.party_org_assignment_id,
        poa.party_id as customer_id,
        poa.assignment_role_code,
        poa.business_unit_id,
        bu.business_unit_code,
        bu.business_unit_name,
        poa.analyst_team_id,
        at.analyst_team_code,
        at.analyst_team_name,
        poa.branch_id,
        bl.branch_code,
        bl.branch_name,
        poa.effective_from_at,
        poa.effective_to_at,
        case when poa.effective_to_at is null then true else false end as is_current_assignment,
        poa.ingestion_batch_id,
        poa.source_file_name,
        poa.ingested_at_utc,
        poa.pipeline_processed_at_utc,
        poa.lineage_run_id
    from {{ ref('slv__party_org_assignment') }} as poa
    left join {{ ref('slv__business_unit') }} as bu
        on poa.business_unit_id = bu.business_unit_id
    left join {{ ref('slv__analyst_team') }} as at
        on poa.analyst_team_id = at.analyst_team_id
    left join {{ ref('slv__branch_location') }} as bl
        on poa.branch_id = bl.branch_id
),
sequenced as (
    select
        base.*,
        row_number() over (
            partition by base.customer_id, base.assignment_role_code
            order by base.effective_from_at desc, base.effective_to_at desc, base.party_org_assignment_id desc
        ) as assignment_version_rank
    from base
)
select
    {{ fraudlens_fact_sk(['seq.party_org_assignment_id']) }} as dim_customer_org_assignment_sk,
    seq.party_org_assignment_id,
    seq.customer_id,
    seq.assignment_role_code,
    seq.business_unit_id,
    seq.business_unit_code,
    seq.business_unit_name,
    seq.analyst_team_id,
    seq.analyst_team_code,
    seq.analyst_team_name,
    seq.branch_id,
    seq.branch_code,
    seq.branch_name,
    seq.effective_from_at,
    seq.effective_to_at,
    seq.is_current_assignment,
    seq.assignment_version_rank,
    seq.ingestion_batch_id,
    seq.source_file_name,
    seq.ingested_at_utc,
    seq.pipeline_processed_at_utc,
    seq.lineage_run_id
from sequenced as seq
