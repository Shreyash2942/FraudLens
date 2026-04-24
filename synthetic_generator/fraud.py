from __future__ import annotations

from datetime import timedelta

from .contracts import ScaleProfile
from .progress import ProgressReporter
from .state import FraudCaseMeta, GenerationState
from .utils import SequenceIdGenerator, isoformat_utc, parse_isoformat


def inject_fraud_scenarios(
    state: GenerationState, profile: ScaleProfile, progress: ProgressReporter | None = None
) -> None:
    payment_ids = list(state.payment_meta)
    state.rng.shuffle(payment_ids)
    target = dict(state.generation_context.get("scenario_counts", {}))

    used = set()
    _apply_account_takeover(state, payment_ids, target.get("account_takeover", 0), used)
    _report_scenario_progress(progress, "account_takeover", used)
    _apply_card_not_present(state, payment_ids, target.get("card_not_present", 0), used)
    _report_scenario_progress(progress, "card_not_present", used)
    _apply_mule_transfer(state, target.get("mule_transfer", 0), used)
    _report_scenario_progress(progress, "mule_transfer", used)
    _apply_burst_velocity(state, target.get("burst_velocity", 0), used)
    _report_scenario_progress(progress, "burst_velocity", used)
    _apply_repeat_offender(state, target.get("repeat_offender", 0), used)
    _report_scenario_progress(progress, "repeat_offender", used)
    _apply_suspicious_new_device(state, payment_ids, target.get("suspicious_new_device", 0), used)
    _report_scenario_progress(progress, "suspicious_new_device", used)
    _apply_false_positive(state, payment_ids, target.get("false_positive", 0), used)
    _report_scenario_progress(progress, "false_positive", used)
    _enforce_fraud_mix_targets(state)
    _score_all_payments(state)


def build_transactions(state: GenerationState, progress: ProgressReporter | None = None) -> None:
    transaction_id = SequenceIdGenerator("PTX")
    rows = []
    total = len(state.payment_meta)
    for index, (instruction_id, meta) in enumerate(state.payment_meta.items(), start=1):
        instruction = state.payment_records[instruction_id]
        amount = float(instruction["instructed_amount"])
        status = _transaction_status_for(meta, instruction["instruction_status"], state)
        event_at = parse_isoformat(instruction["event_at"])
        settlement_at = None
        reversal_reason_code = ""
        if status in {"booked", "pending_settlement"} and event_at:
            settlement_at = isoformat_utc(event_at + timedelta(minutes=state.rng.randint(5, 360)))
        if status in {"reversed", "returned"}:
            reversal_reason_code = state.rng.choice(["fraud_review", "chargeback", "customer_claim", "network_return"])
            if event_at:
                settlement_at = isoformat_utc(event_at + timedelta(hours=state.rng.randint(4, 72)))
        merchant_category_code = _merchant_category_for(state, meta.creditor_party_id)
        rows.append(
            {
                "payment_transaction_id": transaction_id.next(),
                "payment_instruction_id": instruction_id,
                "transaction_status": status,
                "booking_amount": f"{amount:.2f}",
                "transaction_currency_code": instruction["instructed_currency_code"],
                "settlement_at": settlement_at or "",
                "merchant_category_code": merchant_category_code,
                "reversal_reason_code": reversal_reason_code,
                "posted_date": event_at.date().isoformat() if event_at else "",
                "value_date": (event_at + timedelta(days=state.rng.randint(0, 2))).date().isoformat() if event_at else "",
                "transaction_direction_code": "debit",
            }
        )
        if progress:
            progress.tick(
                key="transaction_generation",
                current=index,
                total=total,
                label="Generating payment transactions",
            )
    state.datasets["payment_transaction"] = rows


