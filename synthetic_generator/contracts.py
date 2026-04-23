from __future__ import annotations

from dataclasses import dataclass


DATASET_ORDER = [
    "reference_data_catalog",
    "calendar_day",
    "region",
    "branch_territory",
    "branch_location",
    "business_unit",
    "analyst_team",
    "party",
    "party_org_assignment",
    "deposit_account",
    "payment_card",
    "device_profile",
    "channel_event",
    "payment_instruction",
    "payment_transaction",
    "risk_signal",
    "fraud_alert",
    "fraud_case",
    "investigation_event",
    "decision_record",
    "case_disposition",
]


CSV_FIELD_ORDER = {
    "reference_data_catalog": ["code_set_name", "code_value", "code_description", "is_active"],
    "calendar_day": [
        "calendar_date",
        "calendar_year",
        "calendar_quarter",
        "calendar_month",
        "calendar_month_name",
        "week_of_year",
        "day_of_week",
        "day_name",
        "is_weekend",
        "is_month_end",
        "is_quarter_end",
        "is_holiday",
    ],
    "region": ["region_id", "region_code", "region_name", "country_group_code", "is_active"],
    "branch_territory": ["branch_territory_id", "branch_territory_code", "branch_territory_name", "region_id", "is_active"],
    "branch_location": ["branch_id", "branch_code", "branch_name", "branch_territory_id", "region_id", "country_code", "city_name", "is_active"],
    "business_unit": ["business_unit_id", "business_unit_code", "business_unit_name", "business_unit_type", "region_id", "is_active"],
    "analyst_team": ["analyst_team_id", "analyst_team_code", "analyst_team_name", "business_unit_id", "region_id", "is_active"],
    "party": [
        "party_id",
        "party_type",
        "party_status",
        "domicile_country_code",
        "risk_segment_code",
        "customer_segment_code",
        "customer_type_code",
        "industry_sector_code",
        "residency_region_id",
        "customer_since_at",
    ],
    "party_org_assignment": [
        "party_org_assignment_id",
        "party_id",
        "business_unit_id",
        "analyst_team_id",
        "branch_id",
        "assignment_role_code",
        "effective_from_at",
        "effective_to_at",
    ],
    "deposit_account": [
        "deposit_account_id",
        "account_status",
        "product_type_code",
        "primary_party_id",
        "account_currency_code",
        "available_balance_amount",
        "opened_at",
        "opened_branch_id",
        "servicing_business_unit_id",
        "account_region_id",
        "closed_at",
    ],
    "payment_card": ["card_id", "linked_account_id", "card_status", "card_network_code"],
    "device_profile": ["device_id", "device_status", "operating_system_code", "device_risk_band"],
    "channel_event": [
        "channel_event_id",
        "channel_code",
        "session_id",
        "branch_id",
        "event_at",
        "event_country_code",
        "ip_country_code",
        "authentication_result_code",
        "session_risk_code",
    ],
    "payment_instruction": [
        "payment_instruction_id",
        "instruction_status",
        "debtor_account_id",
        "debtor_party_id",
        "creditor_party_id",
        "instructed_amount",
        "instructed_currency_code",
        "payment_purpose_code",
        "channel_event_id",
        "card_id",
        "device_id",
        "event_at",
        "payment_rail_code",
        "is_cross_border",
        "merchant_country_code",
        "counterparty_bank_country_code",
        "booking_date",
    ],
    "payment_transaction": [
        "payment_transaction_id",
        "payment_instruction_id",
        "transaction_status",
        "booking_amount",
        "transaction_currency_code",
        "settlement_at",
        "merchant_category_code",
        "reversal_reason_code",
        "posted_date",
        "value_date",
        "transaction_direction_code",
    ],
    "risk_signal": [
        "risk_signal_id",
        "payment_instruction_id",
        "signal_type_code",
        "signal_score_amount",
        "risk_level",
        "event_at",
    ],
    "fraud_alert": [
        "fraud_alert_id",
        "risk_signal_id",
        "alert_status",
        "alert_severity",
        "queue_code",
        "created_at",
        "alert_type_code",
        "alert_source_code",
        "owning_business_unit_id",
        "owning_analyst_team_id",
        "service_level_due_at",
    ],
    "fraud_case": [
        "fraud_case_id",
        "primary_alert_id",
        "case_status",
        "assigned_analyst_party_id",
        "opened_at",
        "closed_at",
        "case_type_code",
        "case_priority_code",
        "owning_business_unit_id",
        "owning_analyst_team_id",
        "handling_region_id",
        "escalation_level_code",
    ],
    "investigation_event": [
        "investigation_event_id",
        "fraud_case_id",
        "investigation_event_type",
        "actor_party_id",
        "event_at",
        "event_result_code",
        "elapsed_minutes",
    ],
    "decision_record": [
        "decision_id",
        "fraud_case_id",
        "decision_type",
        "decision_status",
        "decision_maker_party_id",
        "decided_at",
        "decision_reason_code",
        "decision_channel_code",
        "policy_name",
        "rule_set_version",
    ],
    "case_disposition": [
        "disposition_id",
        "decision_id",
        "disposition_code",
        "financial_impact_amount",
        "outcome_at",
        "loss_amount",
        "recovered_amount",
        "write_off_amount",
        "recovery_status_code",
    ],
}


