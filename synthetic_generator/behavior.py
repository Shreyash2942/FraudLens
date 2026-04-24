from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import calendar
import random

from .contracts import (
    ACCOUNT_PRODUCTS,
    ALERT_SOURCE_CODES,
    ALERT_TYPE_CODES,
    ASSIGNMENT_ROLE_CODES,
    AUTHENTICATION_RESULTS,
    BUSINESS_UNIT_TYPES,
    CARD_NETWORKS,
    CHANNELS,
    COUNTRIES,
    COUNTRY_GROUPS,
    CUSTOMER_SEGMENTS,
    CUSTOMER_TYPES,
    DECISION_CHANNEL_CODES,
    DECISION_REASON_CODES,
    DEVICE_OSES,
    ESCALATION_LEVEL_CODES,
    EVENT_RESULT_CODES,
    INDUSTRY_SECTORS,
    MERCHANT_CATEGORIES,
    PAYMENT_PURPOSES,
    PAYMENT_RAIL_CODES,
    RECOVERY_STATUS_CODES,
    SESSION_RISK_CODES,
    TRANSACTION_DIRECTION_CODES,
    ScaleProfile,
)
from .progress import ProgressReporter
from .state import (
    AccountProfile,
    AnalystTeamProfile,
    BranchLocationProfile,
    BranchTerritoryProfile,
    BusinessUnitProfile,
    CardProfile,
    CustomerProfile,
    DeviceProfileInternal,
    GenerationState,
    MerchantProfile,
    PartyOrgAssignmentProfile,
    PaymentMeta,
    RecurringBill,
    RegionProfile,
)
from .utils import (
    SequenceIdGenerator,
    bounded_normal_amount,
    isoformat_utc,
    random_datetime_between,
    random_datetime_on_due_day,
    random_session_id,
)


COUNTRY_GROUP_MAP = {
    "north_america": ["US", "CA"],
    "europe": ["GB", "DE", "FR", "NL"],
    "asia_pacific": ["IN", "AU", "SG"],
    "middle_east": ["AE"],
}


def build_reference_data(state: GenerationState, profile: ScaleProfile) -> None:
    code_sets = {
        "party_type": ["individual", "organization", "merchant", "analyst", "service"],
        "party_status": ["active", "inactive", "restricted", "closed"],
        "account_status": ["open", "dormant", "blocked", "closed", "suspended"],
        "product_type_code": ACCOUNT_PRODUCTS,
        "currency_code": ["USD", "EUR", "GBP", "CAD"],
        "card_status": ["active", "blocked", "expired", "reissued", "closed"],
        "card_network_code": CARD_NETWORKS,
        "device_status": ["trusted", "known", "new", "risky", "blocked"],
        "device_risk_band": ["low", "medium", "high", "severe"],
        "channel_code": CHANNELS,
        "instruction_status": ["pending", "accepted", "rejected", "cancelled", "expired"],
        "transaction_status": ["booked", "pending_settlement", "reversed", "declined", "returned"],
        "risk_level": ["low", "medium", "high", "severe"],
        "alert_status": ["open", "triaged", "escalated", "resolved", "cancelled"],
        "alert_severity": ["low", "medium", "high", "critical"],
        "case_status": ["open", "assigned", "investigating", "pending_decision", "closed"],
        "investigation_event_type": ["note_added", "evidence_attached", "outreach_attempted", "review_completed", "escalation"],
        "decision_type": ["approve", "decline", "hold", "challenge", "file_sar", "close_no_fraud"],
        "decision_status": ["proposed", "approved", "executed", "superseded"],
        "disposition_code": ["confirmed_fraud", "false_positive", "customer_error", "recovered", "written_off"],
        "country_code": COUNTRIES,
        "country_group_code": COUNTRY_GROUPS,
        "payment_purpose_code": PAYMENT_PURPOSES,
        "merchant_category_code": MERCHANT_CATEGORIES,
        "customer_segment_code": CUSTOMER_SEGMENTS,
        "customer_type_code": CUSTOMER_TYPES,
        "industry_sector_code": INDUSTRY_SECTORS,
        "risk_segment_code": ["low", "medium", "high", "severe"],
        "queue_code": ["fraud_ops", "high_risk", "manual_review", "customer_care"],
        "signal_type_code": [
            "account_takeover",
            "card_not_present",
            "mule_transfer",
            "burst_velocity",
            "repeat_offender",
            "suspicious_new_device",
            "false_positive",
            "rule_high_value",
            "rule_new_payee",
        ],
        "business_unit_type": BUSINESS_UNIT_TYPES,
        "assignment_role_code": ASSIGNMENT_ROLE_CODES,
        "authentication_result_code": AUTHENTICATION_RESULTS,
        "session_risk_code": SESSION_RISK_CODES,
        "payment_rail_code": PAYMENT_RAIL_CODES,
        "transaction_direction_code": TRANSACTION_DIRECTION_CODES,
        "alert_type_code": ALERT_TYPE_CODES,
        "alert_source_code": ALERT_SOURCE_CODES,
        "case_type_code": ["account_takeover", "payment_fraud", "card_fraud", "mule_network", "review_case"],
        "case_priority_code": ["p1", "p2", "p3", "p4"],
        "escalation_level_code": ESCALATION_LEVEL_CODES,
        "event_result_code": EVENT_RESULT_CODES,
        "decision_reason_code": DECISION_REASON_CODES,
        "decision_channel_code": DECISION_CHANNEL_CODES,
        "recovery_status_code": RECOVERY_STATUS_CODES,
    }
    rows = []
    for code_set_name, values in code_sets.items():
        for value in values:
            rows.append(
                {
                    "code_set_name": code_set_name,
                    "code_value": value,
                    "code_description": _reference_description(state, code_set_name, value),
                    "is_active": "true",
                }
            )
    while len(rows) < profile.reference_rows:
        index = len(rows) + 1
        rows.append(
            {
                "code_set_name": "synthetic_control",
                "code_value": f"CTRL_{index:03d}",
                "code_description": f"Synthetic control code {index}: {state.fake.bs().capitalize()}",
                "is_active": "true",
            }
        )
    state.datasets["reference_data_catalog"] = rows[: profile.reference_rows]