def build_risk_alert_case_lifecycle(
    state: GenerationState, profile: ScaleProfile, progress: ProgressReporter | None = None
) -> None:
    lifecycle_counts = state.generation_context.get("lifecycle_counts", {})
    risk_signal_count = int(lifecycle_counts.get("risk_signal_count", profile.risk_signal_count))
    alert_count = int(lifecycle_counts.get("alert_count", profile.alert_count))
    case_count = int(lifecycle_counts.get("case_count", profile.case_count))
    decision_count = int(lifecycle_counts.get("decision_count", profile.decision_count))
    disposition_count = int(lifecycle_counts.get("disposition_count", profile.disposition_count))

    ranked_payments = sorted(state.payment_meta.values(), key=lambda item: item.risk_score, reverse=True)
    risk_source = [item for item in ranked_payments if item.risk_score >= 42]
    if len(risk_source) < risk_signal_count:
        risk_source = ranked_payments[:risk_signal_count]
    else:
        risk_source = risk_source[:risk_signal_count]

    risk_signal_id = SequenceIdGenerator("RSK")
    risk_rows = []
    risk_by_payment = {}
    for meta in risk_source:
        signal_time = meta.event_at + timedelta(minutes=state.rng.randint(1, 90))
        risk_id = risk_signal_id.next()
        risk_rows.append(
            {
                "risk_signal_id": risk_id,
                "payment_instruction_id": meta.instruction_id,
                "signal_type_code": meta.scenario if meta.scenario != "normal" else _normal_signal_code(meta),
                "signal_score_amount": f"{meta.risk_score:.2f}",
                "risk_level": meta.risk_level,
                "event_at": isoformat_utc(signal_time),
            }
        )
        risk_by_payment[meta.instruction_id] = risk_rows[-1]
    state.datasets["risk_signal"] = risk_rows
    if progress:
        progress.info(f"Generated risk signals: {len(risk_rows):,}")

    alert_candidates = sorted(risk_rows, key=lambda row: float(row["signal_score_amount"]), reverse=True)
    alerts_to_create = alert_candidates[:alert_count]
    alert_id = SequenceIdGenerator("ALT")
    alert_rows = []
    alert_by_risk = {}
    for row in alerts_to_create:
        score = float(row["signal_score_amount"])
        severity = "critical" if score >= 88 else "high" if score >= 76 else "medium" if score >= 62 else "low"
        status = "open" if severity in {"critical", "high"} else state.rng.choice(["triaged", "resolved", "cancelled"])
        created_at = parse_isoformat(row["event_at"]) + timedelta(minutes=state.rng.randint(5, 60))
        instruction_id = row["payment_instruction_id"]
        account = state.account_profiles[state.payment_meta[instruction_id].account_id]
        owning_business_unit_id = account.servicing_business_unit_id
        owning_analyst_team_id = _team_for_business_unit(state, owning_business_unit_id)
        alert_row = {
            "fraud_alert_id": alert_id.next(),
            "risk_signal_id": row["risk_signal_id"],
            "alert_status": status,
            "alert_severity": severity,
            "queue_code": state.rng.choice(["fraud_ops", "high_risk", "manual_review", "customer_care"]),
            "created_at": isoformat_utc(created_at),
            "alert_type_code": _alert_type_for_signal(row["signal_type_code"]),
            "alert_source_code": _alert_source_for(state),
            "owning_business_unit_id": owning_business_unit_id,
            "owning_analyst_team_id": owning_analyst_team_id,
            "service_level_due_at": isoformat_utc(created_at + timedelta(hours=4 if severity in {"critical", "high"} else 24)),
        }
        alert_rows.append(alert_row)
        alert_by_risk[row["risk_signal_id"]] = alert_row
    state.datasets["fraud_alert"] = alert_rows
    if progress:
        progress.info(f"Generated fraud alerts: {len(alert_rows):,}")

    case_candidates = [
        alert for alert in alert_rows if alert["alert_severity"] in {"critical", "high"} or state.rng.random() < 0.22
    ]
    if len(case_candidates) < case_count:
        fallback_alerts = [alert for alert in alert_rows if alert not in case_candidates]
        case_candidates.extend(fallback_alerts[: max(0, case_count - len(case_candidates))])
    case_candidates = case_candidates[:case_count]
    case_id = SequenceIdGenerator("CAS")
    case_rows = []
    for alert in case_candidates:
        risk_row = next(item for item in risk_rows if item["risk_signal_id"] == alert["risk_signal_id"])
        instruction_id = risk_row["payment_instruction_id"]
        meta = state.payment_meta[instruction_id]
        opened_at = parse_isoformat(alert["created_at"]) + timedelta(minutes=state.rng.randint(15, 240))
        closed_at = opened_at + timedelta(hours=state.rng.randint(2, 96))
        fraud_case_id = case_id.next()
        assigned_analyst_party_id = state.rng.choice(state.analysts) if state.analysts else ""
        account = state.account_profiles[meta.account_id]
        case_rows.append(
            {
                "fraud_case_id": fraud_case_id,
                "primary_alert_id": alert["fraud_alert_id"],
                "case_status": "closed",
                "assigned_analyst_party_id": assigned_analyst_party_id,
                "opened_at": isoformat_utc(opened_at),
                "closed_at": isoformat_utc(closed_at),
                "case_type_code": _case_type_for_scenario(meta.scenario),
                "case_priority_code": _case_priority_for_severity(state, alert["alert_severity"]),
                "owning_business_unit_id": alert["owning_business_unit_id"],
                "owning_analyst_team_id": alert["owning_analyst_team_id"] or _team_for_business_unit(state, account.servicing_business_unit_id),
                "handling_region_id": account.account_region_id,
                "escalation_level_code": _escalation_for_severity(alert["alert_severity"]),
            }
        )
        state.fraud_case_meta[fraud_case_id] = FraudCaseMeta(
            fraud_case_id=fraud_case_id,
            primary_alert_id=alert["fraud_alert_id"],
            scenario=meta.scenario,
            confirmed_fraud=meta.confirmed_fraud,
            related_payment_instruction_id=instruction_id,
        )
        alert["alert_status"] = state.rng.choice(["escalated", "triaged"])
    state.datasets["fraud_case"] = case_rows
    if progress:
        progress.info(f"Generated fraud cases: {len(case_rows):,}")

    investigation_id = SequenceIdGenerator("INV")
    investigation_rows = []
    for case in case_rows:
        opened_at = parse_isoformat(case["opened_at"])
        actor = case["assigned_analyst_party_id"] or (state.analysts[0] if state.analysts else "")
        step_count = 2 if len(investigation_rows) >= profile.investigation_count else state.rng.randint(2, 3)
        for step in range(step_count):
            if len(investigation_rows) >= profile.investigation_count:
                break
            event_at = opened_at + timedelta(minutes=state.rng.randint(20, 240) + step * state.rng.randint(25, 180))
            investigation_rows.append(
                {
                    "investigation_event_id": investigation_id.next(),
                    "fraud_case_id": case["fraud_case_id"],
                    "investigation_event_type": state.rng.choice(
                        ["note_added", "evidence_attached", "outreach_attempted", "review_completed", "escalation"]
                    ),
                    "actor_party_id": actor or state.rng.choice(state.services),
                    "event_at": isoformat_utc(event_at),
                    "event_result_code": state.rng.choice(["pending", "evidence_found", "contact_completed", "no_response", "escalated", "closed"]),
                    "elapsed_minutes": str(state.rng.randint(10, 180)),
                }
            )
    state.datasets["investigation_event"] = investigation_rows
    if progress:
        progress.info(f"Generated investigation events: {len(investigation_rows):,}")

    decision_id = SequenceIdGenerator("DEC")
    decision_rows = []
    decision_cases = case_rows[:decision_count]
    decision_targets = _expand_mix_targets(decision_count, state.generation_context.get("decision_mix", {}), state)
    for index, case in enumerate(decision_cases):
        case_meta = state.fraud_case_meta[case["fraud_case_id"]]
        decision_time = parse_isoformat(case["closed_at"]) - timedelta(minutes=state.rng.randint(5, 30))
        decision_rows.append(
            {
                "decision_id": decision_id.next(),
                "fraud_case_id": case["fraud_case_id"],
                "decision_type": decision_targets[index] if decision_targets else _decision_type_for(state, case_meta),
                "decision_status": "executed",
                "decision_maker_party_id": case["assigned_analyst_party_id"] or state.rng.choice(state.analysts),
                "decided_at": isoformat_utc(decision_time),
                "decision_reason_code": _decision_reason_for_case(state, case_meta),
                "decision_channel_code": state.rng.choice(["analyst_console", "automated_policy", "batch_review"]),
                "policy_name": _policy_name_for_scenario(case_meta.scenario),
                "rule_set_version": f"v{state.rng.randint(1, 3)}.{state.rng.randint(0, 9)}",
            }
        )
    state.datasets["decision_record"] = decision_rows
    if progress:
        progress.info(f"Generated decision records: {len(decision_rows):,}")

    disposition_id = SequenceIdGenerator("DSP")
    disposition_rows = []
    decisions_for_disposition = decision_rows[:disposition_count]
    disposition_targets = _expand_mix_targets(disposition_count, state.generation_context.get("disposition_mix", {}), state)
    for index, decision in enumerate(decisions_for_disposition):
        case_meta = state.fraud_case_meta[decision["fraud_case_id"]]
        outcome_time = parse_isoformat(decision["decided_at"]) + timedelta(minutes=state.rng.randint(20, 240))
        related_payment = state.payment_records[case_meta.related_payment_instruction_id]
        if disposition_targets:
            disposition_code = disposition_targets[index]
            financial_impact = _financial_impact_for_disposition(state, disposition_code, float(related_payment["instructed_amount"]))
        else:
            disposition_code, financial_impact = _disposition_for(state, case_meta, float(related_payment["instructed_amount"]))
        loss_amount, recovered_amount, write_off_amount = _disposition_amounts(financial_impact, disposition_code, float(related_payment["instructed_amount"]))
        recovery_status_code = _recovery_status_for_disposition(state, disposition_code, recovered_amount, write_off_amount)
        disposition_rows.append(
            {
                "disposition_id": disposition_id.next(),
                "decision_id": decision["decision_id"],
                "disposition_code": disposition_code,
                "financial_impact_amount": f"{financial_impact:.2f}" if financial_impact is not None else "",
                "outcome_at": isoformat_utc(outcome_time),
                "loss_amount": f"{loss_amount:.2f}" if loss_amount is not None else "",
                "recovered_amount": f"{recovered_amount:.2f}" if recovered_amount is not None else "",
                "write_off_amount": f"{write_off_amount:.2f}" if write_off_amount is not None else "",
                "recovery_status_code": recovery_status_code,
            }
        )
    state.datasets["case_disposition"] = disposition_rows
    if progress:
        progress.info(f"Generated case dispositions: {len(disposition_rows):,}")


