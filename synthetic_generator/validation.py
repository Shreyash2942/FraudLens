from __future__ import annotations

from collections import Counter, defaultdict

from .contracts import DATASET_ORDER, FOREIGN_KEYS, PRIMARY_KEYS, REQUIRED_FIELDS
from .utils import parse_isoformat


def validate_generation(state) -> dict:
    datasets = state.datasets
    report = {
        "passed": True,
        "checks": {},
        "metrics": {},
        "errors": [],
    }

    row_counts = {name: len(datasets.get(name, [])) for name in DATASET_ORDER}
    report["metrics"]["row_counts"] = row_counts

    pk_results = {}
    for dataset_name, pk_field in PRIMARY_KEYS.items():
        if not pk_field:
            pk_results[dataset_name] = {"checked": False, "reason": "no_single_primary_key"}
            continue
        seen = set()
        duplicates = 0
        for row in datasets.get(dataset_name, []):
            value = row.get(pk_field)
            if value in seen:
                duplicates += 1
            else:
                seen.add(value)
        pk_results[dataset_name] = {"checked": True, "duplicates": duplicates}
        if duplicates:
            report["passed"] = False
            report["errors"].append(f"{dataset_name} has {duplicates} duplicate primary keys")
    report["checks"]["primary_keys"] = pk_results

    fk_results = {}
    indexes = {
        dataset_name: {row[pk]: row for row in datasets.get(dataset_name, [])}
        for dataset_name, pk in PRIMARY_KEYS.items()
        if pk
    }
    for dataset_name, rules in FOREIGN_KEYS.items():
        dataset_result = {}
        for field_name, target_dataset, target_pk in rules:
            invalid = 0
            for row in datasets.get(dataset_name, []):
                value = row.get(field_name, "")
                if value in ("", None):
                    continue
                if value not in indexes.get(target_dataset, {}):
                    invalid += 1
            dataset_result[field_name] = {"target_dataset": target_dataset, "invalid_count": invalid}
            if invalid:
                report["passed"] = False
                report["errors"].append(f"{dataset_name}.{field_name} has {invalid} invalid foreign keys")
        fk_results[dataset_name] = dataset_result
    report["checks"]["foreign_keys"] = fk_results

    required_results = {}
    for dataset_name, required_fields in REQUIRED_FIELDS.items():
        missing_counts = defaultdict(int)
        for row in datasets.get(dataset_name, []):
            for field in required_fields:
                value = row.get(field)
                if value in ("", None):
                    missing_counts[field] += 1
        required_results[dataset_name] = dict(missing_counts)
        if missing_counts:
            report["passed"] = False
            report["errors"].append(f"{dataset_name} has missing required values: {dict(missing_counts)}")
    report["checks"]["required_fields"] = required_results

    report["checks"]["temporal_consistency"] = _validate_temporal_consistency(datasets, report)
    report["checks"]["behavioral_consistency"] = _validate_behavioral_consistency(state, report)
    report["checks"]["org_structure_consistency"] = _validate_org_structure_consistency(state, report)
    if state.batch_mode == "blueprint":
        report["checks"]["blueprint_compliance"] = _validate_blueprint_compliance(state, report)

    return report


def _validate_temporal_consistency(datasets: dict[str, list[dict]], report: dict) -> dict:
    results = {
        "risk_after_payment": True,
        "alert_after_risk": True,
        "case_after_alert": True,
        "decision_after_case": True,
        "disposition_after_decision": True,
    }

    payment_index = {row["payment_instruction_id"]: row for row in datasets.get("payment_instruction", [])}
    risk_index = {row["risk_signal_id"]: row for row in datasets.get("risk_signal", [])}
    alert_index = {row["fraud_alert_id"]: row for row in datasets.get("fraud_alert", [])}
    case_index = {row["fraud_case_id"]: row for row in datasets.get("fraud_case", [])}
    decision_index = {row["decision_id"]: row for row in datasets.get("decision_record", [])}

    for row in datasets.get("risk_signal", []):
        payment_time = parse_isoformat(payment_index[row["payment_instruction_id"]]["event_at"])
        risk_time = parse_isoformat(row["event_at"])
        if payment_time and risk_time and risk_time < payment_time:
            results["risk_after_payment"] = False

    alert_by_risk = {row["risk_signal_id"]: row for row in datasets.get("fraud_alert", [])}
    for risk_id, alert in alert_by_risk.items():
        risk_time = parse_isoformat(risk_index[risk_id]["event_at"])
        alert_time = parse_isoformat(alert["created_at"])
        if risk_time and alert_time and alert_time < risk_time:
            results["alert_after_risk"] = False

    case_by_alert = {row["primary_alert_id"]: row for row in datasets.get("fraud_case", [])}
    for alert_id, case in case_by_alert.items():
        alert_time = parse_isoformat(alert_index[alert_id]["created_at"])
        case_time = parse_isoformat(case["opened_at"])
        if alert_time and case_time and case_time < alert_time:
            results["case_after_alert"] = False

    for row in datasets.get("decision_record", []):
        case_time = parse_isoformat(case_index[row["fraud_case_id"]]["opened_at"])
        decision_time = parse_isoformat(row["decided_at"])
        if case_time and decision_time and decision_time < case_time:
            results["decision_after_case"] = False

    for row in datasets.get("case_disposition", []):
        decision_time = parse_isoformat(decision_index[row["decision_id"]]["decided_at"])
        outcome_time = parse_isoformat(row["outcome_at"])
        if decision_time and outcome_time and outcome_time < decision_time:
            results["disposition_after_decision"] = False

    failing = [name for name, passed in results.items() if not passed]
    if failing:
        report["passed"] = False
        report["errors"].append(f"Temporal consistency failures: {', '.join(failing)}")
    return results


