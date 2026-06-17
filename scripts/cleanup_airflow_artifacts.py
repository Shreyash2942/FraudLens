from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def artifact_root() -> Path:
    return repo_root() / "airflow" / "artifacts"


def _safe_targets(include_observability: bool) -> list[Path]:
    root = artifact_root()
    targets = [root / "orchestration"]
    if include_observability:
        targets.append(root / "observability")
    return targets


def _validate_target(target: Path) -> Path:
    resolved = target.resolve()
    allowed_root = artifact_root().resolve()
    try:
        resolved.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError(f"Refusing to modify path outside {allowed_root}: {resolved}") from exc
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove generated Airflow artifact folders after switching orchestration evidence to MongoDB."
    )
    parser.add_argument(
        "--include-observability",
        action="store_true",
        help="Also remove generated observability artifact folders under airflow/artifacts/observability.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which folders would be removed without deleting them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = [_validate_target(target) for target in _safe_targets(args.include_observability)]
    existing = [target for target in targets if target.exists()]

    if not existing:
        print("No generated Airflow artifact folders found.")
        return 0

    for target in existing:
        if args.dry_run:
            print(f"Would remove {target}")
            continue
        shutil.rmtree(target)
        print(f"Removed {target}")

    root = artifact_root()
    if not args.dry_run and root.exists() and not any(root.iterdir()):
        root.rmdir()
        print(f"Removed empty root {root}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
