"""Warehouse-free dbt validation with a sanitized, fail-closed stage report."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
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
    if stage == "parse":
        # A failed parse must never reuse a previous successful manifest.
        MANIFEST.unlink(missing_ok=True)
        execute(["dbt", "--no-partial-parse", "parse", *DBT_ARGS])
        report["manifest"] = manifest_summary()
        return
    if stage != "validate":
        raise ValueError("Unknown validation stage")
    if report.get("stages", {}).get("parse", {}).get("status") != "success":
        raise ValueError("A successful parse is required before validation")
    if report.get("manifest") != manifest_summary():
        raise ValueError("Manifest changed after parsing")
    checks = report["checks"] = {}
    for selector in ("failure_blocking_gate", "failure_diagnostic_gate"):
        checks[selector] = {"status": "failure"}
        result = execute(["dbt", "--quiet", "ls", *DBT_ARGS, "--resource-type", "test",
                          "--selector", selector, "--output", "json"], capture=True)
        count = selected_test_count(result.stdout)
        checks[selector] = {"status": "success", "selected_tests": count}
    for validator in ("naming_rules", "governance_metadata", "contracts",
                      "contract_alignment", "failure_policy"):
        checks[validator] = {"status": "failure"}
        command = [sys.executable, f"dbt/scripts/validate_{validator}.py", "--manifest", str(MANIFEST)]
        if validator == "failure_policy":
            command += ["--selectors", "dbt/selectors.yml", "--policy",
                        "dbt/tests/validation/failure_policy_matrix.json"]
        execute(command)
        checks[validator] = {"status": "success"}
    checks["docs"] = {"status": "failure"}
    execute(["dbt", "docs", "generate", "--empty-catalog", "--no-compile", *DBT_ARGS])
    checks["docs"] = {"status": "success"}


def selected_test_count(output: str) -> int:
    """Count dbt JSON test records, never log lines or a selector warning."""
    records = [json.loads(line) for line in output.splitlines() if line.strip()]
    if not records or any(not isinstance(item, dict) or item.get("resource_type") != "test"
                          or not str(item.get("unique_id", "")).startswith("test.") for item in records):
        raise ValueError("Selector must resolve to actual test records")
    return len({item["unique_id"] for item in records})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["parse", "validate"], required=True)
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
        if args.stage == "validate":
            report = json.loads(args.report.read_text(encoding="utf-8"))
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