def _report_scenario_progress(progress: ProgressReporter | None, scenario_name: str, used: set[str]) -> None:
    if progress:
        progress.info(f"Applied {scenario_name} scenario adjustments | tagged payments so far: {len(used):,}")


def _apply_account_takeover(state: GenerationState, payment_ids: list[str], count: int, used: set[str]) -> None:
    for instruction_id in payment_ids:
        if count <= 0:
            return
        meta = state.payment_meta[instruction_id]
        if instruction_id in used:
            continue
        if meta.archetype == "recurring_bill":
            continue
        used.add(instruction_id)
        meta.scenario = "account_takeover"
        meta.confirmed_fraud = True
        meta.new_device = True
        meta.new_payee = True
        meta.off_hours = True
        _mutate_digital_payment(state, meta, min_amount=750, max_amount=5200, shared_device=state.rng.random() < 0.35)
        count -= 1


def _apply_card_not_present(state: GenerationState, payment_ids: list[str], count: int, used: set[str]) -> None:
    for instruction_id in payment_ids:
        if count <= 0:
            return
        meta = state.payment_meta[instruction_id]
        row = state.payment_records[instruction_id]
        if instruction_id in used or not row["card_id"]:
            continue
        used.add(instruction_id)
        meta.scenario = "card_not_present"
        meta.confirmed_fraud = True
        meta.new_device = True
        meta.new_payee = True
        _mutate_digital_payment(state, meta, min_amount=120, max_amount=2400, shared_device=False)
        row["payment_purpose_code"] = "card_online_purchase"
        count -= 1