PRIMARY_KEYS = {
    "reference_data_catalog": None,
    "calendar_day": "calendar_date",
    "region": "region_id",
    "branch_territory": "branch_territory_id",
    "branch_location": "branch_id",
    "business_unit": "business_unit_id",
    "analyst_team": "analyst_team_id",
    "party": "party_id",
    "party_org_assignment": "party_org_assignment_id",
    "deposit_account": "deposit_account_id",
    "payment_card": "card_id",
    "device_profile": "device_id",
    "channel_event": "channel_event_id",
    "payment_instruction": "payment_instruction_id",
    "payment_transaction": "payment_transaction_id",
    "risk_signal": "risk_signal_id",
    "fraud_alert": "fraud_alert_id",
    "fraud_case": "fraud_case_id",
    "investigation_event": "investigation_event_id",
    "decision_record": "decision_id",
    "case_disposition": "disposition_id",
}


FOREIGN_KEYS = {
    "branch_territory": [("region_id", "region", "region_id")],
    "branch_location": [
        ("branch_territory_id", "branch_territory", "branch_territory_id"),
        ("region_id", "region", "region_id"),
    ],
    "business_unit": [("region_id", "region", "region_id")],
    "analyst_team": [
        ("business_unit_id", "business_unit", "business_unit_id"),
        ("region_id", "region", "region_id"),
    ],
    "party": [("residency_region_id", "region", "region_id")],
    "party_org_assignment": [
        ("party_id", "party", "party_id"),
        ("business_unit_id", "business_unit", "business_unit_id"),
        ("analyst_team_id", "analyst_team", "analyst_team_id"),
        ("branch_id", "branch_location", "branch_id"),
    ],
    "deposit_account": [
        ("primary_party_id", "party", "party_id"),
        ("opened_branch_id", "branch_location", "branch_id"),
        ("servicing_business_unit_id", "business_unit", "business_unit_id"),
        ("account_region_id", "region", "region_id"),
    ],
    "payment_card": [("linked_account_id", "deposit_account", "deposit_account_id")],
    "channel_event": [("branch_id", "branch_location", "branch_id")],
    "payment_instruction": [
        ("debtor_account_id", "deposit_account", "deposit_account_id"),
        ("debtor_party_id", "party", "party_id"),
        ("creditor_party_id", "party", "party_id"),
        ("channel_event_id", "channel_event", "channel_event_id"),
        ("card_id", "payment_card", "card_id"),
        ("device_id", "device_profile", "device_id"),
    ],
    "payment_transaction": [("payment_instruction_id", "payment_instruction", "payment_instruction_id")],
    "risk_signal": [("payment_instruction_id", "payment_instruction", "payment_instruction_id")],
    "fraud_alert": [
        ("risk_signal_id", "risk_signal", "risk_signal_id"),
        ("owning_business_unit_id", "business_unit", "business_unit_id"),
        ("owning_analyst_team_id", "analyst_team", "analyst_team_id"),
    ],
    "fraud_case": [
        ("primary_alert_id", "fraud_alert", "fraud_alert_id"),
        ("assigned_analyst_party_id", "party", "party_id"),
        ("owning_business_unit_id", "business_unit", "business_unit_id"),
        ("owning_analyst_team_id", "analyst_team", "analyst_team_id"),
        ("handling_region_id", "region", "region_id"),
    ],
    "investigation_event": [
        ("fraud_case_id", "fraud_case", "fraud_case_id"),
        ("actor_party_id", "party", "party_id"),
    ],
    "decision_record": [
        ("fraud_case_id", "fraud_case", "fraud_case_id"),
        ("decision_maker_party_id", "party", "party_id"),
    ],
    "case_disposition": [("decision_id", "decision_record", "decision_id")],
}


