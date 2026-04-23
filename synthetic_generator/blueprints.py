from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


VALID_SCENARIOS = {
    "account_takeover",
    "card_not_present",
    "mule_transfer",
    "burst_velocity",
    "repeat_offender",
    "suspicious_new_device",
    "false_positive",
}

LIFECYCLE_KEYS = {
    "risk_signal_count",
    "alert_count",
    "case_count",
    "decision_count",
    "disposition_count",
}

REALISM_KEYS = {
    "emphasize_new_device_behavior",
    "emphasize_shared_device_clustering",
    "emphasize_new_payees",
    "emphasize_off_hours",
    "emphasize_reversals",
    "emphasize_recoveries",
}


@dataclass(frozen=True)
class BatchBlueprint:
    name: str
    description: str
    recommended_profile: str
    source: str
    default_days: int | None = None
    default_seed: int | None = None
    batch_style: str = "multi_scenario"
    scenario_families: list[str] = field(default_factory=list)
    profile_overrides: dict[str, int] = field(default_factory=dict)
    scenario_counts: dict[str, int] = field(default_factory=dict)
    confirmed_fraud_target: int | None = None
    false_positive_target: int | None = None
    timing_style: str = "distributed"
    lifecycle_counts: dict[str, int] = field(default_factory=dict)
    decision_mix: dict[str, int] = field(default_factory=dict)
    disposition_mix: dict[str, int] = field(default_factory=dict)
    ratio_expectations: dict[str, float] = field(default_factory=dict)
    calendar_controls: dict[str, object] = field(default_factory=dict)
    geography_controls: dict[str, object] = field(default_factory=dict)
    organization_controls: dict[str, object] = field(default_factory=dict)
    customer_controls: dict[str, object] = field(default_factory=dict)
    payment_controls: dict[str, object] = field(default_factory=dict)
    fraud_ops_controls: dict[str, object] = field(default_factory=dict)
    realism_controls: dict[str, bool] = field(default_factory=dict)
    dominant_scenario: str | None = None
    ratio_tolerance: float = 0.05


def list_builtin_blueprints() -> list[str]:
    return sorted(path.stem for path in _builtin_dir().glob("*.yaml"))


def load_blueprint(reference: str) -> BatchBlueprint:
    path = Path(reference)
    if path.exists():
        blueprint_path = path
    else:
        blueprint_path = _builtin_dir() / f"{reference}.yaml"
    if not blueprint_path.exists():
        raise ValueError(f"Blueprint not found: {reference}")
    payload = _read_yaml(blueprint_path)
    return _parse_blueprint(payload, source=str(blueprint_path.resolve()))


def _builtin_dir() -> Path:
    return Path(__file__).parent / "blueprints"


def _read_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("PyYAML is required for blueprint mode. Install requirements-phase2.txt.") from exc
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Blueprint file must contain a YAML mapping: {path}")
    return payload


