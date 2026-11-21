"""Offline checks for governed entity metadata and tracked Markdown destinations."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt

from scripts.ci.validate_repository import run_context, tracked_paths, validate_repository


ROOT = Path(__file__).resolve().parents[2]
SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
CONTRACT_PATH = re.compile(r"^specs/([a-z][a-z0-9_]*)/(v[1-9][0-9]*)/([a-z][a-z0-9_]*)\.yaml$")
AUDIT_FIELDS = {"record_source", "source_record_id", "ingested_at", "effective_at", "created_at",
                "updated_at", "created_by", "updated_by", "change_reason_code", "lineage_run_id"}
CRITICAL = {"accounts.deposit_account", "payments.payment_instruction", "payments.payment_transaction",
            "alerts.fraud_alert", "cases.fraud_case", "decisions.decision_record", "dispositions.case_disposition"}
# Existing natural-key contracts; business entity identifiers otherwise end in _id.
NATURAL_KEYS = {"calendar.calendar_day": "calendar_date", "reference.reference_data_catalog": "code_set_name"}
REQUIRED_STANDARDS = ("standards/naming-conventions.md", "standards/modeling-standard.md",
                      "standards/governance-controls.md", "standards/auditability-standard.md",
                      "specs/semantic-conventions.yaml")


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_contract(name: str, payload: object, audit: set[str]) -> list[dict]:
    errors = []

    def require(condition: bool, code: str, field: str) -> None:
        if not condition:
            errors.append({"code": code, "path": name, "field": field})

    match = CONTRACT_PATH.fullmatch(name)
    if not match or not isinstance(payload, dict):
        return [{"code": "contract_shape", "path": name}]
    domain, version, entity = match.groups()
    identity = domain + "." + entity
    for key, expected in (("domain", domain), ("version", version), ("entity_name", entity)):
        require(payload.get(key) == expected, "contract_identity", key)
    require(payload.get("classification") in ("critical", "governed"), "contract_classification", "classification")
    if identity in CRITICAL:
        require(payload.get("classification") == "critical", "critical_classification", "classification")
    require(nonempty(payload.get("description")), "contract_description", "description")
    ownership = payload.get("ownership")
    ownership = ownership if isinstance(ownership, dict) else {}
    for key in ("business_owner", "technical_steward", "approval_model"):
        require(nonempty(ownership.get(key)), "contract_ownership", "ownership." + key)

    fields = payload.get("fields")
    if not isinstance(fields, list) or not fields:
        require(False, "contract_fields", "fields")
        return errors
    names = []
    for index, field in enumerate(fields):
        pointer = f"fields[{index}]"
        if not isinstance(field, dict):
            require(False, "field_metadata", pointer)
            continue
        field_name = field.get("name")
        require(isinstance(field_name, str) and bool(SNAKE.fullmatch(field_name)), "field_naming", pointer + ".name")
        if isinstance(field_name, str):
            names.append(field_name)
        require(field.get("type") in ("string", "integer", "decimal", "date", "timestamp", "boolean"), "field_type", pointer + ".type")
        require(isinstance(field.get("required"), bool), "field_nullability", pointer + ".required")
        require(nonempty(field.get("description")), "field_description", pointer + ".description")
        if isinstance(field_name, str) and field_name.endswith("_status"):
            values = field.get("allowed_values")
            require(isinstance(values, list) and bool(values), "status_values", pointer + ".allowed_values")
    require(len(names) == len(set(names)), "duplicate_field", "fields")
    keys = payload.get("keys")
    key = keys.get("primary_key") if isinstance(keys, dict) else None
    require(key in names, "primary_key_missing", "keys.primary_key")
    require(isinstance(key, str) and (key.endswith("_id") or NATURAL_KEYS.get(identity) == key), "primary_key_naming", "keys.primary_key")
    require(any(isinstance(field, dict) and field.get("name") == key and field.get("required") is True for field in fields), "primary_key_required", "keys.primary_key")
    controls = payload.get("controls")
    controls = controls if isinstance(controls, dict) else {}
    for flag in ("financial_reporting_relevant", "fraud_decision_relevant"):
        require(isinstance(controls.get(flag), bool), "control_classification", "controls." + flag)
    require(controls.get("required_audit_fields_inherited") is True or audit.issubset(names),
            "audit_fields_missing", "controls.required_audit_fields_inherited")
    return errors


def validate_links(root: Path, name: str, tracked: set[str]) -> tuple[list[dict], int]:
    errors, count = [], 0
    parser = MarkdownIt("commonmark").enable("table")
    for block in parser.parse((root / name).read_text(encoding="utf-8-sig")):
        for token in block.children or []:
            url = token.attrGet("href") if token.type == "link_open" else token.attrGet("src") if token.type == "image" else None
            if not url:
                continue
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            count += 1
            path = unquote(parts.path)
            candidate = root / path.lstrip("/") if path.startswith("/") else root / Path(name).parent / path
            try:
                relative = candidate.resolve().relative_to(root.resolve()).as_posix()
                valid = relative == "." or relative in tracked or any(p.startswith(relative.rstrip("/") + "/") for p in tracked)
            except (ValueError, OSError):
                valid = False
            if not valid:
                errors.append({"code": "markdown_destination_missing_or_untracked", "path": name,
                               "line": block.map[0] + 1 if block.map else None})
    return errors, count


def validate_standards(root: Path) -> dict:
    counts = {"contracts": 0, "markdown_files": 0, "local_links": 0}
    errors = []
    if not validate_repository(root)["valid"]:
        return {"valid": False, "counts": counts, "errors": [{"code": "baseline_required"}]}
    paths = tracked_paths(root)
    tracked = set(paths)
    for name in REQUIRED_STANDARDS:
        if name not in tracked:
            errors.append({"code": "required_standard_untracked", "path": name})
    conventions = yaml.safe_load((root / "specs/semantic-conventions.yaml").read_text(encoding="utf-8"))
    audit = conventions.get("required_audit_fields") if isinstance(conventions, dict) else None
    if not isinstance(audit, list) or not AUDIT_FIELDS.issubset(audit):
        errors.append({"code": "shared_audit_fields_missing", "path": "specs/semantic-conventions.yaml"})
    audit_fields = set(audit) if isinstance(audit, list) and all(isinstance(item, str) for item in audit) else AUDIT_FIELDS
    for identity in sorted(CRITICAL):
        domain, entity = identity.split(".")
        if not any(CONTRACT_PATH.fullmatch(name) and name.startswith(f"specs/{domain}/") and Path(name).stem == entity for name in paths):
            errors.append({"code": "critical_contract_missing", "entity": identity})
    for name in paths:
        path = root / name
        if name.startswith("specs/") and path.suffix in (".yaml", ".yml") and len(path.relative_to(root).parts) == 4:
            counts["contracts"] += 1
            errors.extend(validate_contract(name, yaml.safe_load(path.read_text(encoding="utf-8")), audit_fields))
        if path.suffix.lower() == ".md":
            counts["markdown_files"] += 1
            failures, count = validate_links(root, name, tracked)
            errors.extend(failures)
            counts["local_links"] += count
    if not counts["contracts"] or not counts["markdown_files"]:
        errors.append({"code": "standards_inventory_empty"})
    return {"valid": not errors, "counts": counts, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/repository-standards.json"))
    args = parser.parse_args()
    try:
        result = validate_standards(ROOT)
    except (OSError, ValueError, TypeError, yaml.YAMLError) as error:
        result = {"valid": False, "errors": [{"code": "standards_validation_failed", "error_type": type(error).__name__}]}
    result["context"] = run_context(ROOT)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
