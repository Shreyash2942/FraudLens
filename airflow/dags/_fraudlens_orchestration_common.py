from __future__ import annotations

import json
import os
import sys
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
