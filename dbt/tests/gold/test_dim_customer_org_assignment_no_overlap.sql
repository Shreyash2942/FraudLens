with assignments as (
    select
        customer_id,
        assignment_role_code,
        coalesce(effective_from_at, cast('1900-01-01 00:00:00' as timestamp)) as effective_from_at,
        coalesce(effective_to_at, cast('2999-12-31 23:59:59' as timestamp)) as effective_to_at,
        party_org_assignment_id
    from {{ ref('dim_customer_org_assignment') }}
),
overlaps as (
    select
        a.customer_id,
        a.assignment_role_code,
        a.party_org_assignment_id as assignment_id_a,
        b.party_org_assignment_id as assignment_id_b
    from assignments as a
    join assignments as b
        on a.customer_id = b.customer_id
       and a.assignment_role_code = b.assignment_role_code
       and a.party_org_assignment_id < b.party_org_assignment_id
       and a.effective_from_at <= b.effective_to_at
       and b.effective_from_at <= a.effective_to_at
)
select *
from overlaps
