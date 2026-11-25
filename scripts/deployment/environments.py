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
        try:
            existing = github(f"repos/{REPOSITORY}/environments/{name}")
        except subprocess.CalledProcessError as error:
            if b"404" not in (error.stderr or b""):
                raise
        else:
            payload["deployment_branch_policy"] = existing["deployment_branch_policy"]
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
    if github(f"repos/{REPOSITORY}")["visibility"] != "public":
        raise ValueError("Private-repository activation is outside the no-spend portfolio policy")
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


def main_check_ready() -> dict:
    sha = github(f"repos/{REPOSITORY}/branches/main")["commit"]["sha"]
    runs = github(f"repos/{REPOSITORY}/actions/runs?branch=main&event=push&status=success&head_sha={sha}&per_page=100")["workflow_runs"]
    runs = [run for run in runs if run["head_sha"] == sha and run["path"] == ".github/workflows/ci.yml"]
    if not runs:
        raise ValueError("Required status activation waits for successful CI on the actual main commit")
    run = runs[0]
    jobs = github(f"repos/{REPOSITORY}/actions/runs/{run['id']}/jobs?per_page=100")["jobs"]
    for name in ("Baseline Repository Checks", "dbt Validation", "Python Validation", "CI Summary", "Deployment Validation / Candidate Bundle"):
        if not any(job["name"] == name and job["conclusion"] == "success" for job in jobs):
            raise ValueError("Actual main validation gates are incomplete")
    checks = github(f"repos/{REPOSITORY}/commits/{sha}/check-runs?per_page=100")["check_runs"]
    summary = next((row for row in checks if row["name"] == "CI Summary" and row["conclusion"] == "success"
                    and row["app"]["slug"] == "github-actions"), None)
    if not summary:
        raise ValueError("Main CI Summary check identity could not be verified")
    return {"strict": True, "checks": [{"context": "CI Summary", "app_id": summary["app"]["id"]}]}


def configure_protections(apply: bool, seal_main: bool = False) -> dict:
    desired = contract()
    owner = github("users/" + desired["owner"])
    for name, settings in desired["environments"].items():
        if apply:
            github(f"repos/{REPOSITORY}/environments/{name}", "PUT", {
                "wait_timer": 0, "prevent_self_review": settings["prevent_self_review"],
                "reviewers": [{"type": "User", "id": owner["id"]}], "can_admins_bypass": False,
                "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}})
        prefix = f"repos/{REPOSITORY}/environments/{name}/deployment-branch-policies"
        current = github(f"repos/{REPOSITORY}/environments/{name}")
        policies = (github(prefix + "?per_page=100")["branch_policies"]
                    if current.get("deployment_branch_policy", {}).get("custom_branch_policies") else [])
        if any(row["name"] != settings["allowed_branch"] or row.get("type", "branch") != "branch" for row in policies):
            raise ValueError("Conflicting environment branch restrictions require owner review")
        if apply and not policies:
            github(prefix, "POST", {"name": settings["allowed_branch"], "type": "branch"})
    try:
        old = github(f"repos/{REPOSITORY}/branches/main/protection")
    except subprocess.CalledProcessError as error:
        if b"404" not in (error.stderr or b""):
            raise
        old = {}
    checks = main_check_ready() if seal_main else old.get("required_status_checks")
    if checks:
        checks = {"strict": checks["strict"], "checks": checks["checks"]}
    payload = {"required_status_checks": checks, "enforce_admins": True,
               "required_pull_request_reviews": {"dismiss_stale_reviews": True, "require_code_owner_reviews": False,
                   "required_approving_review_count": 0, "require_last_push_approval": False},
               "restrictions": None, "required_linear_history": False, "allow_force_pushes": False,
               "allow_deletions": False, "required_conversation_resolution": True}
    if apply:
        github(f"repos/{REPOSITORY}/branches/main/protection", "PUT", payload)
        github(f"repos/{REPOSITORY}/actions/permissions/workflow", "PUT", {
            "default_workflow_permissions": "read", "can_approve_pull_request_reviews": False})
        github(f"repos/{REPOSITORY}/actions/permissions/fork-pr-contributor-approval", "PUT", {
            "approval_policy": "all_external_contributors"})
    return {"applied": apply, "main_protection": payload,
            "required_ci_summary": "enforced" if checks else "pending_first_successful_main_ci",
            "sole_maintainer_review": "owner_acceptance_at_merge; not independent approval",
            "environment_branch_rules": {name: settings["allowed_branch"] for name, settings in desired["environments"].items()},
            "external_contributor_workflow_approval": "all_external_contributors", "default_token": "read"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the reviewed environment definitions")
    parser.add_argument("--section", choices=["definitions", "variables", "protections"], default="definitions")
    parser.add_argument("--seal-main", action="store_true", help="Require CI Summary only after verifying successful CI on actual main")
    parser.add_argument("--enable-dev-handoff", action="store_true", help="Enable approval handoffs; never start Docker or a pipeline")
    parser.add_argument("--report", type=Path, default=Path(".ci-artifacts/environment-definitions.json"))
    args = parser.parse_args()
    try:
        if args.section == "definitions":
            result = configure_definitions(args.apply)
        elif args.section == "variables":
            result = configure_variables(args.apply, args.enable_dev_handoff)
        else:
            result = configure_protections(args.apply, args.seal_main)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError):
        raise SystemExit("Environment configuration failed; no cloud resources were requested") from None
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