def _apply_mule_transfer(state: GenerationState, count: int, used: set[str]) -> None:
    if count <= 0:
        return
    mule_parties = state.rng.sample(state.customers, k=min(12, len(state.customers)))
    account_ids = list(state.account_payment_ids)
    remaining = count
    cluster_number = 0
    attempts = 0
    while remaining > 0 and account_ids and attempts < max(25, count * 3):
        attempts += 1
        cluster_account_ids = state.rng.sample(account_ids, k=min(6, len(account_ids)))
        mule_party_id = state.rng.choice(mule_parties)
        cluster_tag = f"mule_{cluster_number:03d}"
        for account_id in cluster_account_ids:
            payment_ids = state.account_payment_ids.get(account_id, [])
            if not payment_ids:
                continue
            instruction_id = state.rng.choice(payment_ids)
            if instruction_id in used:
                continue
            used.add(instruction_id)
            meta = state.payment_meta[instruction_id]
            row = state.payment_records[instruction_id]
            meta.scenario = "mule_transfer"
            meta.confirmed_fraud = True
            meta.new_payee = True
            meta.cluster_id = cluster_tag
            meta.creditor_party_id = mule_party_id
            row["creditor_party_id"] = mule_party_id
            row["payment_purpose_code"] = "p2p_transfer"
            _mutate_digital_payment(state, meta, min_amount=900, max_amount=6800, shared_device=False)
            meta.event_at = meta.event_at.replace(minute=state.rng.randint(0, 20))
            row["event_at"] = isoformat_utc(meta.event_at)
            state.channel_records[row["channel_event_id"]]["event_at"] = row["event_at"]
            remaining -= 1
            if remaining <= 0:
                return
        cluster_number += 1


