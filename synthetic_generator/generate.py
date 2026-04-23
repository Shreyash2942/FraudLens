from __future__ import annotations

import argparse
import calendar
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random
from time import perf_counter

from .behavior import (
    build_analyst_teams,
    build_accounts,
    build_branch_locations,
    build_branch_territories,
    build_business_units,
    build_calendar_day,
    build_cards,
    build_devices,
    build_parties,
    build_payments_and_channels,
    build_party_org_assignments,
    build_reference_data,
    build_regions,
)
from .blueprints import list_builtin_blueprints, load_blueprint
from .contracts import DATASET_ORDER, SCALE_PROFILES
from .exporter import write_json, write_run_outputs
from .fraud import build_risk_alert_case_lifecycle, build_transactions, inject_fraud_scenarios
from .planner import build_generation_plan
from .progress import ProgressReporter
from .realism import build_faker
from .state import GenerationState
from .storage import upload_run_to_minio
from .validation import validate_generation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate FraudLens Phase 2 synthetic datasets.")
    parser.add_argument("--mode", choices=["mixed", "blueprint"], default="mixed", help="Generation mode.")
    parser.add_argument("--blueprint", help="Built-in blueprint name or path to a YAML blueprint file.")
    parser.add_argument("--list-blueprints", action="store_true", help="List available built-in blueprints and exit.")
    parser.add_argument("--output-dir", default="data", help="Base output directory for generated batch runs.")
    parser.add_argument("--days", type=int, help="Number of days to cover in the generated dataset.")
    parser.add_argument("--profile", choices=sorted(SCALE_PROFILES), help="Generation scale profile.")
    parser.add_argument("--seed", type=int, help="Deterministic random seed.")
    parser.add_argument("--validate", action="store_true", help="Run validation after generation.")
    parser.add_argument("--upload-minio", action="store_true", help="Upload generated outputs to MinIO if configured.")
    args = parser.parse_args(argv)

    if args.list_blueprints:
        for name in list_builtin_blueprints():
            print(name)
        return 0

    if args.mode == "blueprint" and not args.blueprint:
        parser.error("--blueprint is required when --mode blueprint is used")

    blueprint = load_blueprint(args.blueprint) if args.mode == "blueprint" and args.blueprint else None
    plan = build_generation_plan(args.mode, args.profile, args.days, args.seed, blueprint)
    profile = plan.profile
    start_at, end_at = _resolve_date_range(plan.days, plan.calendar_controls)
    batch_label = f"{plan.mode}_{_slug(plan.blueprint.name) if plan.blueprint else plan.profile_name}"
    batch_id = f"phase2_{batch_label}_{end_at.strftime('%Y%m%dT%H%M%SZ')}_seed{plan.seed}"
    batch_dir = Path(args.output_dir) / "batches" / batch_id
    rng = random.Random(plan.seed)
    fake = build_faker(plan.seed)
    progress = ProgressReporter()

    state = GenerationState(
        rng=rng,
        fake=fake,
        seed=plan.seed,
        run_id=batch_id,
        batch_mode=plan.mode,
        start_at=start_at,
        end_at=end_at,
        output_root=batch_dir,
        datasets={name: [] for name in DATASET_ORDER},
        generation_context=plan.as_context(),
        blueprint_name=plan.blueprint.name if plan.blueprint else None,
        blueprint_source=plan.blueprint.source if plan.blueprint else None,
    )

    execution_started_at = datetime.now(timezone.utc)
    total_started_at = perf_counter()
    stage_records: list[dict[str, str | float]] = []
    progress.info(
        f"Starting synthetic data batch | batch_id={batch_id} | mode={plan.mode} | profile={profile.name} | days={plan.days} | seed={plan.seed}"
    )

    _run_stage(stage_records, progress, "reference_data", "Building reference data", build_reference_data, state, profile)
    _run_stage(stage_records, progress, "calendar_day", "Building calendar dimension", build_calendar_day, state)
    _run_stage(stage_records, progress, "regions", "Building regions", build_regions, state, profile)
    _run_stage(stage_records, progress, "branch_territories", "Building branch territories", build_branch_territories, state, profile)
    _run_stage(stage_records, progress, "branch_locations", "Building branch locations", build_branch_locations, state, profile)
    _run_stage(stage_records, progress, "business_units", "Building business units", build_business_units, state, profile)
    _run_stage(stage_records, progress, "analyst_teams", "Building analyst teams", build_analyst_teams, state, profile)
    _run_stage(stage_records, progress, "parties", "Building parties", build_parties, state, profile)
    _run_stage(stage_records, progress, "party_org_assignments", "Building party org assignments", build_party_org_assignments, state)
    _run_stage(stage_records, progress, "accounts", "Building accounts", build_accounts, state, profile)
    _run_stage(stage_records, progress, "cards", "Building cards", build_cards, state, profile)
    _run_stage(stage_records, progress, "devices", "Building devices", build_devices, state, profile)
    _run_stage(
        stage_records,
        progress,
        "payments_and_channels",
        "Building payments and channel events",
        build_payments_and_channels,
        state,
        profile,
        progress,
    )
    _run_stage(
        stage_records,
        progress,
        "fraud_injection",
        "Injecting fraud scenarios",
        inject_fraud_scenarios,
        state,
        profile,
        progress,
    )
    _run_stage(stage_records, progress, "transactions", "Building payment transactions", build_transactions, state, progress)
    _run_stage(
        stage_records,
        progress,
        "fraud_lifecycle",
        "Building fraud lifecycle datasets",
        build_risk_alert_case_lifecycle,
        state,
        profile,
        progress,
    )

    output_paths = _run_stage(
        stage_records,
        progress,
        "landing_export",
        "Writing generated datasets",
        write_run_outputs,
        batch_dir,
        state.datasets,
        progress,
    )

    validation_report = {
        "passed": None,
        "status": "not_requested",
        "checks": {},
        "metrics": {},
        "errors": [],
    }
    if args.validate:
        validation_report = _run_stage(stage_records, progress, "quality_validation", "Running validation", validate_generation, state)
        validation_report["status"] = "completed"
    write_json(batch_dir / "quality" / "validation_report.json", validation_report)

    upload_report = {"status": "not_requested"}
    if args.upload_minio:
        upload_report = _run_stage(
            stage_records,
            progress,
            "object_storage_upload",
            "Uploading artifacts to MinIO",
            upload_run_to_minio,
            batch_dir,
            batch_id,
            progress,
        )

    manifest = {
        "batch_id": batch_id,
        "run_id": batch_id,
        "mode": plan.mode,
        "seed": plan.seed,
        "profile": profile.name,
        "date_range": {
            "start_at": start_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_at": end_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "days": plan.days,
        },
        "blueprint": _blueprint_manifest(plan),
        "datasets": {
            dataset_name: {
                "row_count": len(state.datasets.get(dataset_name, [])),
                "file_path": output_paths[dataset_name],
            }
            for dataset_name in DATASET_ORDER
        },
        "scenario_summary": _scenario_summary(state),
        "lifecycle_summary": _lifecycle_summary(state),
        "org_geography_summary": _org_geography_summary(state),
        "validation": {
            "status": validation_report.get("status"),
            "passed": validation_report.get("passed"),
            "error_count": len(validation_report.get("errors", [])),
        },
        "upload": upload_report,
    }
    write_json(batch_dir / "control" / "manifest.json", manifest)

    batch_control = {
        "batch_id": batch_id,
        "batch_type": "phase2_synthetic_generation",
        "mode": plan.mode,
        "profile": profile.name,
        "status": "completed",
        "execution_started_at": execution_started_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "execution_finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset_window": {
            "start_at": start_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_at": end_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "days": plan.days,
        },
        "seed": plan.seed,
        "control_summary": {
            "calendar_controls": dict(plan.calendar_controls),
            "geography_controls": dict(plan.geography_controls),
            "organization_controls": dict(plan.organization_controls),
            "customer_controls": dict(plan.customer_controls),
            "payment_controls": dict(plan.payment_controls),
            "fraud_ops_controls": dict(plan.fraud_ops_controls),
        },
        "blueprint": _blueprint_manifest(plan),
        "stages": stage_records,
    }
    write_json(batch_dir / "control" / "batch_control.json", batch_control)

    summary = {
        "batch_id": batch_id,
        "mode": plan.mode,
        "profile": profile.name,
        "datasets": {name: len(rows) for name, rows in state.datasets.items()},
        "validation_passed": validation_report.get("passed"),
        "upload_status": upload_report.get("status"),
    }
    progress.stage_end("Synthetic data batch", total_started_at, detail=f"output={batch_dir}")
    print(json.dumps(summary, indent=2))
    return 0


