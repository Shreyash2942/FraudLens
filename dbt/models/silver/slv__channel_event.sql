{{ config(alias='silver_channel_event', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.channel_event_id') }} as channel_event_id,
    {{ fraudlens_clean_text('src.channel_code', uppercase=true) }} as channel_code,
    {{ fraudlens_clean_text('src.session_id') }} as session_id,
    {{ fraudlens_clean_text('src.branch_id') }} as branch_id,
    {{ fraudlens_clean_timestamp('src.event_at') }} as event_at,
    {{ fraudlens_clean_text('src.event_country_code', uppercase=true) }} as event_country_code,
    {{ fraudlens_clean_text('src.ip_country_code', uppercase=true) }} as ip_country_code,
    {{ fraudlens_clean_text('src.authentication_result_code', uppercase=true) }} as authentication_result_code,
    {{ fraudlens_clean_text('src.session_risk_code', uppercase=true) }} as session_risk_code,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__channel_event') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.channel_event_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
)
select
    ranked.channel_event_id,
    ranked.channel_code,
    ranked.session_id,
    ranked.branch_id,
    ranked.event_at,
    ranked.event_country_code,
    ranked.ip_country_code,
    ranked.authentication_result_code,
    ranked.session_risk_code,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked.dedup_rank = 1
