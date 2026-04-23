from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from random import Random
from typing import Any

from faker import Faker


@dataclass
class RecurringBill:
    payee_id: str
    purpose_code: str
    amount: float
    due_day: int


@dataclass
class CustomerProfile:
    party_id: str
    segment: str
    customer_type_code: str
    industry_sector_code: str
    income_band: str
    monthly_income: float
    risk_segment: str
    domicile_country: str
    residency_region_id: str
    customer_since_at: datetime
    preferred_channels: list[str]
    merchant_affinity: list[str]
    recurring_bills: list[RecurringBill] = field(default_factory=list)
    p2p_payees: list[str] = field(default_factory=list)
    account_ids: list[str] = field(default_factory=list)
    device_ids: list[str] = field(default_factory=list)


@dataclass
class AccountProfile:
    account_id: str
    party_id: str
    product_type: str
    status: str
    currency_code: str
    opened_at: datetime
    available_balance: float
    activity_weight: int
    opened_branch_id: str
    servicing_business_unit_id: str
    account_region_id: str
    closed_at: datetime | None = None


@dataclass
class CardProfile:
    card_id: str
    account_id: str
    status: str
    network_code: str


@dataclass
class DeviceProfileInternal:
    device_id: str
    owner_party_id: str | None
    status: str
    operating_system: str
    risk_band: str
    trusted: bool


@dataclass
class MerchantProfile:
    party_id: str
    category_code: str
    typical_amount: float
    recurring_eligible: bool
    domicile_country: str
    residency_region_id: str


@dataclass
class RegionProfile:
    region_id: str
    region_code: str
    region_name: str
    country_group_code: str


@dataclass
class BranchTerritoryProfile:
    branch_territory_id: str
    branch_territory_code: str
    branch_territory_name: str
    region_id: str


@dataclass
class BranchLocationProfile:
    branch_id: str
    branch_code: str
    branch_name: str
    branch_territory_id: str
    region_id: str
    country_code: str
    city_name: str


@dataclass
class BusinessUnitProfile:
    business_unit_id: str
    business_unit_code: str
    business_unit_name: str
    business_unit_type: str
    region_id: str


@dataclass
class AnalystTeamProfile:
    analyst_team_id: str
    analyst_team_code: str
    analyst_team_name: str
    business_unit_id: str
    region_id: str


@dataclass
class PartyOrgAssignmentProfile:
    party_org_assignment_id: str
    party_id: str
    business_unit_id: str
    analyst_team_id: str
    branch_id: str
    assignment_role_code: str
    effective_from_at: datetime
    effective_to_at: datetime | None = None


@dataclass
class PaymentMeta:
    instruction_id: str
    account_id: str
    debtor_party_id: str
    creditor_party_id: str
    channel_event_id: str
    event_at: datetime
    archetype: str
    recurring: bool
    new_payee: bool
    new_device: bool
    off_hours: bool
    shared_device: bool = False
    scenario: str = "normal"
    confirmed_fraud: bool = False
    risk_score: float = 0.0
    risk_level: str = "low"
    cluster_id: str | None = None


@dataclass
class FraudCaseMeta:
    fraud_case_id: str
    primary_alert_id: str
    scenario: str
    confirmed_fraud: bool
    related_payment_instruction_id: str


@dataclass
class GenerationState:
    rng: Random
    fake: Faker
    seed: int
    run_id: str
    batch_mode: str
    start_at: datetime
    end_at: datetime
    output_root: Path
    datasets: dict[str, list[dict]]
    generation_context: dict[str, Any] = field(default_factory=dict)
    blueprint_name: str | None = None
    blueprint_source: str | None = None
    calendar_rows: list[dict] = field(default_factory=list)
    region_profiles: dict[str, RegionProfile] = field(default_factory=dict)
    branch_territory_profiles: dict[str, BranchTerritoryProfile] = field(default_factory=dict)
    branch_location_profiles: dict[str, BranchLocationProfile] = field(default_factory=dict)
    business_unit_profiles: dict[str, BusinessUnitProfile] = field(default_factory=dict)
    analyst_team_profiles: dict[str, AnalystTeamProfile] = field(default_factory=dict)
    party_org_assignments: dict[str, PartyOrgAssignmentProfile] = field(default_factory=dict)
    customer_profiles: dict[str, CustomerProfile] = field(default_factory=dict)
    account_profiles: dict[str, AccountProfile] = field(default_factory=dict)
    card_profiles: dict[str, CardProfile] = field(default_factory=dict)
    device_profiles: dict[str, DeviceProfileInternal] = field(default_factory=dict)
    merchant_profiles: dict[str, MerchantProfile] = field(default_factory=dict)
    payment_meta: dict[str, PaymentMeta] = field(default_factory=dict)
    fraud_case_meta: dict[str, FraudCaseMeta] = field(default_factory=dict)
    payment_records: dict[str, dict] = field(default_factory=dict)
    channel_records: dict[str, dict] = field(default_factory=dict)
    account_payment_ids: dict[str, list[str]] = field(default_factory=dict)
    customer_payment_ids: dict[str, list[str]] = field(default_factory=dict)
    analysts: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    merchants: list[str] = field(default_factory=list)
    customers: list[str] = field(default_factory=list)
    region_ids: list[str] = field(default_factory=list)
    branch_ids: list[str] = field(default_factory=list)
    business_unit_ids: list[str] = field(default_factory=list)
    analyst_team_ids: list[str] = field(default_factory=list)
    shared_risky_device_ids: list[str] = field(default_factory=list)
