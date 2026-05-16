with violations as (
    select 'fact_transactions.transaction_date -> dim_date.calendar_date' as check_name
    from {{ ref('fact_transactions') }} ft
    left join {{ ref('dim_date') }} d on ft.transaction_date = d.calendar_date
    where ft.transaction_date is not null and d.calendar_date is null
    limit 1

    union all

    select 'fact_transactions.debtor_account_id -> dim_account.account_id' as check_name
    from {{ ref('fact_transactions') }} ft
    left join {{ ref('dim_account') }} a on ft.debtor_account_id = a.account_id
    where ft.debtor_account_id is not null and a.account_id is null
    limit 1

    union all

    select 'fact_transactions.card_id -> dim_card.card_id' as check_name
    from {{ ref('fact_transactions') }} ft
    left join {{ ref('dim_card') }} c on ft.card_id = c.card_id
    where ft.card_id is not null and c.card_id is null
    limit 1

    union all

    select 'fact_transactions.device_id -> dim_device.device_id' as check_name
    from {{ ref('fact_transactions') }} ft
    left join {{ ref('dim_device') }} d on ft.device_id = d.device_id
    where ft.device_id is not null and d.device_id is null
    limit 1

    union all

    select 'fact_transactions.channel_event_id -> dim_channel.channel_event_id' as check_name
    from {{ ref('fact_transactions') }} ft
    left join {{ ref('dim_channel') }} ch on ft.channel_event_id = ch.channel_event_id
    where ft.channel_event_id is not null and ch.channel_event_id is null
    limit 1

    union all

    select 'fact_fraud_alerts.alert_created_date -> dim_date.calendar_date' as check_name
    from {{ ref('fact_fraud_alerts') }} fa
    left join {{ ref('dim_date') }} d on fa.alert_created_date = d.calendar_date
    where fa.alert_created_date is not null and d.calendar_date is null
    limit 1

    union all

    select 'fact_fraud_alerts.owning_business_unit_id -> dim_business_unit.business_unit_id' as check_name
    from {{ ref('fact_fraud_alerts') }} fa
    left join {{ ref('dim_business_unit') }} bu on fa.owning_business_unit_id = bu.business_unit_id
    where fa.owning_business_unit_id is not null and bu.business_unit_id is null
    limit 1

    union all

    select 'fact_fraud_alerts.owning_analyst_team_id -> dim_analyst_team.analyst_team_id' as check_name
    from {{ ref('fact_fraud_alerts') }} fa
    left join {{ ref('dim_analyst_team') }} at on fa.owning_analyst_team_id = at.analyst_team_id
    where fa.owning_analyst_team_id is not null and at.analyst_team_id is null
    limit 1

    union all

    select 'fact_payment_events.payment_event_date -> dim_date.calendar_date' as check_name
    from {{ ref('fact_payment_events') }} pe
    left join {{ ref('dim_date') }} d on pe.payment_event_date = d.calendar_date
    where pe.payment_event_date is not null and d.calendar_date is null
    limit 1

    union all

    select 'fact_payment_events.card_id -> dim_card.card_id' as check_name
    from {{ ref('fact_payment_events') }} pe
    left join {{ ref('dim_card') }} c on pe.card_id = c.card_id
    where pe.card_id is not null and c.card_id is null
    limit 1

    union all

    select 'fact_payment_events.device_id -> dim_device.device_id' as check_name
    from {{ ref('fact_payment_events') }} pe
    left join {{ ref('dim_device') }} d on pe.device_id = d.device_id
    where pe.device_id is not null and d.device_id is null
    limit 1

    union all

    select 'fact_payment_events.channel_event_id -> dim_channel.channel_event_id' as check_name
    from {{ ref('fact_payment_events') }} pe
    left join {{ ref('dim_channel') }} ch on pe.channel_event_id = ch.channel_event_id
    where pe.channel_event_id is not null and ch.channel_event_id is null
    limit 1
)
select *
from violations