def _validate_behavioral_consistency(state, report: dict) -> dict:
    payment_rows = state.datasets.get("payment_instruction", [])
    risk_rows = state.datasets.get("risk_signal", [])
    alert_rows = state.datasets.get("fraud_alert", [])
    case_rows = state.datasets.get("fraud_case", [])
    decision_rows = state.datasets.get("decision_record", [])
    disposition_rows = state.datasets.get("case_disposition", [])

    payee_counter = Counter((row["debtor_account_id"], row["creditor_party_id"]) for row in payment_rows)
    repeat_payee_pairs = sum(1 for count in payee_counter.values() if count >= 3)
    recurring_count = sum(1 for meta in state.payment_meta.values() if meta.recurring)
    scenario_counter = Counter(meta.scenario for meta in state.payment_meta.values())
    channel_counter = Counter(row["channel_code"] for row in state.datasets.get("channel_event", []))

    results = {
        "repeat_payee_pairs": repeat_payee_pairs,
        "recurring_payment_count": recurring_count,
        "scenario_counts": dict(scenario_counter),
        "channel_distribution": dict(channel_counter),
        "risk_signal_ratio": round(len(risk_rows) / max(len(payment_rows), 1), 4),
        "alert_ratio": round(len(alert_rows) / max(len(risk_rows), 1), 4),
        "case_ratio": round(len(case_rows) / max(len(alert_rows), 1), 4),
        "decision_ratio": round(len(decision_rows) / max(len(case_rows), 1), 4),
        "disposition_ratio": round(len(disposition_rows) / max(len(decision_rows), 1), 4),
    }

    if repeat_payee_pairs <= 0 or recurring_count <= 0:
        report["passed"] = False
        report["errors"].append("Behavioral consistency failed: recurring or repeat-payee behavior not found")

    expected_scenarios = state.generation_context.get("expected_scenarios", [])
    required_scenarios = set(expected_scenarios) if state.batch_mode == "blueprint" and expected_scenarios else {
        "account_takeover",
        "card_not_present",
        "mule_transfer",
        "burst_velocity",
        "repeat_offender",
        "suspicious_new_device",
        "false_positive",
    }
    missing_scenarios = sorted(required_scenarios - set(scenario_counter))
    if missing_scenarios:
        report["passed"] = False
        report["errors"].append(f"Missing fraud scenarios: {', '.join(missing_scenarios)}")

    if not (0 < len(alert_rows) < len(risk_rows) < len(payment_rows)):
        report["passed"] = False
        report["errors"].append("Fraud branching ratios are not realistic enough")

    return results


