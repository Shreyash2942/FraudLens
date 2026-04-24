from __future__ import annotations

from dataclasses import dataclass, replace

from .blueprints import BatchBlueprint
from .contracts import SCALE_PROFILES, ScaleProfile


@dataclass(frozen=True)
class GenerationPlan:
    mode: str
    profile_name: str
    profile: ScaleProfile
    days: int
    seed: int
    blueprint: BatchBlueprint | None
    scenario_counts: dict[str, int]
    lifecycle_counts: dict[str, int]
    decision_mix: dict[str, int]
    disposition_mix: dict[str, int]
    ratio_expectations: dict[str, float]
    calendar_controls: dict[str, object]
    geography_controls: dict[str, object]
    organization_controls: dict[str, object]
    customer_controls: dict[str, object]
    payment_controls: dict[str, object]
    fraud_ops_controls: dict[str, object]
    confirmed_fraud_target: int | None
    false_positive_target: int | None
    timing_style: str
    realism_controls: dict[str, bool]
    dominant_scenario: str | None
    ratio_tolerance: float

    def as_context(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "profile_name": self.profile_name,
            "scenario_counts": dict(self.scenario_counts),
            "lifecycle_counts": dict(self.lifecycle_counts),
            "decision_mix": dict(self.decision_mix),
            "disposition_mix": dict(self.disposition_mix),
            "ratio_expectations": dict(self.ratio_expectations),
            "calendar_controls": dict(self.calendar_controls),
            "geography_controls": dict(self.geography_controls),
            "organization_controls": dict(self.organization_controls),
            "customer_controls": dict(self.customer_controls),
            "payment_controls": dict(self.payment_controls),
            "fraud_ops_controls": dict(self.fraud_ops_controls),
            "confirmed_fraud_target": self.confirmed_fraud_target,
            "false_positive_target": self.false_positive_target,
            "timing_style": self.timing_style,
            "realism_controls": dict(self.realism_controls),
            "dominant_scenario": self.dominant_scenario,
            "ratio_tolerance": self.ratio_tolerance,
            "expected_scenarios": [name for name, count in self.scenario_counts.items() if count > 0],
        }


def build_generation_plan(
    mode: str,
    requested_profile: str | None,
    requested_days: int | None,
    requested_seed: int | None,
    blueprint: BatchBlueprint | None = None,
) -> GenerationPlan:
    if mode == "mixed":
        profile_name = requested_profile or "medium_demo"
        profile = SCALE_PROFILES[profile_name]
        days = requested_days if requested_days is not None else 90
        seed = requested_seed if requested_seed is not None else 42
        return GenerationPlan(
            mode="mixed",
            profile_name=profile_name,
            profile=profile,
            days=days,
            seed=seed,
            blueprint=None,
            scenario_counts=_default_scenario_counts(profile),
            lifecycle_counts={
                "risk_signal_count": profile.risk_signal_count,
                "alert_count": profile.alert_count,
                "case_count": profile.case_count,
                "decision_count": profile.decision_count,
                "disposition_count": profile.disposition_count,
            },
            decision_mix={},
            disposition_mix={},
            ratio_expectations={},
            calendar_controls={},
            geography_controls={},
            organization_controls={},
            customer_controls={},
            payment_controls={},
            fraud_ops_controls={},
            confirmed_fraud_target=None,
            false_positive_target=None,
            timing_style="distributed",
            realism_controls={},
            dominant_scenario=None,
            ratio_tolerance=0.05,
        )

    if blueprint is None:
        raise ValueError("Blueprint mode requires a blueprint")

    profile_name = requested_profile or blueprint.recommended_profile or "medium_demo"
    if profile_name not in SCALE_PROFILES:
        raise ValueError(f"Unknown profile '{profile_name}'")
    base_profile = SCALE_PROFILES[profile_name]
    profile = replace(base_profile, **blueprint.profile_overrides) if blueprint.profile_overrides else base_profile
    days = requested_days if requested_days is not None else (blueprint.default_days or 90)
    seed = requested_seed if requested_seed is not None else (blueprint.default_seed or 42)

    return GenerationPlan(
        mode="blueprint",
        profile_name=profile_name,
        profile=profile,
        days=days,
        seed=seed,
        blueprint=blueprint,
        scenario_counts=dict(blueprint.scenario_counts),
        lifecycle_counts=dict(blueprint.lifecycle_counts),
        decision_mix=dict(blueprint.decision_mix),
        disposition_mix=dict(blueprint.disposition_mix),
        ratio_expectations=dict(blueprint.ratio_expectations),
        calendar_controls=dict(blueprint.calendar_controls),
        geography_controls=dict(blueprint.geography_controls),
        organization_controls=dict(blueprint.organization_controls),
        customer_controls=dict(blueprint.customer_controls),
        payment_controls=dict(blueprint.payment_controls),
        fraud_ops_controls=dict(blueprint.fraud_ops_controls),
        confirmed_fraud_target=blueprint.confirmed_fraud_target,
        false_positive_target=blueprint.false_positive_target,
        timing_style=blueprint.timing_style,
        realism_controls=dict(blueprint.realism_controls),
        dominant_scenario=blueprint.dominant_scenario,
        ratio_tolerance=blueprint.ratio_tolerance,
    )


def _default_scenario_counts(profile: ScaleProfile) -> dict[str, int]:
    return {
        "account_takeover": max(30, profile.risk_signal_count // 8),
        "card_not_present": max(30, profile.risk_signal_count // 6),
        "mule_transfer": max(30, profile.risk_signal_count // 8),
        "burst_velocity": max(30, profile.risk_signal_count // 9),
        "repeat_offender": max(25, profile.risk_signal_count // 11),
        "suspicious_new_device": max(25, profile.risk_signal_count // 10),
        "false_positive": max(25, profile.risk_signal_count // 12),
    }