def _apply_burst_velocity(state: GenerationState, count: int, used: set[str]) -> None:
    if count <= 0:
        return
    candidate_accounts = [aid for aid, ids in state.account_payment_ids.items() if len(ids) >= 4]
    remaining = count
    cluster_number = 0
    attempts = 0
    while remaining > 0 and candidate_accounts and attempts < max(30, count * 4):
        attempts += 1
        account_id = state.rng.choice(candidate_accounts)
        payment_ids = [pid for pid in state.account_payment_ids[account_id] if pid not in used]
        if len(payment_ids) < 2:
            candidate_accounts = [aid for aid in candidate_accounts if aid != account_id]
            continue
        cluster_size = min(len(payment_ids), max(2, state.rng.randint(3, 6)), remaining)
        cluster_ids = state.rng.sample(payment_ids, k=cluster_size)
        anchor_time = state.payment_meta[cluster_ids[0]].event_at
        for index, instruction_id in enumerate(cluster_ids):
            meta = state.payment_meta[instruction_id]
            used.add(instruction_id)
            meta.scenario = "burst_velocity"
            meta.confirmed_fraud = state.rng.random() < 0.7
            meta.cluster_id = f"burst_{cluster_number:03d}"
            meta.new_payee = True
            meta.event_at = anchor_time + timedelta(minutes=index * state.rng.randint(2, 10))
            row = state.payment_records[instruction_id]
            row["event_at"] = isoformat_utc(meta.event_at)
            state.channel_records[row["channel_event_id"]]["event_at"] = row["event_at"]
            row["instructed_amount"] = f"{state.rng.uniform(150.0, 2200.0):.2f}"
            remaining -= 1
            if remaining <= 0:
                return
        cluster_number += 1


def _apply_repeat_offender(state: GenerationState, count: int, used: set[str]) -> None:
    if not state.shared_risky_device_ids:
        return
    if count <= 0:
        return
    shared_device = state.rng.choice(state.shared_risky_device_ids)
    repeat_creditor = state.rng.choice(state.customers)
    account_ids = list(state.account_payment_ids)
    remaining = count
    attempts = 0
    while remaining > 0 and account_ids and attempts < max(20, count * 3):
        attempts += 1
        account_id = state.rng.choice(account_ids)
        applied_in_account = False
        for instruction_id in state.account_payment_ids.get(account_id, []):
            if remaining <= 0:
                return
            if instruction_id in used:
                continue
            meta = state.payment_meta[instruction_id]
            used.add(instruction_id)
            meta.scenario = "repeat_offender"
            meta.confirmed_fraud = True
            meta.new_device = True
            meta.new_payee = True
            meta.shared_device = True
            meta.creditor_party_id = repeat_creditor
            row = state.payment_records[instruction_id]
            row["creditor_party_id"] = repeat_creditor
            row["device_id"] = shared_device
            _mutate_digital_payment(state, meta, min_amount=250, max_amount=3600, shared_device=True)
            remaining -= 1
            applied_in_account = True
            if remaining <= 0:
                return
            if not _realism_flag(state, "emphasize_shared_device_clustering"):
                break
        if not applied_in_account:
            account_ids = [aid for aid in account_ids if aid != account_id]


def _apply_suspicious_new_device(state: GenerationState, payment_ids: list[str], count: int, used: set[str]) -> None:
    for instruction_id in payment_ids:
        if count <= 0:
            return
        if instruction_id in used:
            continue
        meta = state.payment_meta[instruction_id]
        used.add(instruction_id)
        meta.scenario = "suspicious_new_device"
        meta.confirmed_fraud = state.rng.random() < 0.45
        meta.new_device = True
        meta.new_payee = state.rng.random() < 0.55
        _mutate_digital_payment(state, meta, min_amount=120, max_amount=1600, shared_device=False)
        count -= 1


def _apply_false_positive(state: GenerationState, payment_ids: list[str], count: int, used: set[str]) -> None:
    for instruction_id in payment_ids:
        if count <= 0:
            return
        if instruction_id in used:
            continue
        meta = state.payment_meta[instruction_id]
        used.add(instruction_id)
        meta.scenario = "false_positive"
        meta.confirmed_fraud = False
        meta.new_device = True
        meta.new_payee = state.rng.random() < 0.2
        _mutate_digital_payment(state, meta, min_amount=180, max_amount=2400, shared_device=False)
        count -= 1


