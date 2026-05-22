{{ config(alias='SILVER_CASE_DISPOSITION', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.disposition_id') }} as disposition_id,
    {{ fraudlens_clean_text('src.decision_id') }} as decision_id,
    {{ fraudlens_clean_text('src.disposition_code', uppercase=true) }} as disposition_code,
    {{ fraudlens_clean_decimal('src.financial_impact_amount') }} as financial_impact_amount,
    {{ fraudlens_clean_timestamp('src.outcome_at') }} as outcome_at,
    {{ fraudlens_clean_decimal('src.loss_amount') }} as loss_amount,
    {{ fraudlens_clean_decimal('src.recovered_amount') }} as recovered_amount,
    {{ fraudlens_clean_decimal('src.write_off_amount') }} as write_off_amount,
    {{ fraudlens_clean_text('src.recovery_status_code', uppercase=true) }} as recovery_status_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    coalesce(
        {{ fraudlens_clean_timestamp('src.outcome_at') }},
        {{ fraudlens_clean_timestamp('src.created_at_utc') }},
        {{ fraudlens_clean_timestamp('src.ingested_at_utc') }}
    ) as created_at_utc,
    coalesce(
        {{ fraudlens_clean_timestamp('src.updated_at_utc') }},
        {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }}
    ) as updated_at_utc,
    {{ fraudlens_clean_text('src.source_system') }} as source_system,
    {{ fraudlens_clean_text('src.pipeline_run_id') }} as pipeline_run_id,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__case_disposition') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.disposition_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
)
select
    ranked.disposition_id,
    ranked.decision_id,
    ranked.disposition_code,
    ranked.financial_impact_amount,
    ranked.outcome_at,
    ranked.loss_amount,
    ranked.recovered_amount,
    ranked.write_off_amount,
    ranked.recovery_status_code,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.created_at_utc,
    ranked.updated_at_utc,
    ranked.source_system,
    ranked.pipeline_run_id,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked.dedup_rank = 1
