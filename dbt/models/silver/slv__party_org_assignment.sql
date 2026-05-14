{{ config(alias='SILVER_PARTY_ORG_ASSIGNMENT', tags=['silver', 'conformed']) }}

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