def build_calendar_day(state: GenerationState) -> None:
    rows = []
    cursor = state.start_at.date()
    end_date = state.end_at.date()
    holidays = {date(cursor.year, 1, 1), date(cursor.year, 7, 4), date(cursor.year, 12, 25)}
    while cursor <= end_date:
        next_day = cursor + timedelta(days=1)
        rows.append(
            {
                "calendar_date": cursor.isoformat(),
                "calendar_year": str(cursor.year),
                "calendar_quarter": f"Q{((cursor.month - 1) // 3) + 1}",
                "calendar_month": str(cursor.month),
                "calendar_month_name": calendar.month_name[cursor.month],
                "week_of_year": str(cursor.isocalendar().week),
                "day_of_week": str(cursor.isoweekday()),
                "day_name": calendar.day_name[cursor.weekday()],
                "is_weekend": _bool_string(cursor.weekday() >= 5),
                "is_month_end": _bool_string(next_day.month != cursor.month),
                "is_quarter_end": _bool_string(next_day.month in {1, 4, 7, 10} and next_day.day == 1),
                "is_holiday": _bool_string(cursor in holidays),
            }
        )
        cursor = next_day
    state.calendar_rows = rows
    state.datasets["calendar_day"] = rows


def build_regions(state: GenerationState, profile: ScaleProfile) -> None:
    region_id = SequenceIdGenerator("REG")
    rows = []
    templates = [
        ("NAM_EAST", "North America East", "north_america"),
        ("NAM_WEST", "North America West", "north_america"),
        ("EUR_CORE", "Europe Core", "europe"),
        ("EUR_NORTH", "Europe North", "europe"),
        ("APAC_NORTH", "APAC North", "asia_pacific"),
        ("APAC_SOUTH", "APAC South", "asia_pacific"),
        ("MEA_CORE", "Middle East Core", "middle_east"),
        ("GLOBAL_SPECIAL", "Global Special Programs", "north_america"),
    ]
    region_mix_keys = _ordered_region_templates(templates, state.generation_context.get("geography_controls", {}), profile.region_count)
    for index in range(profile.region_count):
        template_index = region_mix_keys[index]
        code, name, group = templates[template_index]
        rid = region_id.next()
        state.region_profiles[rid] = RegionProfile(rid, code, name, group)
        state.region_ids.append(rid)
        rows.append(
            {
                "region_id": rid,
                "region_code": code,
                "region_name": name,
                "country_group_code": group,
                "is_active": "true",
            }
        )
    state.datasets["region"] = rows


def build_branch_territories(state: GenerationState, profile: ScaleProfile) -> None:
    territory_id = SequenceIdGenerator("TER")
    rows = []
    for index in range(profile.branch_territory_count):
        if index < len(state.region_ids):
            region_id = state.region_ids[index]
        else:
            region_id = _choose_region_id(state)
        region = state.region_profiles[region_id]
        tid = territory_id.next()
        code = f"{region.region_code}_T{index + 1:02d}"
        name = f"{region.region_name} Territory {index + 1:02d}"
        state.branch_territory_profiles[tid] = BranchTerritoryProfile(tid, code, name, region_id)
        rows.append(
            {
                "branch_territory_id": tid,
                "branch_territory_code": code,
                "branch_territory_name": name,
                "region_id": region_id,
                "is_active": "true",
            }
        )
    state.datasets["branch_territory"] = rows


def build_branch_locations(state: GenerationState, profile: ScaleProfile) -> None:
    branch_id = SequenceIdGenerator("BR")
    territory_ids = list(state.branch_territory_profiles)
    rows = []
    for index in range(profile.branch_count):
        if index < len(territory_ids):
            territory = state.branch_territory_profiles[territory_ids[index]]
        else:
            territory = state.branch_territory_profiles[_choose_branch_territory_id(state, territory_ids)]
        region = state.region_profiles[territory.region_id]
        bid = branch_id.next()
        code = f"{territory.branch_territory_code}_{index + 1:03d}"
        country_code = state.rng.choice(COUNTRY_GROUP_MAP[region.country_group_code])
        city_name = state.fake.city()
        state.branch_location_profiles[bid] = BranchLocationProfile(
            branch_id=bid,
            branch_code=code,
            branch_name=f"{city_name} Branch",
            branch_territory_id=territory.branch_territory_id,
            region_id=territory.region_id,
            country_code=country_code,
            city_name=city_name,
        )
        state.branch_ids.append(bid)
        rows.append(
            {
                "branch_id": bid,
                "branch_code": code,
                "branch_name": f"{city_name} Branch",
                "branch_territory_id": territory.branch_territory_id,
                "region_id": territory.region_id,
                "country_code": country_code,
                "city_name": city_name,
                "is_active": "true",
            }
        )
    state.datasets["branch_location"] = rows


def build_business_units(state: GenerationState, profile: ScaleProfile) -> None:
    business_unit_id = SequenceIdGenerator("BU")
    rows = []
    for index in range(profile.business_unit_count):
        if index < len(state.region_ids):
            region_id = state.region_ids[index]
        else:
            region_id = _choose_region_id(state)
        bu_type = _choose_business_unit_type(state, index)
        buid = business_unit_id.next()
        code = f"{bu_type[:3].upper()}_{index + 1:02d}"
        name = f"{bu_type.replace('_', ' ').title()} Unit {index + 1:02d}"
        state.business_unit_profiles[buid] = BusinessUnitProfile(buid, code, name, bu_type, region_id)
        state.business_unit_ids.append(buid)
        rows.append(
            {
                "business_unit_id": buid,
                "business_unit_code": code,
                "business_unit_name": name,
                "business_unit_type": bu_type,
                "region_id": region_id,
                "is_active": "true",
            }
        )
    state.datasets["business_unit"] = rows


def build_analyst_teams(state: GenerationState, profile: ScaleProfile) -> None:
    analyst_team_id = SequenceIdGenerator("ATM")
    rows = []
    for index in range(profile.analyst_team_count):
        if index < len(state.business_unit_ids):
            buid = state.business_unit_ids[index]
        else:
            buid = _choose_business_unit_id(state)
        bu = state.business_unit_profiles[buid]
        team_id = analyst_team_id.next()
        code = f"{bu.business_unit_code}_TEAM_{index + 1:02d}"
        name = f"{bu.business_unit_name} Team {index + 1:02d}"
        state.analyst_team_profiles[team_id] = AnalystTeamProfile(team_id, code, name, buid, bu.region_id)
        state.analyst_team_ids.append(team_id)
        rows.append(
            {
                "analyst_team_id": team_id,
                "analyst_team_code": code,
                "analyst_team_name": name,
                "business_unit_id": buid,
                "region_id": bu.region_id,
                "is_active": "true",
            }
        )
    state.datasets["analyst_team"] = rows