def _mutate_digital_payment(state: GenerationState, meta, min_amount: float, max_amount: float, shared_device: bool) -> None:
    row = state.payment_records[meta.instruction_id]
    meta.shared_device = shared_device
    emphasize_off_hours = _realism_flag(state, "emphasize_off_hours")
    emphasize_new_device = _realism_flag(state, "emphasize_new_device_behavior")
    emphasize_new_payees = _realism_flag(state, "emphasize_new_payees")
    meta.off_hours = True if emphasize_off_hours else state.rng.random() < 0.55
    meta.new_device = True if emphasize_new_device else meta.new_device
    meta.new_payee = True if emphasize_new_payees else meta.new_payee
    if meta.off_hours:
        meta.event_at = meta.event_at.replace(
            hour=state.rng.choice([0, 1, 2, 3, 4, 5, 22, 23]),
            minute=state.rng.randint(0, 59),
            second=state.rng.randint(0, 59),
        )
    else:
        meta.event_at = meta.event_at.replace(
            hour=state.rng.choice([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]),
            minute=state.rng.randint(0, 59),
            second=state.rng.randint(0, 59),
        )
    row["event_at"] = isoformat_utc(meta.event_at)
    state.channel_records[row["channel_event_id"]]["event_at"] = row["event_at"]
    state.channel_records[row["channel_event_id"]]["channel_code"] = state.rng.choice(["mobile", "online", "api"])
    row["instructed_amount"] = f"{state.rng.uniform(min_amount, max_amount):.2f}"
    if state.shared_risky_device_ids and (shared_device or meta.new_device or _realism_flag(state, "emphasize_shared_device_clustering")):
        row["device_id"] = state.rng.choice(state.shared_risky_device_ids)


def _score_all_payments(state: GenerationState) -> None:
    for meta in state.payment_meta.values():
        row = state.payment_records[meta.instruction_id]
        amount = float(row["instructed_amount"])
        score = 18.0
        if amount >= 1800:
            score += 18
        elif amount >= 900:
            score += 11
        elif amount >= 300:
            score += 4
        if meta.recurring:
            score -= 8
        if meta.new_payee:
            score += 10
        if meta.new_device:
            score += 16
        if meta.shared_device:
            score += 18
        if meta.off_hours:
            score += 8
        if meta.cluster_id:
            score += 12
        if state.channel_records[meta.channel_event_id]["channel_code"] in {"mobile", "online", "api"}:
            score += 4
        scenario_bonus = {
            "normal": 0,
            "account_takeover": 34,
            "card_not_present": 28,
            "mule_transfer": 30,
            "burst_velocity": 24,
            "repeat_offender": 26,
            "suspicious_new_device": 18,
            "false_positive": 20,
        }
        score += scenario_bonus.get(meta.scenario, 0)
        if meta.confirmed_fraud:
            score += 10
        if meta.scenario == "false_positive":
            score -= 6
        score = max(10.0, min(score, 99.0))
        meta.risk_score = round(score, 2)
        meta.risk_level = "severe" if score >= 85 else "high" if score >= 70 else "medium" if score >= 50 else "low"


def _transaction_status_for(meta, instruction_status: str, state: GenerationState) -> str:
    if instruction_status in {"rejected", "cancelled"}:
        return "declined"
    if meta.scenario == "false_positive":
        return state.rng.choices(["booked", "pending_settlement", "declined"], weights=[0.72, 0.18, 0.1], k=1)[0]
    if meta.confirmed_fraud:
        if _realism_flag(state, "emphasize_reversals"):
            return state.rng.choices(["booked", "declined", "reversed", "returned"], weights=[0.28, 0.18, 0.32, 0.22], k=1)[0]
        return state.rng.choices(["booked", "declined", "reversed", "returned"], weights=[0.42, 0.24, 0.2, 0.14], k=1)[0]
    if meta.risk_score >= 60:
        return state.rng.choices(["booked", "pending_settlement", "declined"], weights=[0.78, 0.15, 0.07], k=1)[0]
    return state.rng.choices(["booked", "pending_settlement", "declined"], weights=[0.9, 0.07, 0.03], k=1)[0]


def _merchant_category_for(state: GenerationState, creditor_party_id: str) -> str:
    merchant = state.merchant_profiles.get(creditor_party_id)
    return merchant.category_code if merchant else ""


def _team_for_business_unit(state: GenerationState, business_unit_id: str) -> str:
    candidates = [team_id for team_id, team in state.analyst_team_profiles.items() if team.business_unit_id == business_unit_id]
    return state.rng.choice(candidates) if candidates else ""


def _alert_type_for_signal(signal_type_code: str) -> str:
    mapping = {
        "account_takeover": "account_takeover",
        "card_not_present": "card_abuse",
        "mule_transfer": "mule_network",
        "burst_velocity": "velocity",
        "repeat_offender": "behavioral",
        "suspicious_new_device": "behavioral",
        "false_positive": "manual_review",
    }
    return mapping.get(signal_type_code, "behavioral")