REQUIRED_FIELDS = {
    "reference_data_catalog": ["code_set_name", "code_value", "code_description", "is_active"],
    "calendar_day": ["calendar_date", "calendar_year", "calendar_month", "week_of_year"],
    "region": ["region_id", "region_code", "region_name", "country_group_code", "is_active"],
    "branch_territory": ["branch_territory_id", "branch_territory_code", "region_id"],
    "branch_location": ["branch_id", "branch_code", "branch_territory_id", "region_id", "country_code"],
    "business_unit": ["business_unit_id", "business_unit_code", "business_unit_name", "business_unit_type", "region_id"],
    "analyst_team": ["analyst_team_id", "analyst_team_code", "analyst_team_name", "business_unit_id", "region_id"],
    "party": ["party_id", "party_type", "party_status"],
    "party_org_assignment": ["party_org_assignment_id", "party_id", "assignment_role_code", "effective_from_at"],
    "deposit_account": [
        "deposit_account_id",
        "account_status",
        "product_type_code",
        "primary_party_id",
        "account_currency_code",
        "opened_at",
    ],
    "payment_card": ["card_id", "linked_account_id", "card_status"],
    "device_profile": ["device_id", "device_status"],
    "channel_event": ["channel_event_id", "channel_code", "event_at"],
    "payment_instruction": [
        "payment_instruction_id",
        "instruction_status",
        "debtor_account_id",
        "debtor_party_id",
        "creditor_party_id",
        "instructed_amount",
        "instructed_currency_code",
        "channel_event_id",
        "event_at",
    ],
    "payment_transaction": ["payment_transaction_id", "payment_instruction_id", "transaction_status", "booking_amount", "transaction_currency_code"],
    "risk_signal": ["risk_signal_id", "payment_instruction_id", "signal_type_code", "risk_level", "event_at"],
    "fraud_alert": ["fraud_alert_id", "risk_signal_id", "alert_status", "alert_severity", "created_at"],
    "fraud_case": ["fraud_case_id", "primary_alert_id", "case_status", "opened_at"],
    "investigation_event": ["investigation_event_id", "fraud_case_id", "investigation_event_type", "actor_party_id", "event_at"],
    "decision_record": ["decision_id", "fraud_case_id", "decision_type", "decision_status", "decision_maker_party_id", "decided_at"],
    "case_disposition": ["disposition_id", "decision_id", "disposition_code", "outcome_at"],
}


