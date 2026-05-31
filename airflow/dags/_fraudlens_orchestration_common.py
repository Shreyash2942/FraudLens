from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


def resolve_repo_root() -> Path:
    configured = os.getenv("FRAUDLENS_REPO_ROOT", "").strip()
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured))
    candidates.extend(
        [
            Path("/home/datalab/fraudlens"),
            Path(__file__).resolve().parents[2],
        ]
    )
    for candidate in candidates:
        if (candidate / "synthetic_generator" / "contracts.py").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


REPO_ROOT = resolve_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synthetic_generator.contracts import DATASET_ORDER

ORCHESTRATION_PROFILE_PATH = REPO_ROOT / "airflow" / "config" / "orchestration_profiles.yml"
RUN_METADATA_SCHEMA_VERSION = "1.0"
RUN_METADATA_FIELDS: tuple[str, ...] = (
    "pipeline_run_id",
    "batch_id",
    "dag_id",
    "task_id",
    "task_group",
    "run_profile",
    "run_target",
    "execution_date_utc",
    "started_at_utc",
    "ended_at_utc",
    "run_status",
    "failure_category",
)


def load_orchestration_profile_contract() -> dict[str, Any]:
    if not ORCHESTRATION_PROFILE_PATH.exists():
        raise FileNotFoundError(f"Orchestration profile contract not found: {ORCHESTRATION_PROFILE_PATH}")
    with ORCHESTRATION_PROFILE_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError("Orchestration profile contract must be a mapping.")
    payload.setdefault("defaults", {})
    payload.setdefault("profiles", {})
    return payload


def allowed_orchestration_profiles() -> set[str]:
    contract = load_orchestration_profile_contract()
    profiles = contract.get("profiles", {})
    if not isinstance(profiles, dict):
        return set()
    return {str(name).strip().lower() for name in profiles.keys() if str(name).strip()}


def resolve_orchestration_profile(profile: str | None) -> str:
    contract = load_orchestration_profile_contract()
    defaults = contract.get("defaults", {})
    default_profile = str(defaults.get("profile", "local")).strip().lower()
    requested = (profile or default_profile).strip().lower()
    profiles = contract.get("profiles", {})
    if requested not in profiles:
        raise ValueError(f"Unsupported orchestration profile '{requested}'. Allowed: {sorted(profiles.keys())}")
    return requested


def orchestration_profile_settings(profile: str | None) -> dict[str, Any]:
    contract = load_orchestration_profile_contract()
    selected = resolve_orchestration_profile(profile)
    return contract["profiles"][selected]


def orchestration_defaults() -> dict[str, Any]:
    contract = load_orchestration_profile_contract()
    defaults = contract.get("defaults", {})
    if not isinstance(defaults, dict):
        return {}
    return defaults


def dag_profile_from_env() -> str:
    env_profile = os.getenv("ORCHESTRATION_PROFILE", "").strip().lower()
    if env_profile:
        return resolve_orchestration_profile(env_profile)
    return resolve_orchestration_profile(None)


def profile_runtime_settings(profile: str | None = None) -> dict[str, Any]:
    selected = resolve_orchestration_profile(profile) if profile else dag_profile_from_env()
    settings = orchestration_profile_settings(selected)
    runtime = settings.get("runtime", {})
    if not isinstance(runtime, dict):
        return {}
    return runtime


def schedule_for_profile(profile: str | None = None) -> str | None:
    runtime = profile_runtime_settings(profile)
    schedule_mode = str(runtime.get("schedule_mode", "manual")).strip().lower()
    if schedule_mode in {"manual", "ci_triggered"}:
        return None
    if schedule_mode == "daily":
        cron_expr = str(runtime.get("schedule_cron", "0 2 * * *")).strip()
        return cron_expr or "0 2 * * *"
    return None


def max_active_runs_for_profile(profile: str | None = None) -> int:
    runtime = profile_runtime_settings(profile)
    raw_value = runtime.get("max_active_runs", 1)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        value = 1
    return max(value, 1)


def run_window_for_profile(profile: str | None = None) -> tuple[str, str]:
    runtime = profile_runtime_settings(profile)
    start = str(runtime.get("run_window_start_utc", "00:00")).strip() or "00:00"
    end = str(runtime.get("run_window_end_utc", "23:59")).strip() or "23:59"
    return start, end


