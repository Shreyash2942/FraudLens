"""Fail-closed GitHub provenance and dev-environment preflight; never creates settings."""
from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
import zipfile
from pathlib import Path

from scripts.deployment.candidate import DIGEST, MAX_BYTES, REPOSITORY, SHA, sha256, verify


def api(endpoint: str) -> dict:
    return json.loads(subprocess.check_output(["gh", "api", "--hostname", "github.com", f"repos/{REPOSITORY}/{endpoint}"]))


def pages(endpoint: str, key: str) -> list[dict]:
    result = []
    for page in range(1, 101):
        rows = api(endpoint + ("&" if "?" in endpoint else "?") + f"per_page=100&page={page}")[key]
        result.extend(rows)
        if len(rows) < 100:
            return result
    raise ValueError("GitHub pagination exceeded limit")


def validate_dispatch(context: dict[str, str]) -> None:
    if (context.get("GITHUB_REPOSITORY") != REPOSITORY or context.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
            or context.get("GITHUB_REF") != "refs/heads/main"
            or context.get("GITHUB_ACTOR", "").lower() != REPOSITORY.split("/")[0].lower()):
        raise ValueError("Deployment requires an owner dispatch from main")
    if context.get("TARGET_ENVIRONMENT") != "dev" or context.get("DEPLOY_ENABLED") != "true":
        raise ValueError("Dev deployment controls are not activated; cloud deployment is disabled")
    if context.get("COST_PROFILE") != "local_only_no_new_paid_resources":
        raise ValueError("The local-only portfolio cost policy must be explicit")
    sha = context.get("CANDIDATE_SHA", "")
    if (not SHA.fullmatch(sha) or context.get("OWNER_APPROVAL") != sha
            or not DIGEST.fullmatch(context.get("CANDIDATE_SHA256", ""))
            or not context.get("CI_RUN_ID", "").isdigit() or int(context["CI_RUN_ID"]) <= 0):
        raise ValueError("Invalid candidate selection or owner acceptance")


def check_remote(context: dict[str, str]) -> tuple[dict, dict]:
    validate_dispatch(context)
    if api("").get("visibility") != "public":
        raise ValueError("This portfolio workflow requires a public repository and standard free runners")
    sha, run_id = context["CANDIDATE_SHA"], context["CI_RUN_ID"]
    run = api(f"actions/runs/{run_id}")
    if any(run.get(key) != value for key, value in {
        "head_sha": sha, "head_branch": "main", "event": "push", "status": "completed",
        "conclusion": "success", "path": ".github/workflows/ci.yml"}.items()):
        raise ValueError("Candidate requires a completed successful push-to-main CI run")
    if run.get("head_repository", {}).get("full_name") != REPOSITORY:
        raise ValueError("Candidate repository mismatch")
    jobs = pages(f"actions/runs/{run_id}/jobs", "jobs")
    for name in ("Baseline Repository Checks", "dbt Validation", "Python Validation", "CI Summary"):
        matches = [job for job in jobs if job["name"] == name]
        if len(matches) != 1 or matches[0]["conclusion"] != "success":
            raise ValueError("Required CI gate is missing or unsuccessful")
    comparison = api(f"compare/{sha}...main")
    if comparison.get("status") not in ("ahead", "identical") or comparison["merge_base_commit"]["sha"] != sha:
        raise ValueError("Candidate is not an ancestor of main")
    environment = api("environments/dev")  # A 404/403 stops preflight; never PUT an environment.
    policy = environment.get("deployment_branch_policy") or {}
    reviewers = [rule for rule in environment.get("protection_rules", []) if rule.get("type") == "required_reviewers"]
    if (environment.get("can_admins_bypass") is not False or not policy.get("custom_branch_policies")
            or policy.get("protected_branches") or not reviewers or not reviewers[0].get("reviewers")):
        raise ValueError("Approved environment protections are missing")
    owner = REPOSITORY.split("/")[0].lower()
    if not any(row.get("type") == "User" and row.get("reviewer", {}).get("login", "").lower() == owner
               for row in reviewers[0]["reviewers"]):
        raise ValueError("Dev owner review protection is missing")
    branches = pages("environments/dev/deployment-branch-policies", "branch_policies")
    if len(branches) != 1 or branches[0].get("name") != "main" or branches[0].get("type", "branch") != "branch":
        raise ValueError("Dev must restrict deployments to the main branch only")
    name = f"candidate-{sha}-{run_id}-{run['run_attempt']}"
    artifacts = [row for row in pages(f"actions/runs/{run_id}/artifacts", "artifacts") if row["name"] == name]
    if len(artifacts) != 1 or artifacts[0].get("expired") or artifacts[0]["size_in_bytes"] > MAX_BYTES:
        raise ValueError("Candidate artifact is missing, expired or oversized")
    return run, artifacts[0]


def download_artifact(artifact: dict, expected_names: set[str]) -> dict[str, bytes]:
    archive = subprocess.check_output(["gh", "api", "--hostname", "github.com",
                                       f"repos/{REPOSITORY}/actions/artifacts/{artifact['id']}/zip"])
    if len(archive) > MAX_BYTES or artifact.get("digest") != "sha256:" + sha256(archive):
        raise ValueError("GitHub artifact digest mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        if (len(zipped.infolist()) != len(expected_names) or set(zipped.namelist()) != expected_names
                or sum(item.file_size for item in zipped.infolist()) > MAX_BYTES):
            raise ValueError("Unexpected artifact contents")
        return {name: zipped.read(name) for name in expected_names}


def prepare(context: dict[str, str], output: Path) -> dict:
    run, artifact = check_remote(context)
    raw = download_artifact(artifact, {"candidate.tar", "candidate.sha256", "candidate-report.json"})["candidate.tar"]
    output.mkdir(parents=True, exist_ok=True)
    bundle = output / "candidate.tar"
    bundle.write_bytes(raw)
    manifest, _ = verify(bundle, context["CANDIDATE_SHA256"], context["CANDIDATE_SHA"])
    if (manifest.get("origin_main_push") is not True or manifest["ci_run_id"] != str(run["id"])
            or manifest["ci_run_attempt"] != str(run["run_attempt"])):
        raise ValueError("Preview or mismatched bundle cannot be promoted")
    report = {"source_sha": manifest["source_sha"], "ci_run_id": run["id"], "ci_run_attempt": run["run_attempt"],
              "candidate_sha256": context["CANDIDATE_SHA256"], "artifact_id": artifact["id"],
              "artifact_digest": artifact["digest"], "environment": "dev", "profile": "local",
              "actor": context["GITHUB_ACTOR"], "owner_acceptance": True, "deployment_executed": False}
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    output = Path(".ci-artifacts/deployment")
    try:
        report = prepare(dict(os.environ), output)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile, tarfile.TarError) as error:
        output.mkdir(parents=True, exist_ok=True)
        (output / "verification.json").write_text(json.dumps({"status": "rejected", "error_type": type(error).__name__,
                                                              "deployment_executed": False}) + "\n", encoding="utf-8")
        raise SystemExit("Deployment preflight rejected the request") from None
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
