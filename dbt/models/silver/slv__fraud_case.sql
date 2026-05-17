{{ config(alias='SILVER_FRAUD_CASE', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.fraud_case_id') }} as fraud_case_id,
    {{ fraudlens_clean_text('src.primary_alert_id') }} as primary_alert_id,
    {{ fraudlens_clean_text('src.case_status', uppercase=true) }} as case_status,
    {{ fraudlens_clean_text('src.assigned_analyst_party_id') }} as assigned_analyst_party_id,
    {{ fraudlens_clean_timestamp('src.opened_at') }} as opened_at,
    {{ fraudlens_clean_timestamp('src.closed_at') }} as closed_at,
    {{ fraudlens_clean_text('src.case_type_code', uppercase=true) }} as case_type_code,
    {{ fraudlens_clean_text('src.case_priority_code', uppercase=true) }} as case_priority_code,
    {{ fraudlens_clean_text('src.owning_business_unit_id') }} as owning_business_unit_id,
    {{ fraudlens_clean_text('src.owning_analyst_team_id') }} as owning_analyst_team_id,
    {{ fraudlens_clean_text('src.handling_region_id') }} as handling_region_id,
    {{ fraudlens_clean_text('src.escalation_level_code', uppercase=true) }} as escalation_level_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__fraud_case') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.fraud_case_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
),
business_safe as (
    select
        ranked.fraud_case_id,
        ranked.primary_alert_id,
        ranked.case_status,
        ranked.assigned_analyst_party_id,
        ranked.opened_at,
        case
            when ranked.closed_at is not null
             and ranked.opened_at is not null
             and ranked.closed_at < ranked.opened_at then null
            else ranked.closed_at
        end as closed_at,
        ranked.case_type_code,
        ranked.case_priority_code,
        ranked.owning_business_unit_id,
        ranked.owning_analyst_team_id,
        ranked.handling_region_id,
        ranked.escalation_level_code,
        ranked.ingestion_batch_id,
        ranked.source_file_name,
        ranked.ingested_at_utc,
        ranked.pipeline_processed_at_utc,
        ranked.lineage_run_id
    from ranked
    where ranked.dedup_rank = 1
)
select
    business_safe.fraud_case_id,
    business_safe.primary_alert_id,
    business_safe.case_status,
    business_safe.assigned_analyst_party_id,
    business_safe.opened_at,
    business_safe.closed_at,
    business_safe.case_type_code,
    business_safe.case_priority_code,
    business_safe.owning_business_unit_id,
    business_safe.owning_analyst_team_id,
    business_safe.handling_region_id,
    business_safe.escalation_level_code,
    business_safe.ingestion_batch_id,
    business_safe.source_file_name,
    business_safe.ingested_at_utc,
    business_safe.pipeline_processed_at_utc,
    business_safe.lineage_run_id
from business_safe
