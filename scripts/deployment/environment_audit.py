"""Offline portfolio cost and workflow-boundary checks; no GitHub writes or Docker calls."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from scripts.deployment.candidate import ROOT
from scripts.deployment.environments import contract


def audit(root: Path = ROOT) -> dict:
    policy = contract()
    errors = []
    workflows = sorted((root / ".github/workflows").glob("*.yml"))
    for path in workflows:
        source = path.read_text(encoding="utf-8")
        workflow = yaml.safe_load(source)
        if "pull_request_target" in workflow.get("on", {}):
            errors.append({"path": path.name, "code": "privileged_pr_event"})
        if "secrets." in source:
            errors.append({"path": path.name, "code": "github_runtime_secret_reference"})
        for name, job in workflow["jobs"].items():
            if "github.event.repository.private == false" not in job.get("if", ""):
                errors.append({"path": path.name, "job": name, "code": "public_repository_guard_missing"})
            permissions = job.get("permissions", workflow.get("permissions", {}))
            if any(value != "read" for value in permissions.values()):
                errors.append({"path": path.name, "job": name, "code": "write_token_permission"})
            if "uses" in job:
                if job["uses"] != "./.github/workflows/deploy.yml" or job.get("with") != {"ci_bundle": True}:
                    errors.append({"path": path.name, "job": name, "code": "unapproved_reusable_route"})
                continue
            if job.get("runs-on") != policy["public_ci_runner"]:
                errors.append({"path": path.name, "job": name, "code": "nonstandard_or_self_hosted_runner"})
            if "environment" in job and (path.name != "deploy.yml" or name != "deploy-dev" or job["environment"] != "dev"):
                errors.append({"path": path.name, "job": name, "code": "unapproved_environment_association"})
            for step in job.get("steps", []):
                if "uses" in step and not re.search(r"@[0-9a-f]{40}$", step["uses"]):
                    errors.append({"path": path.name, "job": name, "code": "unpinned_action"})
    deploy = yaml.safe_load((root / ".github/workflows/deploy.yml").read_text(encoding="utf-8"))
    if ("inputs.ci_bundle == true" not in deploy["jobs"]["package"]["if"]
            or any("!inputs.ci_bundle" not in deploy["jobs"][job]["if"] for job in ("verify", "deploy-dev"))):
        errors.append({"code": "ci_and_deployment_routes_not_separated"})
    protected = deploy["jobs"]["deploy-dev"]
    if (protected["needs"] != ["verify"] or not any(step.get("run") == "python -m scripts.deployment.handoff" for step in protected["steps"])
            or any("scripts.deployment.runtime" in step.get("run", "") or "docker " in step.get("run", "") for step in protected["steps"])):
        errors.append({"code": "public_workflow_must_only_prepare_handoff"})
    return {"valid": not errors, "cost_policy": policy["cost_policy"], "execution_mode": policy["execution_mode"],
            "workflows": len(workflows), "github_runtime_secrets_required": 0, "errors": errors}


def main() -> None:
    result = audit()
    output = Path(".ci-artifacts/portfolio-policy.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