def _case_type_for_scenario(scenario: str) -> str:
    mapping = {
        "account_takeover": "account_takeover",
        "card_not_present": "card_fraud",
        "mule_transfer": "mule_network",
        "burst_velocity": "payment_fraud",
        "repeat_offender": "payment_fraud",
        "suspicious_new_device": "review_case",
        "false_positive": "review_case",
    }
    return mapping.get(scenario, "payment_fraud")


def _alert_source_for(state: GenerationState) -> str:
    controls = state.generation_context.get("fraud_ops_controls", {})
    source_mix = controls.get("alert_source_mix") if isinstance(controls, dict) else None
    options = ["rules_engine", "ml_model", "network_feed", "analyst_referral"]
    if isinstance(source_mix, dict) and source_mix:
        weights = [float(source_mix.get(option, 1.0)) for option in options]
        return state.rng.choices(options, weights=weights, k=1)[0]
    return state.rng.choices(options, weights=[0.46, 0.32, 0.16, 0.06], k=1)[0]


def _case_priority_for_severity(state: GenerationState, severity: str) -> str:
    controls = state.generation_context.get("fraud_ops_controls", {})
    priority_mix = controls.get("case_priority_mix") if isinstance(controls, dict) else None
    if isinstance(priority_mix, dict) and priority_mix:
        options = ["p1", "p2", "p3", "p4"]
        weights = [float(priority_mix.get(option, 1.0)) for option in options]
        return state.rng.choices(options, weights=weights, k=1)[0]
    mapping = {
        "critical": "p1",
        "high": "p2",
        "medium": "p3",
        "low": "p4",
    }
    return mapping.get(severity, "p3")


def _escalation_for_severity(severity: str) -> str:
    mapping = {
        "critical": "level_3",
        "high": "level_2",
        "medium": "level_1",
        "low": "level_0",
    }
    return mapping.get(severity, "level_1")


def _normal_signal_code(meta) -> str:
    if meta.new_payee and meta.new_device:
        return "rule_new_payee"
    if meta.risk_score >= 65:
        return "rule_high_value"
    return "rule_new_payee"


def _decision_type_for(state: GenerationState, case_meta: FraudCaseMeta) -> str:
    if case_meta.confirmed_fraud:
        return state.rng.choices(["decline", "hold", "file_sar"], weights=[0.45, 0.35, 0.2], k=1)[0]
    if case_meta.scenario == "false_positive":
        return state.rng.choices(["close_no_fraud", "approve"], weights=[0.7, 0.3], k=1)[0]
    return state.rng.choices(["challenge", "close_no_fraud", "approve"], weights=[0.4, 0.35, 0.25], k=1)[0]


def _decision_reason_for_case(state: GenerationState, case_meta: FraudCaseMeta) -> str:
    controls = state.generation_context.get("fraud_ops_controls", {})
    reason_mix = controls.get("decision_reason_mix") if isinstance(controls, dict) else None
    if isinstance(reason_mix, dict) and reason_mix:
        options = list(reason_mix)
        weights = [float(reason_mix.get(option, 1.0)) for option in options]
        return state.rng.choices(options, weights=weights, k=1)[0]
    mapping = {
        "account_takeover": ["device_mismatch", "high_risk_score", "analyst_override"],
        "card_not_present": ["velocity_breach", "high_risk_score", "device_mismatch"],
        "mule_transfer": ["new_payee", "velocity_breach", "high_risk_score"],
        "burst_velocity": ["velocity_breach", "high_risk_score"],
        "repeat_offender": ["device_mismatch", "velocity_breach"],
        "suspicious_new_device": ["device_mismatch", "high_risk_score"],
        "false_positive": ["analyst_override", "customer_confirmed"],
    }
    return state.rng.choice(mapping.get(case_meta.scenario, ["high_risk_score"]))


def _policy_name_for_scenario(scenario: str) -> str:
    mapping = {
        "account_takeover": "ATO_Shield",
        "card_not_present": "Card_Guard",
        "mule_transfer": "Mule_Link_Review",
        "burst_velocity": "Velocity_Watch",
        "repeat_offender": "Repeat_Offender_Monitor",
        "suspicious_new_device": "Device_Trust_Policy",
        "false_positive": "Review_Exception_Policy",
    }
    return mapping.get(scenario, "Fraud_Control_Framework")


