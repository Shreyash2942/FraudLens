from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = REPO_ROOT / "monitoring" / "coverage" / "observability-lineage-coverage.json"
REQUIRED_SERVICES = {"airflow", "prometheus", "grafana", "openlineage", "marquez"}
REQUIRED_LAYERS = {"ingestion", "transformation", "serving"}
VALID_STATUSES = {"covered", "partial", "planned", "blocked"}


def load_matrix(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Coverage matrix must be a JSON object: {path}")
    return payload


def missing_evidence_paths(matrix: dict[str, Any], *, repo_root: Path) -> list[str]:
    missing: list[str] = []
    sections = [
        item for item in matrix.get("critical_services", []) if isinstance(item, dict)
    ] + [
        item for item in matrix.get("pipeline_layers", []) if isinstance(item, dict)
    ]
    for item in sections:
        for evidence in item.get("evidence", []):
            evidence_path = repo_root / str(evidence)
            if not evidence_path.exists():
                missing.append(str(evidence))
    return sorted(set(missing))


def validate_matrix(matrix: dict[str, Any], *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    services = {
        str(item.get("service"))
        for item in matrix.get("critical_services", [])
        if isinstance(item, dict)
    }
    layers = {
        str(item.get("layer"))
        for item in matrix.get("pipeline_layers", [])
        if isinstance(item, dict)
    }
    statuses = [
        str(item.get("status"))
        for section_name in ("critical_services", "pipeline_layers", "production_like_readiness")
        for item in matrix.get(section_name, [])
        if isinstance(item, dict)
    ]
    missing_services = sorted(REQUIRED_SERVICES - services)
    missing_layers = sorted(REQUIRED_LAYERS - layers)
    invalid_statuses = sorted({status for status in statuses if status not in VALID_STATUSES})
    missing_evidence = missing_evidence_paths(matrix, repo_root=repo_root)
    return {
        "valid": not (missing_services or missing_layers or invalid_statuses or missing_evidence),
        "missing_services": missing_services,
        "missing_layers": missing_layers,
        "invalid_statuses": invalid_statuses,
        "missing_evidence": missing_evidence,
        "service_count": len(services),
        "layer_count": len(layers),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FraudLens observability and lineage coverage matrix.")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matrix = load_matrix(args.matrix)
    result = validate_matrix(matrix)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
