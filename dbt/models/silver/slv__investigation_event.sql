{{ config(alias='SILVER_INVESTIGATION_EVENT', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.investigation_event_id') }} as investigation_event_id,
    {{ fraudlens_clean_text('src.fraud_case_id') }} as fraud_case_id,
    {{ fraudlens_clean_text('src.investigation_event_type', uppercase=true) }} as investigation_event_type,
    {{ fraudlens_clean_text('src.actor_party_id') }} as actor_party_id,
    {{ fraudlens_clean_timestamp('src.event_at') }} as event_at,
    {{ fraudlens_clean_text('src.event_result_code', uppercase=true) }} as event_result_code,
    {{ fraudlens_clean_int('src.elapsed_minutes') }} as elapsed_minutes,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__investigation_event') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        case
            when standardized.investigation_event_id is not null then row_number() over (
                partition by standardized.investigation_event_id
                order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
            )
            else 1
        end as _dedup_rank
    from standardized
)
select
    ranked.investigation_event_id,
    ranked.fraud_case_id,
    ranked.investigation_event_type,
    ranked.actor_party_id,
    ranked.event_at,
    ranked.event_result_code,
    ranked.elapsed_minutes,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked._dedup_rank = 1
