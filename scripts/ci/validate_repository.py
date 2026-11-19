"""Offline baseline checks over Git-tracked files; never import project runtime code."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import yaml


REQUIRED_PATHS = (
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "specs/README.md",
    "standards/README.md", ".github/workflows/ci.yml",
)
GENERATED_PREFIXES = (
    ".ci-artifacts/", "airflow/artifacts/", "data/batches/", "dbt/target/",
    "dbt/logs/", "dbt/dbt_packages/", "__pycache__/",
)
SAFE_ENV_EXAMPLES = {".env.example", ".env.sample", ".env.template"}


def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True,
    )
    return sorted(path for path in result.stdout.decode("utf-8").split("\0") if path)


def validate_repository(root: Path, required_paths: Sequence[str] = REQUIRED_PATHS) -> dict[str, Any]:
    root = root.resolve()
    errors: list[dict[str, Any]] = []
    counts = {"tracked": 0, "python": 0, "yaml": 0}
    try:
        paths = tracked_paths(root)
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        return {"valid": False, "counts": counts, "errors": [{"code": "git_file_inventory_failed"}]}
    counts["tracked"] = len(paths)
    for name in required_paths:
        if name not in paths:
            errors.append({"code": "required_file_untracked", "path": name})

    for name in paths:
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            errors.append({"code": "unsafe_file_reference", "path": name})
            continue
        env_file = path.name == ".env" or (path.name.startswith(".env.") and path.name not in SAFE_ENV_EXAMPLES)
        generated = any(name.startswith(prefix) for prefix in GENERATED_PREFIXES)
        generated = generated or "__pycache__" in path.parts or path.suffix == ".pyc"
        private_config = name == "synthetic_generator/runtime_config.yaml"
        if env_file or private_config or (generated and path.name != ".gitkeep"):
            errors.append({"code": "private_or_generated_file_tracked", "path": name})
            continue
        try:
            if path.suffix == ".py":
                counts["python"] += 1
                ast.parse(path.read_bytes(), filename=name)
            elif path.suffix.lower() in {".yaml", ".yml"}:
                counts["yaml"] += 1
                list(yaml.safe_load_all(path.read_text(encoding="utf-8-sig")))
            elif not path.is_file():
                errors.append({"code": "tracked_file_missing", "path": name})
        except SyntaxError as exc:
            errors.append({"code": "python_syntax", "path": name, "line": exc.lineno})
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            errors.append({"code": "yaml_syntax", "path": name, "line": None if mark is None else mark.line + 1})
        except (OSError, UnicodeError):
            errors.append({"code": "file_unreadable", "path": name})
    return {"valid": not errors, "counts": counts, "errors": errors}


def run_context(root: Path) -> dict[str, Any]:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    context: dict[str, Any] = {
        "tested_commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "event_name": os.getenv("GITHUB_EVENT_NAME", "local"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if event_path:
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            pull_request = event.get("pull_request", {})
            context["pull_request_head_sha"] = pull_request.get("head", {}).get("sha")
            context["pull_request_base_sha"] = pull_request.get("base", {}).get("sha")
        except (OSError, ValueError, AttributeError):
            context["event_metadata_unavailable"] = True
    return context


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/repository-checks.json"))
    args = parser.parse_args()
    result = validate_repository(args.root)
    result["context"] = run_context(args.root)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
