from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
AIRFLOW_ARTIFACT_ROOT = REPO_ROOT / "airflow" / "artifacts"


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def iter_artifact_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted((entry for entry in root.rglob("*") if entry.is_file()), key=lambda entry: entry.stat().st_mtime, reverse=True)


def infer_artifact_kind(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "failures" in parts:
        return "failure"
    if "metrics" in parts:
        return "metric"
    if "lineage" in parts:
        return "lineage"
    if "orchestration" in parts:
        return "orchestration"
    return "artifact"


def summarize_artifact(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "artifact_reference": repo_relative(path),
        "artifact_kind": infer_artifact_kind(path),
        "size_bytes": stat.st_size,
        "modified_epoch": int(stat.st_mtime),
    }


def locate_latest_artifacts(*, workflow: str | None, limit: int) -> dict[str, Any]:
    roots = [
        AIRFLOW_ARTIFACT_ROOT / "orchestration",
        AIRFLOW_ARTIFACT_ROOT / "observability",
    ]
    artifact_files: list[Path] = []
    for root in roots:
        artifact_files.extend(iter_artifact_files(root))

    if workflow:
        workflow_marker = workflow.lower()
        artifact_files = [path for path in artifact_files if workflow_marker in {part.lower() for part in path.parts}]

    selected = sorted(artifact_files, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
    return {
        "artifact_root": repo_relative(AIRFLOW_ARTIFACT_ROOT),
        "workflow": workflow or "all",
        "limit": limit,
        "artifacts": [summarize_artifact(path) for path in selected],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Locate the latest FraudLens Airflow orchestration artifacts.")
    parser.add_argument("--workflow", help="Optional workflow name to filter artifact paths.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum artifacts to return.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = locate_latest_artifacts(workflow=args.workflow, limit=max(args.limit, 1))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
