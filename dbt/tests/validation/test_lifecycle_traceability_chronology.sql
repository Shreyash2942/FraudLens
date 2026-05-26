{{ config(tags=['quality', 'quality_critical', 'governance_critical', 'contract_critical', 'audit_critical', 'validation_critical']) }}

with violations as (
    select
        'slv__fraud_alert_created_before_updated' as check_name,
        count(*) as violation_count
    from {{ ref('slv__fraud_alert') }} as fa
    where fa.created_at_utc is not null
      and fa.updated_at_utc is not null
      and fa.updated_at_utc < fa.created_at_utc

    union all

    select
        'slv__fraud_case_open_after_alert_created' as check_name,
        count(*) as violation_count
    from {{ ref('slv__fraud_case') }} as fc
    inner join {{ ref('slv__fraud_alert') }} as fa
        on fc.primary_alert_id = fa.fraud_alert_id
    where fc.opened_at is not null
      and fa.created_at is not null
      and fc.opened_at < fa.created_at

    union all

    select
        'slv__decision_record_decided_after_case_open' as check_name,
        count(*) as violation_count
    from {{ ref('slv__decision_record') }} as dr
    inner join {{ ref('slv__fraud_case') }} as fc
        on dr.fraud_case_id = fc.fraud_case_id
    where dr.decided_at is not null
      and fc.opened_at is not null
      and dr.decided_at < fc.opened_at

    union all

    select
        'slv__case_disposition_outcome_after_decision' as check_name,
        count(*) as violation_count
    from {{ ref('slv__case_disposition') }} as cd
    inner join {{ ref('slv__decision_record') }} as dr
        on cd.decision_id = dr.decision_id
    where cd.outcome_at is not null
      and dr.decided_at is not null
      and cd.outcome_at < dr.decided_at

    union all

    select
        'fact_fraud_alerts_minutes_to_case_open_non_negative' as check_name,
        count(*) as violation_count
    from {{ ref('fact_fraud_alerts') }} as fa
    where fa.minutes_to_case_open is not null
      and fa.minutes_to_case_open < 0
)
select *
from violations
where violation_count > 0