def _validate_blueprint_compliance(state, report: dict) -> dict:
    scenario_counter = Counter(meta.scenario for meta in state.payment_meta.values() if meta.scenario != "normal")
    actual_lifecycle = {
        "risk_signal_count": len(state.datasets.get("risk_signal", [])),
        "alert_count": len(state.datasets.get("fraud_alert", [])),
        "case_count": len(state.datasets.get("fraud_case", [])),
        "decision_count": len(state.datasets.get("decision_record", [])),
        "disposition_count": len(state.datasets.get("case_disposition", [])),
    }
    expected_scenarios = dict(state.generation_context.get("scenario_counts", {}))
    expected_lifecycle = dict(state.generation_context.get("lifecycle_counts", {}))
    ratio_expectations = dict(state.generation_context.get("ratio_expectations", {}))
    ratio_tolerance = float(state.generation_context.get("ratio_tolerance", 0.05))
    dominant_scenario = state.generation_context.get("dominant_scenario")

    scenario_results = {}
    blueprint_passed = True
    for name, expected in expected_scenarios.items():
        actual = scenario_counter.get(name, 0)
        matches = actual == expected
        scenario_results[name] = {"expected": expected, "actual": actual, "matches": matches}
        if not matches:
            blueprint_passed = False
            report["passed"] = False
            report["errors"].append(f"Blueprint scenario target mismatch for {name}: expected {expected}, got {actual}")

    lifecycle_results = {}
    for name, expected in expected_lifecycle.items():
        actual = actual_lifecycle.get(name, 0)
        matches = actual == expected
        lifecycle_results[name] = {"expected": expected, "actual": actual, "matches": matches}
        if not matches:
            blueprint_passed = False
            report["passed"] = False
            report["errors"].append(f"Blueprint lifecycle target mismatch for {name}: expected {expected}, got {actual}")

    ratio_results = {}
    behavioral = report["checks"].get("behavioral_consistency", {})
    for name, expected in ratio_expectations.items():
        actual = behavioral.get(name)
        matches = actual is not None and abs(actual - expected) <= ratio_tolerance
        ratio_results[name] = {
            "expected": expected,
            "actual": actual,
            "tolerance": ratio_tolerance,
            "matches": matches,
        }
        if not matches:
            blueprint_passed = False
            report["passed"] = False
            report["errors"].append(f"Blueprint ratio mismatch for {name}: expected {expected}, got {actual}")

    dominant_result = None
    if dominant_scenario:
        ordered = scenario_counter.most_common()
        actual_dominant = ordered[0][0] if ordered else None
        dominant_result = {
            "expected": dominant_scenario,
            "actual": actual_dominant,
            "matches": actual_dominant == dominant_scenario,
        }
        if actual_dominant != dominant_scenario:
            blueprint_passed = False
            report["passed"] = False
            report["errors"].append(
                f"Blueprint dominant scenario mismatch: expected {dominant_scenario}, got {actual_dominant}"
            )

    return {
        "passed": blueprint_passed,
        "scenario_counts": scenario_results,
        "lifecycle_counts": lifecycle_results,
        "ratio_expectations": ratio_results,
        "dominant_scenario": dominant_result,
    }


def _validate_org_structure_consistency(state, report: dict) -> dict:
    accounts = state.datasets.get("deposit_account", [])
    alerts = state.datasets.get("fraud_alert", [])
    cases = state.datasets.get("fraud_case", [])
    assignments = state.datasets.get("party_org_assignment", [])
    channel_events = state.datasets.get("channel_event", [])
    branches = {row["branch_id"]: row for row in state.datasets.get("branch_location", [])}
    regions = {row["region_id"] for row in state.datasets.get("region", [])}
    units = {row["business_unit_id"] for row in state.datasets.get("business_unit", [])}
    teams = {row["analyst_team_id"] for row in state.datasets.get("analyst_team", [])}

    account_region_mismatch = 0
    for row in accounts:
        branch = branches.get(row.get("opened_branch_id", ""))
        if branch and row.get("account_region_id") != branch.get("region_id"):
            account_region_mismatch += 1

    alert_owner_mismatch = sum(
        1
        for row in alerts
        if row.get("owning_business_unit_id") and row.get("owning_business_unit_id") not in units
        or row.get("owning_analyst_team_id") and row.get("owning_analyst_team_id") not in teams
    )
    case_owner_mismatch = sum(
        1
        for row in cases
        if row.get("owning_business_unit_id") and row.get("owning_business_unit_id") not in units
        or row.get("owning_analyst_team_id") and row.get("owning_analyst_team_id") not in teams
        or row.get("handling_region_id") and row.get("handling_region_id") not in regions
    )
    branch_event_rows = sum(1 for row in channel_events if row.get("branch_id"))

    results = {
        "party_assignment_count": len(assignments),
        "branch_event_count": branch_event_rows,
        "account_region_mismatch_count": account_region_mismatch,
        "alert_owner_mismatch_count": alert_owner_mismatch,
        "case_owner_mismatch_count": case_owner_mismatch,
    }
    if account_region_mismatch or alert_owner_mismatch or case_owner_mismatch:
        report["passed"] = False
        report["errors"].append("Org structure consistency failures detected")
    return results