def _parse_blueprint(payload: dict, source: str) -> BatchBlueprint:
    metadata = _require_mapping(payload, "metadata")
    generation = _require_mapping(payload, "generation")
    scenario_controls = _require_mapping(payload, "scenario_controls")
    lifecycle_controls = _require_mapping(payload, "lifecycle_controls")
    outcome_controls = _optional_mapping(payload, "outcome_controls")
    calendar_controls = _optional_mapping(payload, "calendar_controls")
    geography_controls = _optional_mapping(payload, "geography_controls")
    organization_controls = _optional_mapping(payload, "organization_controls")
    customer_controls = _optional_mapping(payload, "customer_controls")
    payment_controls = _optional_mapping(payload, "payment_controls")
    fraud_ops_controls = _optional_mapping(payload, "fraud_ops_controls")
    realism_controls = _optional_mapping(payload, "realism_controls")
    validation = _optional_mapping(payload, "validation")

    name = _require_string(metadata, "name")
    description = _require_string(metadata, "description")
    recommended_profile = _require_string(generation, "recommended_profile")
    batch_style = str(generation.get("batch_style", "multi_scenario"))
    if batch_style not in {"single_scenario", "multi_scenario"}:
        raise ValueError(f"Unsupported batch_style '{batch_style}' in {source}")

    scenario_families = _string_list(generation.get("scenario_families", []))
    profile_overrides = _int_mapping(generation.get("profile_overrides", {}), "generation.profile_overrides")
    scenario_counts = _int_mapping(scenario_controls.get("scenario_counts", {}), "scenario_controls.scenario_counts")
    if not scenario_counts:
        raise ValueError(f"Blueprint '{name}' must define at least one scenario count")
    invalid_scenarios = sorted(set(scenario_counts) - VALID_SCENARIOS)
    if invalid_scenarios:
        raise ValueError(f"Blueprint '{name}' uses unsupported scenarios: {', '.join(invalid_scenarios)}")
    if scenario_families:
        invalid_families = sorted(set(scenario_families) - VALID_SCENARIOS)
        if invalid_families:
            raise ValueError(f"Blueprint '{name}' has invalid scenario_families: {', '.join(invalid_families)}")

    lifecycle_counts = _int_mapping(lifecycle_controls, "lifecycle_controls")
    missing_lifecycle = sorted(LIFECYCLE_KEYS - set(lifecycle_counts))
    if missing_lifecycle:
        raise ValueError(f"Blueprint '{name}' is missing lifecycle counts: {', '.join(missing_lifecycle)}")

    decision_mix = _int_mapping(outcome_controls.get("decision_mix", {}), "outcome_controls.decision_mix")
    disposition_mix = _int_mapping(outcome_controls.get("disposition_mix", {}), "outcome_controls.disposition_mix")
    ratio_expectations = _float_mapping(outcome_controls.get("ratio_expectations", {}), "outcome_controls.ratio_expectations")
    if decision_mix and sum(decision_mix.values()) != lifecycle_counts["decision_count"]:
        raise ValueError(f"Blueprint '{name}' decision_mix must sum to decision_count")
    if disposition_mix and sum(disposition_mix.values()) != lifecycle_counts["disposition_count"]:
        raise ValueError(f"Blueprint '{name}' disposition_mix must sum to disposition_count")

    realism = _bool_mapping(realism_controls, "realism_controls")
    invalid_realism = sorted(set(realism) - REALISM_KEYS)
    if invalid_realism:
        raise ValueError(f"Blueprint '{name}' uses unsupported realism controls: {', '.join(invalid_realism)}")

    dominant_scenario = validation.get("dominant_scenario")
    if dominant_scenario is not None and dominant_scenario not in VALID_SCENARIOS:
        raise ValueError(f"Blueprint '{name}' has invalid dominant_scenario '{dominant_scenario}'")
    ratio_tolerance = float(validation.get("ratio_tolerance", 0.05))

    return BatchBlueprint(
        name=name,
        description=description,
        recommended_profile=recommended_profile,
        source=source,
        default_days=_optional_int(generation.get("default_days")),
        default_seed=_optional_int(generation.get("default_seed")),
        batch_style=batch_style,
        scenario_families=scenario_families,
        profile_overrides=profile_overrides,
        scenario_counts=scenario_counts,
        confirmed_fraud_target=_optional_int(scenario_controls.get("confirmed_fraud_target")),
        false_positive_target=_optional_int(scenario_controls.get("false_positive_target")),
        timing_style=str(scenario_controls.get("timing_style", "distributed")),
        lifecycle_counts=lifecycle_counts,
        decision_mix=decision_mix,
        disposition_mix=disposition_mix,
        ratio_expectations=ratio_expectations,
        calendar_controls=calendar_controls,
        geography_controls=geography_controls,
        organization_controls=organization_controls,
        customer_controls=customer_controls,
        payment_controls=payment_controls,
        fraud_ops_controls=fraud_ops_controls,
        realism_controls=realism,
        dominant_scenario=dominant_scenario,
        ratio_tolerance=ratio_tolerance,
    )


def _require_mapping(payload: dict, key: str) -> dict:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Blueprint is missing required mapping '{key}'")
    return value


def _optional_mapping(payload: dict, key: str) -> dict:
    value = payload.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Blueprint section '{key}' must be a mapping")
    return value


def _require_string(payload: dict, key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Blueprint field '{key}' must be a non-empty string")
    return value.strip()


def _string_list(value) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("Blueprint string-list field must be a list of strings")
    return [item.strip() for item in value]


def _int_mapping(value, label: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    parsed: dict[str, int] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{label} keys must be strings")
        parsed[key] = _require_non_negative_int(item, f"{label}.{key}")
    return parsed


def _float_mapping(value, label: str) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    parsed: dict[str, float] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{label} keys must be strings")
        try:
            parsed[key] = float(item)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label}.{key} must be numeric") from exc
    return parsed


def _bool_mapping(value, label: str) -> dict[str, bool]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    parsed: dict[str, bool] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, bool):
            raise ValueError(f"{label} must contain string keys and boolean values")
        parsed[key] = item
    return parsed


def _require_non_negative_int(value, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer, not bool")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be an integer") from exc
    if number < 0:
        raise ValueError(f"{label} must be non-negative")
    return number


def _optional_int(value) -> int | None:
    if value is None:
        return None
    return _require_non_negative_int(value, "optional_int")
