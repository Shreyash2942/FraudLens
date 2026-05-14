{{ config(alias='SILVER_BUSINESS_UNIT', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.business_unit_id') }} as business_unit_id,
    {{ fraudlens_clean_text('src.business_unit_code', uppercase=true) }} as business_unit_code,
    {{ fraudlens_clean_text('src.business_unit_name') }} as business_unit_name,
    {{ fraudlens_clean_text('src.business_unit_type', uppercase=true) }} as business_unit_type,
    {{ fraudlens_clean_text('src.region_id') }} as region_id,
    {{ fraudlens_clean_boolean('src.is_active') }} as is_active,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__business_unit') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        case
            when standardized.business_unit_id is not null then row_number() over (
                partition by standardized.business_unit_id
                order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
            )
            else 1
        end as _dedup_rank
    from standardized
)
select
    ranked.business_unit_id,
    ranked.business_unit_code,
    ranked.business_unit_name,
    ranked.business_unit_type,
    ranked.region_id,
    ranked.is_active,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked._dedup_rank = 1
