{{ config(alias='SILVER_PARTY_ORG_ASSIGNMENT', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.party_org_assignment_id') }} as party_org_assignment_id,
    {{ fraudlens_clean_text('src.party_id') }} as party_id,
    {{ fraudlens_clean_text('src.business_unit_id') }} as business_unit_id,
    {{ fraudlens_clean_text('src.analyst_team_id') }} as analyst_team_id,
    {{ fraudlens_clean_text('src.branch_id') }} as branch_id,
    {{ fraudlens_clean_text('src.assignment_role_code', uppercase=true) }} as assignment_role_code,
    {{ fraudlens_clean_timestamp('src.effective_from_at') }} as effective_from_at,
    {{ fraudlens_clean_timestamp('src.effective_to_at') }} as effective_to_at,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__party_org_assignment') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.party_org_assignment_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
),
business_safe as (
    select
        ranked.party_org_assignment_id,
        ranked.party_id,
        ranked.business_unit_id,
        ranked.analyst_team_id,
        ranked.branch_id,
        ranked.assignment_role_code,
        ranked.effective_from_at,
        case
            when ranked.effective_to_at is not null
             and ranked.effective_from_at is not null
             and ranked.effective_to_at < ranked.effective_from_at then null
            else ranked.effective_to_at
        end as effective_to_at,
        ranked.ingestion_batch_id,
        ranked.source_file_name,
        ranked.ingested_at_utc,
        ranked.pipeline_processed_at_utc,
        ranked.lineage_run_id
    from ranked
    where ranked.dedup_rank = 1
)
select
    business_safe.party_org_assignment_id,
    business_safe.party_id,
    business_safe.business_unit_id,
    business_safe.analyst_team_id,
    business_safe.branch_id,
    business_safe.assignment_role_code,
    business_safe.effective_from_at,
    business_safe.effective_to_at,
    business_safe.ingestion_batch_id,
    business_safe.source_file_name,
    business_safe.ingested_at_utc,
    business_safe.pipeline_processed_at_utc,
    business_safe.lineage_run_id
from business_safe