def _disposition_for(state: GenerationState, case_meta: FraudCaseMeta, amount: float) -> tuple[str, float | None]:
    if case_meta.confirmed_fraud:
        weights = [0.28, 0.52, 0.2] if _realism_flag(state, "emphasize_recoveries") else [0.4, 0.35, 0.25]
        outcome = state.rng.choices(["confirmed_fraud", "recovered", "written_off"], weights=weights, k=1)[0]
        return outcome, _financial_impact_for_disposition(state, outcome, amount)
    if case_meta.scenario == "false_positive":
        return "false_positive", None
    return "customer_error", round(amount * state.rng.uniform(0.1, 0.5), 2) if state.rng.random() < 0.35 else None


def _expand_mix_targets(total: int, mix: dict[str, int], state: GenerationState) -> list[str]:
    if not mix:
        return []
    expanded: list[str] = []
    for value, count in mix.items():
        expanded.extend([value] * count)
    if len(expanded) < total:
        expanded.extend([state.rng.choice(list(mix))] * (total - len(expanded)))
    state.rng.shuffle(expanded)
    return expanded[:total]


def _financial_impact_for_disposition(state: GenerationState, disposition_code: str, amount: float) -> float | None:
    if disposition_code == "false_positive":
        return None
    if disposition_code == "customer_error":
        return round(amount * state.rng.uniform(0.1, 0.5), 2) if state.rng.random() < 0.35 else None
    if disposition_code == "recovered":
        return round(amount * state.rng.uniform(0.2, 0.8), 2)
    if disposition_code == "written_off":
        return round(amount * state.rng.uniform(0.5, 1.0), 2)
    return round(amount * state.rng.uniform(0.4, 1.0), 2)


def _disposition_amounts(
    financial_impact: float | None,
    disposition_code: str,
    instructed_amount: float,
) -> tuple[float | None, float | None, float | None]:
    if disposition_code == "false_positive":
        return None, None, None
    loss_amount = financial_impact if financial_impact is not None else round(instructed_amount * 0.2, 2)
    if disposition_code == "recovered":
        recovered_amount = financial_impact if financial_impact is not None else round(instructed_amount * 0.5, 2)
        return loss_amount, recovered_amount, 0.0
    if disposition_code == "written_off":
        write_off_amount = financial_impact if financial_impact is not None else round(instructed_amount * 0.7, 2)
        return loss_amount, 0.0, write_off_amount
    if disposition_code == "customer_error":
        return loss_amount, 0.0, 0.0
    return loss_amount, 0.0, 0.0


def _recovery_status_for_disposition(
    state: GenerationState,
    disposition_code: str,
    recovered_amount: float | None,
    write_off_amount: float | None,
) -> str:
    controls = state.generation_context.get("fraud_ops_controls", {})
    recovery_mix = controls.get("recovery_status_mix") if isinstance(controls, dict) else None
    if isinstance(recovery_mix, dict) and recovery_mix:
        options = list(recovery_mix)
        weights = [float(recovery_mix.get(option, 1.0)) for option in options]
        return state.rng.choices(options, weights=weights, k=1)[0]
    if disposition_code == "false_positive":
        return "not_applicable"
    if disposition_code == "recovered":
        return "fully_recovered" if recovered_amount and recovered_amount > 0 else "pending_recovery"
    if disposition_code == "written_off":
        return "written_off"
    if recovered_amount and recovered_amount > 0:
        return "partially_recovered"
    return "pending_recovery"


def _enforce_fraud_mix_targets(state: GenerationState) -> None:
    scenario_payments = [meta for meta in state.payment_meta.values() if meta.scenario != "normal"]
    if not scenario_payments:
        return

    target_confirmed = state.generation_context.get("confirmed_fraud_target")
    target_false_positive = state.generation_context.get("false_positive_target")
    if target_confirmed is None and target_false_positive is None:
        return

    total = len(scenario_payments)
    if target_false_positive is None and target_confirmed is not None:
        target_false_positive = max(0, total - int(target_confirmed))
    if target_confirmed is None and target_false_positive is not None:
        target_confirmed = max(0, total - int(target_false_positive))
    target_confirmed = max(0, min(int(target_confirmed or 0), total))
    target_false_positive = max(0, min(int(target_false_positive or 0), total))

    ordered = sorted(
        scenario_payments,
        key=lambda meta: (
            0 if meta.scenario == "false_positive" else 1,
            0 if meta.scenario == "suspicious_new_device" else 1,
            meta.instruction_id,
        ),
    )
    false_set = {meta.instruction_id for meta in ordered[:target_false_positive]}
    for meta in scenario_payments:
        meta.confirmed_fraud = meta.instruction_id not in false_set


def _realism_flag(state: GenerationState, key: str) -> bool:
    realism = state.generation_context.get("realism_controls", {})
    return bool(realism.get(key, False)) if isinstance(realism, dict) else False
