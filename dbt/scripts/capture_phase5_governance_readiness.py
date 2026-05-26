#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _run(command: list[str], cwd: Path) -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    process = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout_lines = [line for line in process.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in process.stderr.splitlines() if line.strip()]
    return {
        "command": " ".join(command),
        "started_at_utc": started_at,
        "exit_code": process.returncode,
        "result": "passed" if process.returncode == 0 else "failed",
        "stdout_line_count": len(stdout_lines),
        "stderr_tail": stderr_lines[-10:],
        "stdout_tail": stdout_lines[-10:],
    }


def _dbt_command(subcommand: str, dbt_options: list[str], extra_args: list[str] | None = None) -> list[str]:
    command = ["dbt", subcommand] + dbt_options
    if extra_args:
        command.extend(extra_args)
    return command


def _selector_count(selector: str, dbt_options: list[str], cwd: Path) -> dict:
    command = _dbt_command("ls", dbt_options, ["--resource-type", "test", "--selector", selector])
    result = _run(command, cwd)
    if result["result"] == "passed":
        result["test_count"] = result["stdout_line_count"]
    else:
        result["test_count"] = 0
    result["selector"] = selector
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture Phase 5 governance readiness command artifacts."
    )
    parser.add_argument(
        "--output",
        default="documents/validation/data-quality-governance-readiness-artifacts.json",
        help="Output JSON artifact path",
    )
    parser.add_argument(
        "--project-dir",
        default="dbt",
    )
    parser.add_argument(
        "--profiles-dir",
        default="dbt/profiles",
    )
    parser.add_argument(
        "--profile",
        default=os.getenv("FRAUDLENS_DBT_PROFILE_NAME", "fraudlens_local_spark"),
    )
    parser.add_argument(
        "--target",
        default=os.getenv("FRAUDLENS_DBT_TARGET_NAME", "local"),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dbt_options = [
        "--project-dir",
        args.project_dir,
        "--profiles-dir",
        args.profiles_dir,
        "--profile",
        args.profile,
        "--target",
        args.target,
    ]

    commands = []
    commands.append(_run(_dbt_command("parse", dbt_options), repo_root))
    commands.append(_run(["bash", "dbt/scripts/validate_structure.sh"], repo_root))

    selectors = [
        "quality_critical_gate",
        "quality_high_gate",
        "governance_critical_gate",
        "contract_critical_gate",
        "audit_traceability_gate",
        "phase5_readiness_bundle",
    ]
    selector_results = [_selector_count(selector, dbt_options, repo_root) for selector in selectors]

    commands.extend(selector_results)

    all_passed = all(entry["result"] == "passed" for entry in commands)
    artifact = {
        "issue": 63,
        "phase": 5,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "target": args.target,
        "commands": commands,
        "selectors": {
            entry["selector"]: entry.get("test_count", 0)
            for entry in selector_results
        },
        "summary": {
            "result": "READY" if all_passed else "CONDITIONAL READY",
            "command_count": len(commands),
            "passed_count": sum(1 for entry in commands if entry["result"] == "passed"),
            "failed_count": sum(1 for entry in commands if entry["result"] == "failed"),
        },
    }

    output_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"[readiness] wrote artifact: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
