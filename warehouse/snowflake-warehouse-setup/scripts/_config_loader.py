from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_profile(profile_name: str | None = None) -> dict[str, Any]:
    selected = (profile_name or os.getenv("PHASE3_ENV", "local")).strip().lower()
    if selected not in {"local", "cloud"}:
        raise ValueError(f"Unsupported PHASE3_ENV '{selected}'. Use 'local' or 'cloud'.")
    config_path = Path(__file__).resolve().parents[1] / "config" / f"{selected}.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config profile not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Config profile must be a YAML mapping: {config_path}")
    return payload


def resolve_secret(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()
