"""Create an approved local-Docker handoff without exporting runtime secrets to GitHub."""
from __future__ import annotations

import json
import os
from pathlib import Path

from scripts.deployment.candidate import SHA, sha256
from scripts.deployment.control import prepare
from scripts.deployment.environments import contract


def configuration(context: dict[str, str]) -> dict:
    policy = contract()
    dev = policy["environments"]["dev"]
    expected = {"execution_mode": policy["execution_mode"], "container": dev["container"],
                "root": dev["managed_root"], "runtime_python": dev["runtime_python"], "source_root": dev["source_root"]}
    keys = {"execution_mode": "EXECUTION_MODE", "container": "DOCKER_CONTAINER", "root": "DEPLOY_ROOT",
            "runtime_python": "AIRFLOW_PYTHON", "source_root": "SOURCE_ROOT"}
    if context.get("CLOUD_RESOURCES_ENABLED") != "false" or any(context.get(keys[name]) != value for name, value in expected.items()):
        raise ValueError("Environment variables must match the local-only portfolio contract")
    return expected


def fingerprint(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def create(context: dict[str, str], output: Path) -> dict:
    settings = configuration(context)
    controller_sha = context.get("GITHUB_SHA", "")
    if (not SHA.fullmatch(controller_sha) or not context.get("GITHUB_RUN_ID", "").isdigit()
            or not context.get("GITHUB_RUN_ATTEMPT", "").isdigit()):
        raise ValueError("A complete trusted workflow identity is required")
    verification = prepare(context, output)
    record = {"schema_version": 1, **verification, "execution_mode": "local_docker_operator",
              "configuration": settings, "configuration_sha256": fingerprint(settings),
              "controller_sha": controller_sha, "deployment_run_id": context["GITHUB_RUN_ID"],
              "deployment_run_attempt": context["GITHUB_RUN_ATTEMPT"],
              "state": "approved_handoff_awaiting_local_operator", "deployment_executed": False,
              "github_runtime_secrets_required": False}
    (output / "handoff.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    try:
        result = create(dict(os.environ), Path(".ci-artifacts/deployment"))
    except Exception:
        # Never print private provider/connection exception details into a public run.
        raise SystemExit("Approved handoff creation failed; local runtime was not accessed") from None
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