def build_parties(state: GenerationState, profile: ScaleProfile) -> None:
    party_id = SequenceIdGenerator("PTY")
    parties = []

    for _ in range(profile.merchant_count):
        pid = party_id.next()
        category = state.rng.choice(MERCHANT_CATEGORIES)
        region_id = _choose_region_id(state)
        region = state.region_profiles[region_id]
        country = state.rng.choice(COUNTRY_GROUP_MAP[region.country_group_code])
        typical_amount = round(state.rng.uniform(15, 220), 2)
        state.merchant_profiles[pid] = MerchantProfile(
            party_id=pid,
            category_code=category,
            typical_amount=typical_amount,
            recurring_eligible=category in {"utilities", "telecom", "health", "gaming"},
            domicile_country=country,
            residency_region_id=region_id,
        )
        state.merchants.append(pid)
        parties.append(
            {
                "party_id": pid,
                "party_type": "merchant",
                "party_status": "active",
                "domicile_country_code": country,
                "risk_segment_code": state.rng.choice(["low", "medium", "high"]),
                "customer_segment_code": "small_business",
                "customer_type_code": "merchant_entity",
                "industry_sector_code": _industry_for_merchant_category(category),
                "residency_region_id": region_id,
                "customer_since_at": isoformat_utc(state.start_at - timedelta(days=state.rng.randint(180, 3650))),
            }
        )

    for _ in range(profile.analyst_count):
        pid = party_id.next()
        state.analysts.append(pid)
        team_id = state.rng.choice(state.analyst_team_ids)
        team = state.analyst_team_profiles[team_id]
        region = state.region_profiles[team.region_id]
        country = state.rng.choice(COUNTRY_GROUP_MAP[region.country_group_code])
        parties.append(
            {
                "party_id": pid,
                "party_type": "analyst",
                "party_status": "active",
                "domicile_country_code": country,
                "risk_segment_code": "low",
                "customer_segment_code": "",
                "customer_type_code": "employee",
                "industry_sector_code": "technology_services",
                "residency_region_id": team.region_id,
                "customer_since_at": isoformat_utc(state.start_at - timedelta(days=state.rng.randint(365, 2200))),
            }
        )

    for _ in range(profile.service_party_count):
        pid = party_id.next()
        state.services.append(pid)
        region_id = _choose_region_id(state)
        region = state.region_profiles[region_id]
        country = state.rng.choice(COUNTRY_GROUP_MAP[region.country_group_code])
        parties.append(
            {
                "party_id": pid,
                "party_type": "service",
                "party_status": "active",
                "domicile_country_code": country,
                "risk_segment_code": "low",
                "customer_segment_code": "",
                "customer_type_code": "employee",
                "industry_sector_code": "technology_services",
                "residency_region_id": region_id,
                "customer_since_at": isoformat_utc(state.start_at - timedelta(days=state.rng.randint(365, 2200))),
            }
        )

    segment_choices = CUSTOMER_SEGMENTS
    segment_weights = _segment_weights(state)
    income_map = {
        "mass_market": ("moderate", "retail_consumer", (2500, 7000), ["mobile", "online", "atm"]),
        "affluent": ("high", "affluent_consumer", (8000, 25000), ["mobile", "online", "branch"]),
        "small_business": ("upper_middle", "small_business_owner", (6000, 18000), ["online", "branch", "api"]),
    }
    risk_weights = {
        "mass_market": ["low", "medium", "high"],
        "affluent": ["low", "medium"],
        "small_business": ["low", "medium", "high"],
    }

    for _ in range(profile.customer_count):
        pid = party_id.next()
        segment = state.rng.choices(segment_choices, weights=segment_weights, k=1)[0]
        income_band, customer_type_code, income_range, channels = income_map[segment]
        monthly_income = round(state.rng.uniform(*income_range), 2)
        region_id = _choose_region_id(state)
        region = state.region_profiles[region_id]
        country = state.rng.choice(COUNTRY_GROUP_MAP[region.country_group_code])
        customer_since_at = state.start_at - timedelta(days=state.rng.randint(90, 3650))
        customer = CustomerProfile(
            party_id=pid,
            segment=segment,
            customer_type_code=customer_type_code,
            industry_sector_code="consumer" if segment != "small_business" else "retail_trade",
            income_band=income_band,
            monthly_income=monthly_income,
            risk_segment=state.rng.choice(risk_weights[segment]),
            domicile_country=country,
            residency_region_id=region_id,
            customer_since_at=customer_since_at,
            preferred_channels=state.rng.sample(channels, k=min(len(channels), state.rng.randint(2, len(channels)))),
            merchant_affinity=[],
        )
        state.customer_profiles[pid] = customer
        state.customers.append(pid)
        parties.append(
            {
                "party_id": pid,
                "party_type": "individual",
                "party_status": state.rng.choices(["active", "inactive", "restricted"], weights=[0.93, 0.05, 0.02], k=1)[0],
                "domicile_country_code": customer.domicile_country,
                "risk_segment_code": customer.risk_segment,
                "customer_segment_code": customer.segment,
                "customer_type_code": customer.customer_type_code,
                "industry_sector_code": customer.industry_sector_code,
                "residency_region_id": customer.residency_region_id,
                "customer_since_at": isoformat_utc(customer.customer_since_at),
            }
        )

    merchant_ids = list(state.merchant_profiles)
    for customer in state.customer_profiles.values():
        customer.merchant_affinity = state.rng.sample(merchant_ids, k=min(len(merchant_ids), state.rng.randint(4, 10)))
        recurring_merchant_candidates = [
            mid for mid in customer.merchant_affinity if state.merchant_profiles[mid].recurring_eligible
        ] or customer.merchant_affinity
        bill_count = min(len(recurring_merchant_candidates), state.rng.randint(1, 3))
        for payee_id in state.rng.sample(recurring_merchant_candidates, k=bill_count):
            customer.recurring_bills.append(
                RecurringBill(
                    payee_id=payee_id,
                    purpose_code=state.rng.choice(["utilities", "telecom", "travel", "merchant_purchase"]),
                    amount=round(max(18.0, state.merchant_profiles[payee_id].typical_amount * state.rng.uniform(0.8, 1.2)), 2),
                    due_day=state.rng.randint(1, 27),
                )
            )
        p2p_candidates = [cid for cid in state.customers if cid != customer.party_id]
        customer.p2p_payees = state.rng.sample(p2p_candidates, k=min(len(p2p_candidates), state.rng.randint(2, 5)))

    state.datasets["party"] = parties


