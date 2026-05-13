{{ config(alias='BRONZE_STG_CALENDAR_DAY', tags=['bronze', 'staging_raw']) }}

select
    src.CALENDAR_DATE as calendar_date,
    src.CALENDAR_YEAR as calendar_year,
    src.CALENDAR_QUARTER as calendar_quarter,
    src.CALENDAR_MONTH as calendar_month,
    src.CALENDAR_MONTH_NAME as calendar_month_name,
    src.WEEK_OF_YEAR as week_of_year,
    src.DAY_OF_WEEK as day_of_week,
    src.DAY_NAME as day_name,
    src.IS_WEEKEND as is_weekend,
    src.IS_MONTH_END as is_month_end,
    src.IS_QUARTER_END as is_quarter_end,
    src.IS_HOLIDAY as is_holiday,
    src.INGESTION_BATCH_ID as ingestion_batch_id,
    src.SOURCE_FILE_NAME as source_file_name,
    src.INGESTED_AT_UTC as ingested_at_utc
from {{ source('bronze', 'calendar_day') }} as src
{{ fraudlens_batch_where('src') }}
