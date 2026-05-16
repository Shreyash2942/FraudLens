{{ config(alias='GOLD_DIM_DATE', tags=['gold', 'dim']) }}

select
    {{ fraudlens_fact_sk(['cast(cal.calendar_date as string)']) }} as dim_date_sk,
    cast(from_unixtime(unix_timestamp(cal.calendar_date), 'yyyyMMdd') as int) as date_key,
    cal.calendar_date,
    cal.calendar_year,
    cal.calendar_quarter,
    cal.calendar_month,
    cal.calendar_month_name,
    cal.week_of_year,
    cal.day_of_week,
    cal.day_name,
    cal.is_weekend,
    cal.is_month_end,
    cal.is_quarter_end,
    cal.is_holiday,
    cal.ingestion_batch_id,
    cal.source_file_name,
    cal.ingested_at_utc,
    cal.pipeline_processed_at_utc,
    cal.lineage_run_id
from {{ ref('slv__calendar_day') }} as cal