def _run_stage(stage_records: list[dict[str, str | float]], progress: ProgressReporter, stage_key: str, label: str, func, *args):
    wall_started_at = datetime.now(timezone.utc)
    started_at = progress.stage_start(label)
    result = func(*args)
    detail = _describe_stage_result(result)
    elapsed = perf_counter() - started_at
    progress.stage_end(label, started_at, detail=detail)
    stage_records.append(
        {
            "stage_key": stage_key,
            "stage_label": label,
            "status": "completed",
            "started_at": wall_started_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "elapsed_seconds": round(elapsed, 4),
            "detail": detail,
        }
    )
    return result


def _describe_stage_result(result) -> str:
    if isinstance(result, dict):
        if "status" in result:
            status = str(result["status"])
            extras = []
            if "file_count" in result:
                extras.append(f"files={result['file_count']}")
            if "reason" in result:
                extras.append(f"reason={result['reason']}")
            suffix = f" ({', '.join(extras)})" if extras else ""
            return f"status={status}{suffix}"
        if result and all(isinstance(value, str) for value in result.values()):
            return f"files={len(result)}"
    if isinstance(result, list):
        return f"rows={len(result)}"
    return ""


def _scenario_summary(state: GenerationState) -> dict[str, object]:
    scenario_counts = Counter(meta.scenario for meta in state.payment_meta.values())
    non_normal = {name: count for name, count in sorted(scenario_counts.items()) if name != "normal"}
    confirmed = sum(1 for meta in state.payment_meta.values() if meta.scenario != "normal" and meta.confirmed_fraud)
    non_confirmed = sum(1 for meta in state.payment_meta.values() if meta.scenario != "normal" and not meta.confirmed_fraud)
    return {
        "counts_by_scenario": non_normal,
        "confirmed_fraud_count": confirmed,
        "non_confirmed_count": non_confirmed,
    }


