with invalid_cases as (
    select
        'fraud_case' as rule_name,
        fraud_case_id as record_id
    from {{ ref('slv__fraud_case') }}
    where closed_at is not null
      and opened_at is not null
      and closed_at < opened_at

    union all

    select
        'deposit_account' as rule_name,
        deposit_account_id as record_id
    from {{ ref('slv__deposit_account') }}
    where closed_at is not null
      and opened_at is not null
      and closed_at < opened_at

    union all

    select
        'party_org_assignment' as rule_name,
        party_org_assignment_id as record_id
    from {{ ref('slv__party_org_assignment') }}
    where effective_to_at is not null
      and effective_from_at is not null
      and effective_to_at < effective_from_at

    union all

    select
        'investigation_event' as rule_name,
        investigation_event_id as record_id
    from {{ ref('slv__investigation_event') }}
    where elapsed_minutes is not null
      and elapsed_minutes < 0
)
select *
from invalid_cases
