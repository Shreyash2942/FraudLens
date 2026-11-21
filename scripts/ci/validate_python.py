"""Validate tracked Python and offline tests without private local configuration."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

from scripts.ci.validate_repository import run_context, tracked_paths, validate_repository


ROOT = Path(__file__).resolve().parents[2]


def lint(root: Path, report: dict) -> bool:
    paths = [name for name in tracked_paths(root) if name.endswith(".py")]
    if not paths:
        raise ValueError("No tracked Python files found")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", str(root / "ruff.toml"),
         "--no-cache", "--no-fix", "--output-format", "json", "--", *paths],
        cwd=root, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode not in (0, 1):
        raise ValueError("Ruff could not complete")
    diagnostics = json.loads(result.stdout)
    if not isinstance(diagnostics, list):
        raise ValueError("Invalid Ruff result")
    report["python_files"] = len(paths)
    report["lint_errors"] = [
        {"path": Path(item["filename"]).resolve().relative_to(root.resolve()).as_posix(),
         "rule": item["code"], "line": item["location"]["row"],
         "column": item["location"]["column"]}
        for item in diagnostics
    ]
    return result.returncode == 0 and not diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["lint"], required=True)
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/python-validation.json"))
    args = parser.parse_args()
    report = {"schema_version": 1, "scope": "offline_python_validation", "stages": {},
              "context": run_context(ROOT),
              "dependencies": {name: importlib.metadata.version(name)
                               for name in ("pytest", "ruff", "Faker", "minio", "PyYAML")}}
    passed = False
    try:
        if not validate_repository(ROOT)["valid"]:
            raise ValueError("Tracked-file baseline must pass before running Python checks")
        passed = lint(ROOT, report)
        report["stages"][args.stage] = {"status": "success" if passed else "failure"}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        report["stages"][args.stage] = {"status": "failure", "error_type": type(error).__name__}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