COUNTRIES = ["US", "CA", "GB", "IN", "DE", "AU", "SG", "AE", "FR", "NL"]
COUNTRY_GROUPS = ["north_america", "europe", "asia_pacific", "middle_east"]
CHANNELS = ["mobile", "online", "branch", "atm", "api", "contact_center"]
ACCOUNT_PRODUCTS = ["checking", "savings", "student_checking", "premium_checking"]
CARD_NETWORKS = ["visa", "mastercard", "amex", "discover"]
DEVICE_OSES = ["ios", "android", "windows", "macos", "linux"]
PAYMENT_PURPOSES = [
    "merchant_purchase",
    "recurring_bill",
    "p2p_transfer",
    "card_online_purchase",
    "atm_cash",
    "branch_payment",
    "wallet_topup",
    "utilities",
    "groceries",
    "travel",
]
MERCHANT_CATEGORIES = [
    "groceries",
    "travel",
    "gas",
    "utilities",
    "ecommerce",
    "dining",
    "health",
    "retail",
    "gaming",
    "telecom",
]
CUSTOMER_SEGMENTS = ["mass_market", "affluent", "small_business"]
CUSTOMER_TYPES = ["retail_consumer", "affluent_consumer", "small_business_owner", "merchant_entity", "employee"]
INDUSTRY_SECTORS = ["consumer", "retail_trade", "travel_services", "health_services", "telecom_services", "technology_services"]
BUSINESS_UNIT_TYPES = ["retail_banking", "fraud_operations", "digital_banking", "branch_network", "risk_management"]
ASSIGNMENT_ROLE_CODES = ["customer_owner", "merchant_owner", "fraud_analyst", "service_account", "branch_manager"]
AUTHENTICATION_RESULTS = ["success", "challenge_success", "challenge_failed", "step_up_required", "bypassed"]
SESSION_RISK_CODES = ["low", "medium", "high", "severe"]
PAYMENT_RAIL_CODES = ["ach", "wire", "sepa", "swift", "card", "rtp", "internal_transfer"]
TRANSACTION_DIRECTION_CODES = ["debit", "credit"]
ALERT_TYPE_CODES = ["behavioral", "velocity", "account_takeover", "card_abuse", "mule_network", "manual_review"]
ALERT_SOURCE_CODES = ["rules_engine", "ml_model", "network_feed", "analyst_referral"]
CASE_TYPE_CODES = ["account_takeover", "payment_fraud", "card_fraud", "mule_network", "review_case"]
CASE_PRIORITY_CODES = ["p1", "p2", "p3", "p4"]
ESCALATION_LEVEL_CODES = ["level_0", "level_1", "level_2", "level_3"]
EVENT_RESULT_CODES = ["pending", "evidence_found", "contact_completed", "no_response", "escalated", "closed"]
DECISION_REASON_CODES = ["high_risk_score", "device_mismatch", "new_payee", "velocity_breach", "analyst_override", "customer_confirmed"]
DECISION_CHANNEL_CODES = ["analyst_console", "automated_policy", "batch_review"]
RECOVERY_STATUS_CODES = ["not_applicable", "pending_recovery", "partially_recovered", "fully_recovered", "written_off"]


@dataclass(frozen=True)
class ScaleProfile:
    name: str
    customer_count: int
    merchant_count: int
    analyst_count: int
    service_party_count: int
    region_count: int
    branch_territory_count: int
    branch_count: int
    business_unit_count: int
    analyst_team_count: int
    account_count: int
    card_count: int
    device_count: int
    payment_count: int
    reference_rows: int
    risk_signal_count: int
    alert_count: int
    case_count: int
    investigation_count: int
    decision_count: int
    disposition_count: int


SCALE_PROFILES = {
    "small_fast": ScaleProfile(
        name="small_fast",
        customer_count=180,
        merchant_count=40,
        analyst_count=6,
        service_party_count=4,
        region_count=4,
        branch_territory_count=8,
        branch_count=16,
        business_unit_count=6,
        analyst_team_count=8,
        account_count=240,
        card_count=140,
        device_count=220,
        payment_count=1400,
        reference_rows=180,
        risk_signal_count=180,
        alert_count=70,
        case_count=34,
        investigation_count=90,
        decision_count=30,
        disposition_count=28,
    ),
    "medium_demo": ScaleProfile(
        name="medium_demo",
        customer_count=9500,
        merchant_count=1400,
        analyst_count=80,
        service_party_count=20,
        region_count=8,
        branch_territory_count=24,
        branch_count=80,
        business_unit_count=12,
        analyst_team_count=20,
        account_count=12500,
        card_count=8200,
        device_count=15000,
        payment_count=180000,
        reference_rows=240,
        risk_signal_count=18000,
        alert_count=4200,
        case_count=2100,
        investigation_count=5200,
        decision_count=2000,
        disposition_count=1900,
    ),
}