def build_party_org_assignments(state: GenerationState) -> None:
    assignment_id = SequenceIdGenerator("POA")
    rows = []
    branch_by_region = _group_branch_ids_by_region(state)
    business_unit_by_region = _group_business_units_by_region(state)
    analyst_team_by_region = _group_analyst_teams_by_region(state)

    for customer in state.customer_profiles.values():
        region_id = customer.residency_region_id
        branch_id = _choose_branch_id(state, region_id, branch_by_region)
        business_unit_id = _choose_business_unit_id(state, region_id, business_unit_by_region)
        profile = PartyOrgAssignmentProfile(
            party_org_assignment_id=assignment_id.next(),
            party_id=customer.party_id,
            business_unit_id=business_unit_id,
            analyst_team_id="",
            branch_id=branch_id,
            assignment_role_code="customer_owner",
            effective_from_at=customer.customer_since_at,
        )
        state.party_org_assignments[customer.party_id] = profile
        rows.append(_assignment_row(profile))

    for merchant in state.merchant_profiles.values():
        region_id = merchant.residency_region_id
        branch_id = _choose_branch_id(state, region_id, branch_by_region)
        business_unit_id = _choose_business_unit_id(state, region_id, business_unit_by_region)
        profile = PartyOrgAssignmentProfile(
            party_org_assignment_id=assignment_id.next(),
            party_id=merchant.party_id,
            business_unit_id=business_unit_id,
            analyst_team_id="",
            branch_id=branch_id,
            assignment_role_code="merchant_owner",
            effective_from_at=state.start_at - timedelta(days=state.rng.randint(180, 3650)),
        )
        state.party_org_assignments[merchant.party_id] = profile
        rows.append(_assignment_row(profile))

    for analyst_id in state.analysts:
        party_row = next(row for row in state.datasets["party"] if row["party_id"] == analyst_id)
        preferred_region_id = party_row.get("residency_region_id", "") or None
        team_id = _choose_analyst_team_id(state, preferred_region_id, analyst_team_by_region)
        team = state.analyst_team_profiles[team_id]
        branch_id = _choose_branch_id(state, team.region_id, branch_by_region)
        profile = PartyOrgAssignmentProfile(
            party_org_assignment_id=assignment_id.next(),
            party_id=analyst_id,
            business_unit_id=team.business_unit_id,
            analyst_team_id=team_id,
            branch_id=branch_id,
            assignment_role_code="fraud_analyst",
            effective_from_at=state.start_at - timedelta(days=state.rng.randint(365, 2200)),
        )
        state.party_org_assignments[analyst_id] = profile
        rows.append(_assignment_row(profile))

    for service_id in state.services:
        business_unit_id = _choose_business_unit_id(state)
        bu = state.business_unit_profiles[business_unit_id]
        team_id = _choose_analyst_team_id(state, bu.region_id, analyst_team_by_region)
        profile = PartyOrgAssignmentProfile(
            party_org_assignment_id=assignment_id.next(),
            party_id=service_id,
            business_unit_id=business_unit_id,
            analyst_team_id=team_id,
            branch_id="",
            assignment_role_code="service_account",
            effective_from_at=state.start_at - timedelta(days=state.rng.randint(365, 2200)),
        )
        state.party_org_assignments[service_id] = profile
        rows.append(_assignment_row(profile))

    state.datasets["party_org_assignment"] = rows


def build_accounts(state: GenerationState, profile: ScaleProfile) -> None:
    account_id = SequenceIdGenerator("ACC")
    accounts = []
    customer_ids = list(state.customer_profiles)
    for index in range(profile.account_count):
        customer = state.customer_profiles[customer_ids[index % len(customer_ids)]]
        assignment = state.party_org_assignments[customer.party_id]
        opened_at = state.start_at - timedelta(days=state.rng.randint(30, 3650))
        status = state.rng.choices(
            ["open", "dormant", "blocked", "closed", "suspended"],
            weights=[0.86, 0.05, 0.03, 0.04, 0.02],
            k=1,
        )[0]
        closed_at = opened_at + timedelta(days=state.rng.randint(60, 3000)) if status == "closed" else None
        product_type = state.rng.choice(ACCOUNT_PRODUCTS)
        currency = state.rng.choices(["USD", "USD", "USD", "EUR", "GBP"], k=1)[0]
        balance = round(max(0.0, customer.monthly_income * state.rng.uniform(0.4, 4.5)), 2)
        aid = account_id.next()
        profile_row = AccountProfile(
            account_id=aid,
            party_id=customer.party_id,
            product_type=product_type,
            status=status,
            currency_code=currency,
            opened_at=opened_at,
            available_balance=balance,
            activity_weight=5 if customer.segment == "affluent" else 4 if customer.segment == "small_business" else 3,
            opened_branch_id=assignment.branch_id,
            servicing_business_unit_id=assignment.business_unit_id,
            account_region_id=customer.residency_region_id,
            closed_at=closed_at,
        )
        state.account_profiles[aid] = profile_row
        customer.account_ids.append(aid)
        accounts.append(
            {
                "deposit_account_id": aid,
                "account_status": status,
                "product_type_code": product_type,
                "primary_party_id": customer.party_id,
                "account_currency_code": currency,
                "available_balance_amount": f"{balance:.2f}",
                "opened_at": isoformat_utc(opened_at),
                "opened_branch_id": assignment.branch_id,
                "servicing_business_unit_id": assignment.business_unit_id,
                "account_region_id": customer.residency_region_id,
                "closed_at": isoformat_utc(closed_at) if closed_at else "",
            }
        )
    state.datasets["deposit_account"] = accounts


def build_cards(state: GenerationState, profile: ScaleProfile) -> None:
    card_id = SequenceIdGenerator("CRD")
    cards = []
    eligible_accounts = [aid for aid, account in state.account_profiles.items() if account.status != "closed"]
    selected_accounts = state.rng.sample(eligible_accounts, k=min(profile.card_count, len(eligible_accounts)))
    for account_id in selected_accounts:
        cid = card_id.next()
        card_profile = CardProfile(
            card_id=cid,
            account_id=account_id,
            status=state.rng.choices(["active", "blocked", "expired", "reissued"], weights=[0.82, 0.04, 0.08, 0.06], k=1)[0],
            network_code=state.rng.choice(CARD_NETWORKS),
        )
        state.card_profiles[cid] = card_profile
        cards.append(
            {
                "card_id": cid,
                "linked_account_id": account_id,
                "card_status": card_profile.status,
                "card_network_code": card_profile.network_code,
            }
        )
    state.datasets["payment_card"] = cards