def dagrun_timeout_for_profile(profile: str | None = None) -> timedelta | None:
    runtime = profile_runtime_settings(profile)
    raw_value = runtime.get("dagrun_timeout_minutes", None)
    if raw_value in {None, "", 0, "0"}:
        return None
    try:
        minutes = int(raw_value)
    except (TypeError, ValueError):
        return None
    if minutes <= 0:
        return None
    return timedelta(minutes=minutes)


def runtime_policy_map(profile: str | None = None) -> dict[str, dict[str, Any]]:
    defaults = orchestration_defaults()
    default_map = defaults.get("runtime_policies", {})
    if not isinstance(default_map, dict):
        default_map = {}
    selected = resolve_orchestration_profile(profile) if profile else dag_profile_from_env()
    profile_settings = orchestration_profile_settings(selected)
    runtime = profile_settings.get("runtime", {})
    profile_map = runtime.get("runtime_policies", {}) if isinstance(runtime, dict) else {}
    if not isinstance(profile_map, dict):
        profile_map = {}

    merged: dict[str, dict[str, Any]] = {}
    for key, value in default_map.items():
        if isinstance(value, dict):
            merged[str(key)] = dict(value)
    for key, value in profile_map.items():
        if isinstance(value, dict):
            base = merged.get(str(key), {})
            base.update(value)
            merged[str(key)] = base
    return merged


def task_policy_kwargs(task_category: str, profile: str | None = None) -> dict[str, Any]:
    policy = runtime_policy_map(profile).get(task_category, {})

    retries = int(policy.get("retries", 0))
    retry_delay_minutes = int(policy.get("retry_delay_minutes", 1))
    max_retry_delay_minutes = int(policy.get("max_retry_delay_minutes", max(retry_delay_minutes, 1)))
    timeout_minutes = int(policy.get("execution_timeout_minutes", 30))
    retry_backoff = bool(policy.get("retry_exponential_backoff", False))

    return {
        "retries": max(retries, 0),
        "retry_delay": timedelta(minutes=max(retry_delay_minutes, 1)),
        "max_retry_delay": timedelta(minutes=max(max_retry_delay_minutes, 1)),
        "retry_exponential_backoff": retry_backoff,
        "execution_timeout": timedelta(minutes=max(timeout_minutes, 1)),
    }


def classify_failure_category(task_id: str, error_text: str) -> str:
    task = task_id.lower()
    text = error_text.lower()
    if any(marker in task for marker in ["input_assets", "trigger", "runtime_context"]):
        return "infra_transient"
    if any(marker in task for marker in ["contract", "alignment", "failure_policy"]):
        return "config_contract"
    if any(marker in task for marker in ["quality", "validation", "tag_test"]):
        return "data_quality"
    if any(marker in task for marker in ["governance", "traceability"]):
        return "governance_block"
    if "traceback" in text and "connection" in text:
        return "infra_transient"
    return "unknown"


def runtime_failure_callback(context: dict[str, Any]) -> None:
    dag_id = str(getattr(context.get("dag"), "dag_id", context.get("dag_id", "unknown_dag")))
    task_id = str(getattr(context.get("task"), "task_id", context.get("task_id", "unknown_task")))
    run_id = str(context.get("run_id", "unknown_run"))
    run_stamp = str(context.get("ts_nodash", "unknown_ts"))
    error = context.get("exception")
    error_text = repr(error) if error is not None else "unknown_exception"
    category = classify_failure_category(task_id, error_text)

    artifact_dir = REPO_ROOT / "airflow" / "artifacts" / "orchestration" / "failures" / dag_id / run_stamp
    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "dag_id": dag_id,
        "task_id": task_id,
        "run_id": run_id,
        "run_stamp": run_stamp,
        "failure_category": category,
        "error": error_text,
        "status": "FAILED",
    }
    target = artifact_dir / f"{task_id}.json"
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "task_failure_classified", **payload}))


def canonical_run_metadata(
    *,
    pipeline_run_id: str,
    batch_id: str,
    dag_id: str,
    task_id: str,
    task_group: str,
    run_profile: str,
    run_target: str,
    execution_date_utc: str,
    started_at_utc: str,
    ended_at_utc: str,
    run_status: str,
    failure_category: str | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_version": RUN_METADATA_SCHEMA_VERSION,
        "pipeline_run_id": pipeline_run_id,
        "batch_id": batch_id,
        "dag_id": dag_id,
        "task_id": task_id,
        "task_group": task_group,
        "run_profile": run_profile,
        "run_target": run_target,
        "execution_date_utc": execution_date_utc,
        "started_at_utc": started_at_utc,
        "ended_at_utc": ended_at_utc,
        "run_status": run_status,
        "failure_category": failure_category,
    }
    return payload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def log_orchestration_event(level: str, event: str, **fields: Any) -> None:
    payload = {
        "level": level.upper(),
        "event": event,
        "timestamp_utc": utc_now_iso(),
        **fields,
    }
    print(json.dumps(payload))


