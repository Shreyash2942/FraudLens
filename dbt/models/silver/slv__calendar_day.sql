{{ config(alias='SILVER_CALENDAR_DAY', tags=['silver', 'conformed']) }}

select
    {{ fraudlens_clean_date('src.calendar_date') }} as calendar_date,
    {{ fraudlens_clean_int('src.calendar_year') }} as calendar_year,
    {{ fraudlens_clean_int('src.calendar_quarter') }} as calendar_quarter,
    {{ fraudlens_clean_int('src.calendar_month') }} as calendar_month,
    {{ fraudlens_clean_text('src.calendar_month_name') }} as calendar_month_name,
    {{ fraudlens_clean_int('src.week_of_year') }} as week_of_year,
    {{ fraudlens_clean_int('src.day_of_week') }} as day_of_week,
    {{ fraudlens_clean_text('src.day_name') }} as day_name,
    {{ fraudlens_clean_boolean('src.is_weekend') }} as is_weekend,
    {{ fraudlens_clean_boolean('src.is_month_end') }} as is_month_end,
    {{ fraudlens_clean_boolean('src.is_quarter_end') }} as is_quarter_end,
    {{ fraudlens_clean_boolean('src.is_holiday') }} as is_holiday,
    {{ fraudlens_clean_text('src.ingestion_batch_id') }} as ingestion_batch_id,
    {{ fraudlens_clean_text('src.source_file_name') }} as source_file_name,
    {{ fraudlens_clean_timestamp('src.ingested_at_utc') }} as ingested_at_utc,
    {{ fraudlens_clean_timestamp('src.pipeline_processed_at_utc') }} as pipeline_processed_at_utc,
    {{ fraudlens_clean_text('src.lineage_run_id') }} as lineage_run_id
from {{ ref('stg_bronze__calendar_day') }} as src
{{ fraudlens_batch_where('src') }}