def build_devices(state: GenerationState, profile: ScaleProfile) -> None:
    device_id = SequenceIdGenerator("DEV")
    devices = []
    shared_risky_target = max(8, profile.device_count // 100)
    customer_device_target = max(0, profile.device_count - shared_risky_target)
    customer_ids = list(state.customer_profiles)

    for _ in range(shared_risky_target):
        did = device_id.next()
        operating_system = state.rng.choice(DEVICE_OSES)
        state.shared_risky_device_ids.append(did)
        state.device_profiles[did] = DeviceProfileInternal(
            device_id=did,
            owner_party_id=None,
            status="risky",
            operating_system=operating_system,
            risk_band="severe",
            trusted=False,
        )
        devices.append(
            {
                "device_id": did,
                "device_status": "risky",
                "operating_system_code": operating_system,
                "device_risk_band": "severe",
            }
        )

    for index in range(customer_device_target):
        customer = state.customer_profiles[customer_ids[index % len(customer_ids)]]
        did = device_id.next()
        trusted = len(customer.device_ids) == 0 or state.rng.random() < 0.72
        status = "trusted" if trusted else state.rng.choice(["known", "new", "risky"])
        risk_band = "low" if trusted else state.rng.choice(["medium", "high"])
        profile_row = DeviceProfileInternal(
            device_id=did,
            owner_party_id=customer.party_id,
            status=status,
            operating_system=state.rng.choice(DEVICE_OSES),
            risk_band=risk_band,
            trusted=trusted,
        )
        state.device_profiles[did] = profile_row
        customer.device_ids.append(did)
        devices.append(
            {
                "device_id": did,
                "device_status": status,
                "operating_system_code": profile_row.operating_system,
                "device_risk_band": risk_band,
            }
        )
    state.datasets["device_profile"] = devices


def build_payments_and_channels(
    state: GenerationState, profile: ScaleProfile, progress: ProgressReporter | None = None
) -> None:
    payment_id = SequenceIdGenerator("PIN")
    channel_id = SequenceIdGenerator("CHN")
    payments = []
    channels = []
    account_pool = []
    for account in state.account_profiles.values():
        weight = 1 if account.status in {"blocked", "closed"} else account.activity_weight
        account_pool.extend([account.account_id] * weight)

    merchant_ids = state.merchants
    customer_ids = state.customers

    for index in range(profile.payment_count):
        account_id = state.rng.choice(account_pool)
        account = state.account_profiles[account_id]
        customer = state.customer_profiles[account.party_id]
        archetype = state.rng.choices(
            ["merchant_purchase", "recurring_bill", "p2p_transfer", "card_online_purchase", "atm_cash", "branch_payment"],
            weights=[38, 18, 18, 14, 6, 6],
            k=1,
        )[0]
        recurring = archetype == "recurring_bill"
        if recurring and customer.recurring_bills:
            bill = state.rng.choice(customer.recurring_bills)
            creditor_party_id = bill.payee_id
            purpose = bill.purpose_code
            amount = bounded_normal_amount(state.rng, bill.amount, bill.amount * 0.08, floor=8.0)
            event_at = _sample_event_datetime(state, bill.due_day, business_hour=True)
            new_payee = False
        else:
            purpose = archetype if archetype in PAYMENT_PURPOSES else state.rng.choice(PAYMENT_PURPOSES)
            if archetype in {"merchant_purchase", "card_online_purchase", "branch_payment"}:
                creditor_party_id = state.rng.choice(customer.merchant_affinity or merchant_ids)
                new_payee = state.rng.random() < 0.04
            elif archetype == "p2p_transfer":
                creditor_party_id = state.rng.choice(customer.p2p_payees or customer_ids)
                new_payee = state.rng.random() < 0.14
            else:
                creditor_party_id = state.rng.choice(merchant_ids)
                new_payee = state.rng.random() < 0.05

            if new_payee and archetype == "p2p_transfer":
                creditor_party_id = state.rng.choice(customer_ids)
            elif new_payee:
                creditor_party_id = state.rng.choice(merchant_ids)

            amount_center = {
                "merchant_purchase": 62,
                "card_online_purchase": 95,
                "p2p_transfer": 140,
                "atm_cash": 180,
                "branch_payment": 320,
            }.get(archetype, 55)
            amount = bounded_normal_amount(state.rng, amount_center, amount_center * 0.55, floor=3.0)
            event_at = _sample_event_datetime(state)

        channel_code = _choose_channel(state.rng, customer.preferred_channels, archetype)
        branch_id = account.opened_branch_id if channel_code == "branch" else ""
        session_id = random_session_id(state.rng, fake=state.fake)
        new_device = channel_code in {"mobile", "online", "api"} and state.rng.random() < 0.05
        device_id = _choose_device_for_customer(state, customer, new_device)
        card_id = _choose_card_for_account(state, account_id, archetype)
        instruction_status = state.rng.choices(
            ["accepted", "accepted", "accepted", "pending", "rejected", "cancelled"],
            weights=[45, 22, 18, 8, 4, 3],
            k=1,
        )[0]
        creditor_country = _party_country(state, creditor_party_id)
        event_country = _event_country_for_channel(state, customer.domicile_country, branch_id, channel_code)
        ip_country = event_country if state.rng.random() < 0.82 else state.rng.choice(COUNTRIES)
        payment_rail = _payment_rail_for_archetype(state, archetype)
        creditor_country = _apply_cross_border_control(state, customer.domicile_country, creditor_country)
        is_cross_border = creditor_country != customer.domicile_country

        cid = channel_id.next()
        pid = payment_id.next()
        channels.append(
            {
                "channel_event_id": cid,
                "channel_code": channel_code,
                "session_id": session_id,
                "branch_id": branch_id,
                "event_at": isoformat_utc(event_at),
                "event_country_code": event_country,
                "ip_country_code": ip_country,
                "authentication_result_code": _authentication_result_for_channel(state, channel_code),
                "session_risk_code": _session_risk_for_payment(state, new_device, is_cross_border),
            }
        )
        payment_row = {
            "payment_instruction_id": pid,
            "instruction_status": instruction_status,
            "debtor_account_id": account_id,
            "debtor_party_id": customer.party_id,
            "creditor_party_id": creditor_party_id,
            "instructed_amount": f"{amount:.2f}",
            "instructed_currency_code": account.currency_code,
            "payment_purpose_code": purpose,
            "channel_event_id": cid,
            "card_id": card_id,
            "device_id": device_id,
            "event_at": isoformat_utc(event_at),
            "payment_rail_code": payment_rail,
            "is_cross_border": _bool_string(is_cross_border),
            "merchant_country_code": creditor_country,
            "counterparty_bank_country_code": state.rng.choice(COUNTRIES if is_cross_border else [creditor_country]),
            "booking_date": event_at.date().isoformat(),
        }
        payments.append(payment_row)
        meta = PaymentMeta(
            instruction_id=pid,
            account_id=account_id,
            debtor_party_id=customer.party_id,
            creditor_party_id=creditor_party_id,
            channel_event_id=cid,
            event_at=event_at,
            archetype=archetype,
            recurring=recurring,
            new_payee=new_payee,
            new_device=new_device,
            off_hours=False,
        )
        state.payment_meta[pid] = meta
        state.payment_records[pid] = payment_row
        state.channel_records[cid] = channels[-1]
        state.account_payment_ids.setdefault(account_id, []).append(pid)
        state.customer_payment_ids.setdefault(customer.party_id, []).append(pid)
        if progress:
            progress.tick(
                key="payment_generation",
                current=index + 1,
                total=profile.payment_count,
                label="Generating payments and channel events",
            )

    state.datasets["channel_event"] = channels
    state.datasets["payment_instruction"] = payments


def _segment_weights(state: GenerationState) -> list[float]:
    controls = state.generation_context.get("customer_controls", {})
    if isinstance(controls, dict):
        segment_mix = controls.get("customer_segment_mix")
        if isinstance(segment_mix, dict):
            return [float(segment_mix.get(segment, 1.0)) for segment in CUSTOMER_SEGMENTS]
    return [0.72, 0.2, 0.08]


def _ordered_region_templates(
    templates: list[tuple[str, str, str]], controls: object, count: int
) -> list[int]:
    if not isinstance(controls, dict):
        return [index % len(templates) for index in range(count)]
    region_mix = controls.get("region_mix")
    if not isinstance(region_mix, dict) or not region_mix:
        return [index % len(templates) for index in range(count)]
    weighted: list[int] = []
    for index, (code, name, _) in enumerate(templates):
        weight = float(region_mix.get(code, region_mix.get(name, 1.0)))
        copies = max(1, int(round(weight * 10)))
        weighted.extend([index] * copies)
    return [weighted[index % len(weighted)] for index in range(count)]


def _choose_region_id(state: GenerationState) -> str:
    controls = state.generation_context.get("geography_controls", {})
    region_mix = controls.get("region_mix") if isinstance(controls, dict) else None
    if not isinstance(region_mix, dict) or not region_mix:
        return state.rng.choice(state.region_ids)
    weights = []
    for region_id in state.region_ids:
        region = state.region_profiles[region_id]
        weights.append(
            float(
                region_mix.get(
                    region_id,
                    region_mix.get(region.region_code, region_mix.get(region.region_name, 1.0)),
                )
            )
        )
    return state.rng.choices(state.region_ids, weights=weights, k=1)[0]


def _choose_branch_territory_id(state: GenerationState, territory_ids: list[str]) -> str:
    geography_controls = state.generation_context.get("geography_controls", {})
    territory_mix = geography_controls.get("branch_territory_mix") if isinstance(geography_controls, dict) else None
    if not isinstance(territory_mix, dict) or not territory_mix:
        return state.rng.choice(territory_ids)
    weights = []
    for territory_id in territory_ids:
        territory = state.branch_territory_profiles[territory_id]
        weights.append(
            float(
                territory_mix.get(
                    territory_id,
                    territory_mix.get(
                        territory.branch_territory_code,
                        territory_mix.get(territory.branch_territory_name, 1.0),
                    ),
                )
            )
        )
    return state.rng.choices(territory_ids, weights=weights, k=1)[0]


def _choose_business_unit_type(state: GenerationState, index: int) -> str:
    organization_controls = state.generation_context.get("organization_controls", {})
    unit_mix = organization_controls.get("business_unit_mix") if isinstance(organization_controls, dict) else None
    if not isinstance(unit_mix, dict) or not unit_mix:
        return BUSINESS_UNIT_TYPES[index % len(BUSINESS_UNIT_TYPES)]
    weights = [float(unit_mix.get(unit_type, 1.0)) for unit_type in BUSINESS_UNIT_TYPES]
    return state.rng.choices(BUSINESS_UNIT_TYPES, weights=weights, k=1)[0]


def _choose_business_unit_id(
    state: GenerationState,
    region_id: str | None = None,
    grouped_units: dict[str, list[str]] | None = None,
) -> str:
    candidate_ids = grouped_units.get(region_id, []) if region_id and grouped_units else list(state.business_unit_ids)
    if not candidate_ids:
        candidate_ids = list(state.business_unit_ids)
    organization_controls = state.generation_context.get("organization_controls", {})
    unit_mix = organization_controls.get("business_unit_mix") if isinstance(organization_controls, dict) else None
    if not isinstance(unit_mix, dict) or not unit_mix:
        return state.rng.choice(candidate_ids)
    weights = []
    for business_unit_id in candidate_ids:
        unit = state.business_unit_profiles[business_unit_id]
        weights.append(
            float(
                unit_mix.get(
                    business_unit_id,
                    unit_mix.get(unit.business_unit_code, unit_mix.get(unit.business_unit_type, 1.0)),
                )
            )
        )
    return state.rng.choices(candidate_ids, weights=weights, k=1)[0]


def _choose_analyst_team_id(
    state: GenerationState,
    region_id: str | None = None,
    grouped_teams: dict[str, list[str]] | None = None,
) -> str:
    candidate_ids = grouped_teams.get(region_id, []) if region_id and grouped_teams else list(state.analyst_team_ids)
    if not candidate_ids:
        candidate_ids = list(state.analyst_team_ids)
    organization_controls = state.generation_context.get("organization_controls", {})
    team_mix = organization_controls.get("analyst_team_mix") if isinstance(organization_controls, dict) else None
    if not isinstance(team_mix, dict) or not team_mix:
        return state.rng.choice(candidate_ids)
    weights = []
    for analyst_team_id in candidate_ids:
        team = state.analyst_team_profiles[analyst_team_id]
        weights.append(
            float(
                team_mix.get(
                    analyst_team_id,
                    team_mix.get(team.analyst_team_code, team_mix.get(team.analyst_team_name, 1.0)),
                )
            )
        )
    return state.rng.choices(candidate_ids, weights=weights, k=1)[0]


def _choose_branch_id(
    state: GenerationState,
    region_id: str,
    grouped_branches: dict[str, list[str]],
) -> str:
    candidate_ids = grouped_branches.get(region_id, []) or list(state.branch_ids)
    organization_controls = state.generation_context.get("organization_controls", {})
    branch_mix = organization_controls.get("branch_activity_mix") if isinstance(organization_controls, dict) else None
    if not isinstance(branch_mix, dict) or not branch_mix:
        return state.rng.choice(candidate_ids)
    weights = []
    for branch_id in candidate_ids:
        branch = state.branch_location_profiles[branch_id]
        territory = state.branch_territory_profiles[branch.branch_territory_id]
        weights.append(
            float(
                branch_mix.get(
                    branch_id,
                    branch_mix.get(
                        branch.branch_code,
                        branch_mix.get(
                            territory.branch_territory_code,
                            branch_mix.get(territory.branch_territory_name, 1.0),
                        ),
                    ),
                )
            )
        )
    return state.rng.choices(candidate_ids, weights=weights, k=1)[0]


def _choose_channel(rng: random.Random, preferred_channels: list[str], archetype: str) -> str:
    if archetype == "atm_cash":
        return "atm"
    if archetype == "branch_payment":
        return "branch"
    if archetype == "card_online_purchase":
        return rng.choice(["mobile", "online"])
    return rng.choices(preferred_channels or CHANNELS, k=1)[0]


def _choose_device_for_customer(state: GenerationState, customer: CustomerProfile, force_new: bool) -> str:
    if not customer.device_ids:
        return ""
    if force_new and state.shared_risky_device_ids and state.rng.random() < 0.35:
        return state.rng.choice(state.shared_risky_device_ids)
    if force_new:
        unknown_devices = [did for did in customer.device_ids if not state.device_profiles[did].trusted]
        if unknown_devices:
            return state.rng.choice(unknown_devices)
    return state.rng.choice(customer.device_ids)


def _choose_card_for_account(state: GenerationState, account_id: str, archetype: str) -> str:
    if archetype not in {"merchant_purchase", "card_online_purchase", "atm_cash"}:
        return ""
    candidates = [card.card_id for card in state.card_profiles.values() if card.account_id == account_id]
    if not candidates:
        return ""
    return state.rng.choice(candidates)


def _party_country(state: GenerationState, party_id: str) -> str:
    merchant = state.merchant_profiles.get(party_id)
    if merchant:
        return merchant.domicile_country
    customer = state.customer_profiles.get(party_id)
    if customer:
        return customer.domicile_country
    for row in state.datasets.get("party", []):
        if row["party_id"] == party_id:
            return row.get("domicile_country_code", "US")
    return "US"


def _event_country_for_channel(state: GenerationState, domicile_country: str, branch_id: str, channel_code: str) -> str:
    if branch_id and branch_id in state.branch_location_profiles:
        return state.branch_location_profiles[branch_id].country_code
    if channel_code in {"mobile", "online", "api"} and state.rng.random() < 0.08:
        return state.rng.choice(COUNTRIES)
    return domicile_country


def _authentication_result_for_channel(state: GenerationState, channel_code: str) -> str:
    if channel_code in {"mobile", "online", "api"}:
        return state.rng.choices(
            AUTHENTICATION_RESULTS,
            weights=[0.72, 0.12, 0.05, 0.08, 0.03],
            k=1,
        )[0]
    return "success"


def _session_risk_for_payment(state: GenerationState, new_device: bool, is_cross_border: bool) -> str:
    if new_device and is_cross_border:
        return state.rng.choice(["high", "severe"])
    if new_device:
        return state.rng.choice(["medium", "high"])
    if is_cross_border:
        return state.rng.choice(["medium", "high"])
    return state.rng.choice(["low", "low", "medium"])


def _payment_rail_for_archetype(state: GenerationState, archetype: str) -> str:
    controls = state.generation_context.get("payment_controls", {})
    payment_mix = controls.get("payment_rail_mix") if isinstance(controls, dict) else None
    if isinstance(payment_mix, dict) and payment_mix:
        allowed = _allowed_payment_rails(archetype)
        weights = [float(payment_mix.get(rail, 1.0)) for rail in allowed]
        return state.rng.choices(allowed, weights=weights, k=1)[0]
    if archetype in {"merchant_purchase", "card_online_purchase", "atm_cash"}:
        return "card"
    if archetype == "p2p_transfer":
        return state.rng.choice(["ach", "rtp", "internal_transfer"])
    if archetype == "branch_payment":
        return state.rng.choice(["wire", "ach"])
    if archetype == "recurring_bill":
        return state.rng.choice(["ach", "sepa", "internal_transfer"])
    return state.rng.choice(PAYMENT_RAIL_CODES)


def _industry_for_merchant_category(category_code: str) -> str:
    mapping = {
        "groceries": "retail_trade",
        "travel": "travel_services",
        "gas": "retail_trade",
        "utilities": "telecom_services",
        "ecommerce": "technology_services",
        "dining": "retail_trade",
        "health": "health_services",
        "retail": "retail_trade",
        "gaming": "technology_services",
        "telecom": "telecom_services",
    }
    return mapping.get(category_code, "retail_trade")


def _group_branch_ids_by_region(state: GenerationState) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {region_id: [] for region_id in state.region_ids}
    for branch in state.branch_location_profiles.values():
        grouped.setdefault(branch.region_id, []).append(branch.branch_id)
    return grouped


def _group_business_units_by_region(state: GenerationState) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {region_id: [] for region_id in state.region_ids}
    for business_unit in state.business_unit_profiles.values():
        grouped.setdefault(business_unit.region_id, []).append(business_unit.business_unit_id)
    return grouped


def _group_analyst_teams_by_region(state: GenerationState) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {region_id: [] for region_id in state.region_ids}
    for team in state.analyst_team_profiles.values():
        grouped.setdefault(team.region_id, []).append(team.analyst_team_id)
    return grouped


def _assignment_row(profile: PartyOrgAssignmentProfile) -> dict[str, str]:
    return {
        "party_org_assignment_id": profile.party_org_assignment_id,
        "party_id": profile.party_id,
        "business_unit_id": profile.business_unit_id,
        "analyst_team_id": profile.analyst_team_id,
        "branch_id": profile.branch_id,
        "assignment_role_code": profile.assignment_role_code,
        "effective_from_at": isoformat_utc(profile.effective_from_at),
        "effective_to_at": isoformat_utc(profile.effective_to_at) if profile.effective_to_at else "",
    }


def _reference_description(state: GenerationState, code_set_name: str, code_value: str) -> str:
    clean_value = code_value.replace("_", " ")
    templates = {
        "party_type": f"Party classification for {clean_value}.",
        "party_status": f"Lifecycle status indicating the party is {clean_value}.",
        "account_status": f"Deposit account servicing status: {clean_value}.",
        "product_type_code": f"Retail banking product family for {clean_value}.",
        "currency_code": f"Supported transaction currency code {code_value}.",
        "card_status": f"Card lifecycle state recorded as {clean_value}.",
        "card_network_code": f"Payment card network mapped to {clean_value}.",
        "device_status": f"Device trust posture marked as {clean_value}.",
        "device_risk_band": f"Device risk assessment band of {clean_value}.",
        "channel_code": f"Customer interaction channel through {clean_value}.",
        "instruction_status": f"Payment instruction processing state is {clean_value}.",
        "transaction_status": f"Booking lifecycle state set to {clean_value}.",
        "risk_level": f"Fraud risk severity classified as {clean_value}.",
        "alert_status": f"Fraud alert workflow state is {clean_value}.",
        "alert_severity": f"Alert severity rating of {clean_value}.",
        "case_status": f"Case management workflow currently {clean_value}.",
        "investigation_event_type": f"Fraud investigation activity of type {clean_value}.",
        "decision_type": f"Decision outcome recorded as {clean_value}.",
        "decision_status": f"Decision execution status set to {clean_value}.",
        "disposition_code": f"Final case disposition captured as {clean_value}.",
        "country_code": f"Jurisdiction or domicile country code {code_value}.",
        "country_group_code": f"Country grouping for {clean_value}.",
        "payment_purpose_code": f"Payment purpose category covering {clean_value}.",
        "merchant_category_code": f"Merchant industry category aligned to {clean_value}.",
        "customer_segment_code": f"Customer segment grouped as {clean_value}.",
        "customer_type_code": f"Customer type coded as {clean_value}.",
        "industry_sector_code": f"Industry sector classification for {clean_value}.",
        "risk_segment_code": f"Customer or entity risk segment of {clean_value}.",
        "queue_code": f"Operational review queue routed to {clean_value}.",
        "signal_type_code": f"Risk signal pattern for {clean_value}.",
        "business_unit_type": f"Business unit operates as {clean_value}.",
        "assignment_role_code": f"Organizational assignment role for {clean_value}.",
        "authentication_result_code": f"Authentication flow result marked as {clean_value}.",
        "session_risk_code": f"Session risk classification of {clean_value}.",
        "payment_rail_code": f"Payment executed via {clean_value}.",
        "transaction_direction_code": f"Transaction direction coded as {clean_value}.",
        "alert_type_code": f"Alert category for {clean_value}.",
        "alert_source_code": f"Alert source recorded as {clean_value}.",
        "case_type_code": f"Case category for {clean_value}.",
        "case_priority_code": f"Case priority of {clean_value}.",
        "escalation_level_code": f"Escalation tier {clean_value}.",
        "event_result_code": f"Investigation event outcome {clean_value}.",
        "decision_reason_code": f"Decision reason captured as {clean_value}.",
        "decision_channel_code": f"Decision produced through {clean_value}.",
        "recovery_status_code": f"Recovery status tracked as {clean_value}.",
    }
    if code_set_name in templates:
        return templates[code_set_name]
    return state.fake.sentence(nb_words=8)


def _bool_string(value: bool) -> str:
    return "true" if value else "false"


def _sample_event_datetime(state: GenerationState, due_day: int | None = None, business_hour: bool = False) -> datetime:
    controls = state.generation_context.get("calendar_controls", {})
    if due_day is not None and not state.calendar_rows:
        return random_datetime_on_due_day(state.rng, state.start_at, state.end_at, due_day, business_hour=business_hour)
    if not state.calendar_rows:
        return random_datetime_between(state.rng, state.start_at, state.end_at, off_hours=not business_hour)

    candidate_rows = state.calendar_rows
    if due_day is not None:
        candidate_rows = [
            row for row in state.calendar_rows if int(row["calendar_date"].split("-")[2]) == min(due_day, 28)
        ] or state.calendar_rows

    month_weighting = controls.get("month_weighting") if isinstance(controls, dict) else None
    quarter_end_spike = bool(controls.get("quarter_end_spike")) if isinstance(controls, dict) else False
    holiday_spike = bool(controls.get("holiday_spike")) if isinstance(controls, dict) else False
    weights: list[float] = []
    for row in candidate_rows:
        weight = 1.0
        if isinstance(month_weighting, dict):
            month_number = row["calendar_month"]
            month_name = row["calendar_month_name"].lower()
            weight *= float(month_weighting.get(month_number, month_weighting.get(month_name, 1.0)))
        if quarter_end_spike and row.get("is_quarter_end") == "true":
            weight *= 2.5
        if holiday_spike and row.get("is_holiday") == "true":
            weight *= 2.0
        weights.append(weight)

    selected = state.rng.choices(candidate_rows, weights=weights, k=1)[0]
    year, month, day = (int(part) for part in selected["calendar_date"].split("-"))
    if business_hour:
        hour = state.rng.randint(8, 20)
    else:
        hour = state.rng.choices([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], weights=[4, 6, 8, 8, 7, 7, 8, 8, 8, 7, 5, 4, 3], k=1)[0]
    return datetime(
        year,
        month,
        day,
        hour=hour,
        minute=state.rng.randint(0, 59),
        second=state.rng.randint(0, 59),
        tzinfo=timezone.utc,
    )


def _apply_cross_border_control(state: GenerationState, domicile_country: str, creditor_country: str) -> str:
    controls = state.generation_context.get("payment_controls", {})
    target_ratio = controls.get("cross_border_ratio") if isinstance(controls, dict) else None
    if target_ratio is None:
        return creditor_country
    try:
        ratio = float(target_ratio)
    except (TypeError, ValueError):
        return creditor_country
    if state.rng.random() < max(0.0, min(ratio, 1.0)):
        foreign_choices = [country for country in COUNTRIES if country != domicile_country]
        return state.rng.choice(foreign_choices)
    return domicile_country


def _allowed_payment_rails(archetype: str) -> list[str]:
    if archetype in {"merchant_purchase", "card_online_purchase", "atm_cash"}:
        return ["card"]
    if archetype == "p2p_transfer":
        return ["ach", "rtp", "internal_transfer"]
    if archetype == "branch_payment":
        return ["wire", "ach"]
    if archetype == "recurring_bill":
        return ["ach", "sepa", "internal_transfer"]
    return PAYMENT_RAIL_CODES
