"""Warehouse-free dbt validation with a sanitized, fail-closed stage report."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "dbt/target/manifest.json"
DBT_ARGS = ["--project-dir", "dbt", "--profiles-dir", "dbt/profiles/ci",
            "--profile", "fraudlens_ci", "--target", "validation"]


def execute(arguments: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(arguments, cwd=ROOT, check=True, text=True,
                          capture_output=capture,
                          env=dict(os.environ, DBT_SEND_ANONYMOUS_USAGE_STATS="false"))


def manifest_summary(path: Path = MANIFEST) -> dict:
    raw = path.read_bytes()
    manifest = json.loads(raw)
    models = sum(n.get("resource_type") == "model" for n in manifest["nodes"].values())
    tests = sum(n.get("resource_type") == "test" for n in manifest["nodes"].values())
    if not models or not tests:
        raise ValueError("Manifest must contain models and tests")
    return {"sha256": hashlib.sha256(raw).hexdigest(), "models": models, "tests": tests}


def run_stage(stage: str, report: dict) -> None:
    if stage != "parse":
        raise ValueError("Unknown validation stage")
    # A failed parse must never reuse a previous successful manifest.
    MANIFEST.unlink(missing_ok=True)
    execute(["dbt", "--no-partial-parse", "parse", *DBT_ARGS])
    report["manifest"] = manifest_summary()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["parse"], required=True)
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/dbt-validation.json"))
    args = parser.parse_args()
    report = {"schema_version": 1, "scope": "offline_dbt_validation",
              "warehouse_tests_executed": False, "stages": {},
              "tested_sha": os.environ.get("GITHUB_SHA"),
              "pr_head_sha": os.environ.get("PR_HEAD_SHA"),
              "run_id": os.environ.get("GITHUB_RUN_ID"),
              "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
              "dependencies": {name: importlib.metadata.version(name)
                               for name in ("dbt-core", "dbt-hive")}}
    code = 0
    try:
        run_stage(args.stage, report)
        report["stages"][args.stage] = {"status": "success"}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        code = 1
        # Keep raw command output and source SQL out of the uploaded JSON.
        report["stages"][args.stage] = {"status": "failure", "error_type": type(error).__name__}
        print(f"dbt {args.stage} failed ({type(error).__name__})", flush=True)
    report["updated_at"] = datetime.now(timezone.utc).isoformat()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