def _lifecycle_summary(state: GenerationState) -> dict[str, int]:
    return {
        "risk_signal_count": len(state.datasets.get("risk_signal", [])),
        "alert_count": len(state.datasets.get("fraud_alert", [])),
        "case_count": len(state.datasets.get("fraud_case", [])),
        "decision_count": len(state.datasets.get("decision_record", [])),
        "disposition_count": len(state.datasets.get("case_disposition", [])),
    }


def _org_geography_summary(state: GenerationState) -> dict[str, object]:
    accounts_by_region = Counter(row["account_region_id"] for row in state.datasets.get("deposit_account", []))
    alerts_by_unit = Counter(row["owning_business_unit_id"] for row in state.datasets.get("fraud_alert", []))
    cases_by_team = Counter(row["owning_analyst_team_id"] for row in state.datasets.get("fraud_case", []))
    branches_by_territory = Counter(row["branch_territory_id"] for row in state.datasets.get("branch_location", []))
    return {
        "accounts_by_region": dict(sorted(accounts_by_region.items())),
        "alerts_by_business_unit": dict(sorted(alerts_by_unit.items())),
        "cases_by_analyst_team": dict(sorted(cases_by_team.items())),
        "branches_by_territory": dict(sorted(branches_by_territory.items())),
    }


def _blueprint_manifest(plan) -> dict | None:
    if not plan.blueprint:
        return None
    return {
        "name": plan.blueprint.name,
        "source": plan.blueprint.source,
        "description": plan.blueprint.description,
        "calendar_controls": dict(plan.calendar_controls),
        "geography_controls": dict(plan.geography_controls),
        "organization_controls": dict(plan.organization_controls),
        "customer_controls": dict(plan.customer_controls),
        "payment_controls": dict(plan.payment_controls),
        "fraud_ops_controls": dict(plan.fraud_ops_controls),
    }


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def _resolve_date_range(days: int, calendar_controls: dict[str, object]) -> tuple[datetime, datetime]:
    controls = calendar_controls if isinstance(calendar_controls, dict) else {}
    start_year = _maybe_int(controls.get("start_year"))
    start_month = _bounded_month(_maybe_int(controls.get("start_month")))
    end_year = _maybe_int(controls.get("end_year"))
    end_month = _bounded_month(_maybe_int(controls.get("end_month")))
    if start_year and end_year:
        start_at = datetime(start_year, start_month or 1, 1, tzinfo=timezone.utc)
        last_day = calendar.monthrange(end_year, end_month or 12)[1]
        end_at = datetime(end_year, end_month or 12, last_day, 23, 59, 59, tzinfo=timezone.utc)
        return start_at, end_at
    if end_year:
        last_day = calendar.monthrange(end_year, end_month or 12)[1]
        end_at = datetime(end_year, end_month or 12, last_day, 23, 59, 59, tzinfo=timezone.utc)
        start_at = end_at - timedelta(days=days)
        return start_at, end_at
    end_at = datetime.now(timezone.utc).replace(microsecond=0)
    start_at = end_at - timedelta(days=days)
    return start_at, end_at


def _maybe_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _bounded_month(value: int | None) -> int | None:
    if value is None:
        return None
    return max(1, min(value, 12))


if __name__ == "__main__":
    raise SystemExit(main())
