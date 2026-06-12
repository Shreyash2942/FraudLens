{{ config(alias='bronze_stg_calendar_day', tags=['bronze', 'staging_raw']) }}

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
    {{ fraudlens_pipeline_audit_projection('src') }}
from {{ source('bronze', 'calendar_day') }} as src
{{ fraudlens_batch_where('src') }}
