{{ config(alias='SILVER_REGION', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.region_id') }} as region_id,
    {{ fraudlens_clean_text('src.region_code', uppercase=true) }} as region_code,
    {{ fraudlens_clean_text('src.region_name') }} as region_name,
    {{ fraudlens_clean_text('src.country_group_code', uppercase=true) }} as country_group_code,
    {{ fraudlens_clean_boolean('src.is_active') }} as is_active,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__region') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        case
            when standardized.region_id is not null then row_number() over (
                partition by standardized.region_id
                order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
            )
            else 1
        end as _dedup_rank
    from standardized
)
select
    ranked.region_id,
    ranked.region_code,
    ranked.region_name,
    ranked.country_group_code,
    ranked.is_active,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked._dedup_rank = 1
