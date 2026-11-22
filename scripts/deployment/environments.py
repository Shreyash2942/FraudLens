"""Plan/apply free public-repository portfolio controls; never provision cloud resources."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.deployment.candidate import REPOSITORY, ROOT


CONTRACT = ROOT / ".github/portfolio-environments.json"


def github(endpoint: str, method: str = "GET", body: dict | None = None) -> dict:
    command = ["gh", "api", "--hostname", "github.com", "--method", method, endpoint]
    if body is not None:
        command += ["--input", "-"]
    result = subprocess.run(command, input=None if body is None else json.dumps(body).encode(),
                            capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def contract() -> dict:
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (value["repository"] != REPOSITORY or value["cost_policy"] != "local_only_no_new_paid_resources"
            or value["cloud_resources_enabled"] is not False or value["execution_mode"] != "local_docker_operator"
            or set(value["environments"]) != {"dev", "test", "prod"}
            or any(value["environments"][name]["enabled"] for name in ("test", "prod"))):
        raise ValueError("Portfolio cost/environment policy mismatch")
    return value


def configure_definitions(apply: bool) -> dict:
    desired = contract()
    repository = github(f"repos/{REPOSITORY}")
    if repository["visibility"] != "public" or not repository["permissions"].get("admin"):
        raise ValueError("Public portfolio repository with owner administration is required")
    owner = github("users/" + desired["owner"])
    plan = {"cost_policy": desired["cost_policy"], "execution_mode": desired["execution_mode"],
            "physical_runtime_count": 1, "cloud_resources_created": 0, "environments": {}}
    for name, settings in desired["environments"].items():
        # Initially protected-branch-only. Main-only custom restrictions are applied in the protection step.
        payload = {"wait_timer": 0, "prevent_self_review": settings["prevent_self_review"],
                   "reviewers": [{"type": "User", "id": owner["id"]}], "can_admins_bypass": False,
                   "deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}}
        plan["environments"][name] = {"enabled": settings["enabled"], "runtime": settings["runtime"],
                                      "owner_reviewer": desired["owner"], "prevent_self_review": settings["prevent_self_review"]}
        if apply:
            result = github(f"repos/{REPOSITORY}/environments/{name}", "PUT", payload)
            if result["name"] != name:
                raise ValueError("Environment configuration was not acknowledged")
    plan["applied"] = apply
    return plan


def desired_variables(enabled: bool = False) -> dict[str, dict[str, str]]:
    desired = contract()
    dev = desired["environments"]["dev"]
    result = {"repository": {"FRAUDLENS_COST_PROFILE": desired["cost_policy"],
                              "FRAUDLENS_DEV_DEPLOY_ENABLED": str(enabled).lower()}}
    for name, settings in desired["environments"].items():
        values = {"FRAUDLENS_ENVIRONMENT": name, "FRAUDLENS_CLOUD_RESOURCES_ENABLED": "false",
                  "FRAUDLENS_EXECUTION_MODE": desired["execution_mode"] if settings["enabled"] else "disabled"}
        if name == "dev":
            values.update(FRAUDLENS_DOCKER_CONTAINER=dev["container"], FRAUDLENS_DEPLOY_ROOT=dev["managed_root"],
                          FRAUDLENS_RUNTIME_PYTHON=dev["runtime_python"], FRAUDLENS_SOURCE_ROOT=dev["source_root"])
        else:
            values["FRAUDLENS_DEPLOY_ENABLED"] = "false"
        result[name] = values
    return result


def configure_variables(apply: bool, enabled: bool = False) -> dict:
    values = desired_variables(enabled)
    for scope, variables in values.items():
        prefix = f"repos/{REPOSITORY}/actions" if scope == "repository" else f"repos/{REPOSITORY}/environments/{scope}"
        existing = {row["name"] for row in github(prefix + "/variables?per_page=100")["variables"]}
        if apply:
            for name, value in variables.items():
                github(prefix + "/variables" + ("/" + name if name in existing else ""),
                       "PATCH" if name in existing else "POST", {"name": name, "value": value})
    return {"applied": apply, "variables": values, "github_runtime_secrets_required": [],
            "secret_storage": "private_existing_local_docker_volume"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the reviewed environment definitions")
    parser.add_argument("--section", choices=["definitions", "variables"], default="definitions")
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/environment-definitions.json"))
    args = parser.parse_args()
    try:
        result = configure_definitions(args.apply) if args.section == "definitions" else configure_variables(args.apply)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError):
        raise SystemExit("Environment configuration failed; no cloud resources were requested") from None
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
