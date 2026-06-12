{{ config(alias='silver_party', tags=['silver', 'conformed']) }}

with standardized as (
    select
    {{ fraudlens_clean_text('src.party_id') }} as party_id,
    {{ fraudlens_clean_text('src.party_type', uppercase=true) }} as party_type,
    {{ fraudlens_clean_text('src.party_status', uppercase=true) }} as party_status,
    {{ fraudlens_clean_text('src.domicile_country_code', uppercase=true) }} as domicile_country_code,
    {{ fraudlens_clean_text('src.risk_segment_code', uppercase=true) }} as risk_segment_code,
    {{ fraudlens_clean_text('src.customer_segment_code', uppercase=true) }} as customer_segment_code,
    {{ fraudlens_clean_text('src.customer_type_code', uppercase=true) }} as customer_type_code,
    {{ fraudlens_clean_text('src.industry_sector_code', uppercase=true) }} as industry_sector_code,
    {{ fraudlens_clean_text('src.residency_region_id') }} as residency_region_id,
    {{ fraudlens_clean_timestamp('src.customer_since_at') }} as customer_since_at,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
    from {{ ref('stg_bronze__party') }} as src
    {{ fraudlens_batch_where('src') }}
),
ranked as (
    select
        standardized.*,
        row_number() over (
            partition by standardized.party_id
            order by standardized.ingested_at_utc desc, standardized.pipeline_processed_at_utc desc, standardized.source_file_name desc
        ) as dedup_rank
    from standardized
)
select
    ranked.party_id,
    ranked.party_type,
    ranked.party_status,
    ranked.domicile_country_code,
    ranked.risk_segment_code,
    ranked.customer_segment_code,
    ranked.customer_type_code,
    ranked.industry_sector_code,
    ranked.residency_region_id,
    ranked.customer_since_at,
    ranked.ingestion_batch_id,
    ranked.source_file_name,
    ranked.ingested_at_utc,
    ranked.pipeline_processed_at_utc,
    ranked.lineage_run_id
from ranked
where ranked.dedup_rank = 1