def infer_task_group(task_id: str) -> str:
    if "." in task_id:
        return task_id.split(".", 1)[0]
    if "__" in task_id:
        return task_id.split("__", 1)[0]
    return "root"


def latest_batch_id(data_root: Path | None = None) -> str:
    root = data_root or (REPO_ROOT / "data" / "batches")
    if not root.exists():
        raise FileNotFoundError(f"Batch root not found: {root}")
    dirs = [entry for entry in root.iterdir() if entry.is_dir()]
    if not dirs:
        raise FileNotFoundError(f"No batch directories found in: {root}")
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0].name


def bronze_dataset_order() -> list[str]:
    dataset_index = REPO_ROOT / "warehouse" / "snowflake-warehouse-setup" / "sql" / "bronze" / "dataset_index.json"
    if dataset_index.exists():
        with dataset_index.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        entries = payload.get("datasets", [])
        if isinstance(entries, list):
            ordered = [str(item.get("dataset")) for item in entries if isinstance(item, dict) and item.get("dataset")]
            if ordered:
                return ordered
    return list(DATASET_ORDER)


def parse_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


def parse_dataset_override(raw_value: Any) -> list[str] | None:
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    if not text or text.lower() == "from_contract":
        return None
    return [name.strip() for name in text.split(",") if name.strip()]


def validate_dataset_subset(requested: list[str] | None, valid_order: list[str]) -> list[str]:
    if requested is None:
        return list(valid_order)
    invalid = [name for name in requested if name not in valid_order]
    if invalid:
        raise ValueError(f"Invalid dataset names: {invalid}. Allowed: {valid_order}")
    return [name for name in valid_order if name in requested]


def orchestration_artifact_dir(workflow: str, run_stamp: str) -> Path:
    return REPO_ROOT / "airflow" / "artifacts" / "orchestration" / workflow / run_stamp


def observability_settings(profile: str | None) -> dict[str, Any]:
    settings = orchestration_profile_settings(profile)
    section = settings.get("observability", {})
    if not isinstance(section, dict):
        return {}
    return section


def observability_enabled(profile: str | None) -> bool:
    section = observability_settings(profile)
    return parse_bool(section.get("enabled"), default=True)


def observability_artifact_dir(signal_type: str, workflow: str, run_stamp: str) -> Path:
    return REPO_ROOT / "airflow" / "artifacts" / "observability" / signal_type / workflow / run_stamp


def emit_metric_event(
    *,
    workflow: str,
    run_stamp: str,
    metric_name: str,
    metric_value: float,
    metric_type: str,
    run_profile: str,
    payload: dict[str, Any],
) -> Path:
    section = observability_settings(run_profile)
    namespace = str(section.get("metrics_namespace", f"fraudlens.orchestration.{run_profile}")).strip()
    target_dir = observability_artifact_dir("metrics", workflow, run_stamp)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "metric_events.jsonl"
    event = {
        "metric_name": metric_name,
        "metric_value": metric_value,
        "metric_type": metric_type,
        "namespace": namespace,
        "emitted_at_utc": utc_now_iso(),
        **payload,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    log_orchestration_event("INFO", "metric_event_emitted", metric_name=metric_name, target_file=str(target))
    return target


def emit_lineage_event(
    *,
    workflow: str,
    run_stamp: str,
    event_type: str,
    run_profile: str,
    payload: dict[str, Any],
) -> Path:
    section = observability_settings(run_profile)
    namespace = str(section.get("lineage_namespace", f"fraudlens.orchestration.{run_profile}")).strip()
    target_dir = observability_artifact_dir("lineage", workflow, run_stamp)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "lineage_events.jsonl"
    event = {
        "event_type": event_type,
        "event_time_utc": utc_now_iso(),
        "namespace": namespace,
        **payload,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    log_orchestration_event("INFO", "lineage_event_emitted", event_type=event_type, target_file=str(target))
    return target
