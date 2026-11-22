from __future__ import annotations

import copy
import io
import json
import os
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts.deployment import candidate, control, runtime


class DeploymentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="fraudlens-deployment-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        files = {"README.md": "Fixture only", "example.py": "VALUE = 1\n",
                 "synthetic_generator/contracts.py": "DATASET_ORDER = []\n",
                 "dbt/dbt_project.yml": "name: fixture\n",
                 "airflow/dags/fraudlens_pipeline_orchestration.py": "VALUE = 1\n",
                 "airflow/config/orchestration_profiles.yml": yaml.safe_dump({"defaults": {"profile": "local"},
                     "profiles": {"local": {"transformation": {"dbt_profile": "fraudlens_local_spark", "dbt_target": "local"},
                                             "validation": {"dbt_target": "local"}}}})}
        for name, data in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data, encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=CI Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        self.context = {"GITHUB_REPOSITORY": candidate.REPOSITORY, "GITHUB_EVENT_NAME": "push",
                        "GITHUB_REF": "refs/heads/main", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1"}
        self.output = self.root / "bundle"
        self.report = candidate.build(self.repo, self.output, self.context)
        self.bundle = self.output / "candidate.tar"
        self.sha = self.report["source_sha"]
        self.digest = self.report["candidate_sha256"]

    def git(self, *args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=self.repo, stderr=subprocess.DEVNULL)

    def dispatch(self) -> dict:
        return {**self.context, "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_ACTOR": "Shreyash2942",
                "DEPLOY_ENABLED": "true", "TARGET_ENVIRONMENT": "dev", "CANDIDATE_SHA": self.sha,
                "OWNER_APPROVAL": self.sha, "CANDIDATE_SHA256": self.digest, "CI_RUN_ID": "123"}

    def remote(self) -> dict:
        return {"actions/runs/123": {"id": 123, "run_attempt": 1, "head_sha": self.sha, "head_branch": "main",
                    "event": "push", "status": "completed", "conclusion": "success", "path": ".github/workflows/ci.yml",
                    "head_repository": {"full_name": candidate.REPOSITORY}},
                "actions/runs/123/jobs": {"jobs": [{"name": name, "conclusion": "success"} for name in
                    ("Baseline Repository Checks", "dbt Validation", "Python Validation", "CI Summary")]},
                f"compare/{self.sha}...main": {"status": "identical", "merge_base_commit": {"sha": self.sha}},
                "environments/dev": {"can_admins_bypass": False, "deployment_branch_policy": {"custom_branch_policies": True, "protected_branches": False},
                    "protection_rules": [{"type": "required_reviewers", "reviewers": [{"type": "User", "reviewer": {"login": "Shreyash2942"}}]}]},
                "environments/dev/deployment-branch-policies": {"branch_policies": [{"name": "main", "type": "branch"}]},
                "actions/runs/123/artifacts": {"artifacts": [{"id": 77, "name": f"candidate-{self.sha}-123-1", "expired": False, "size_in_bytes": 1000}]}}

    @staticmethod
    def api_stub(data: dict):
        return lambda endpoint: copy.deepcopy(data[endpoint.split("?", 1)[0]])

    def test_candidate_round_trip_digest_and_dirty_source_rejection(self) -> None:
        manifest, files = candidate.verify(self.bundle, self.digest, self.sha)
        self.assertTrue(manifest["origin_main_push"])
        self.assertEqual(files["example.py"], b"VALUE = 1\n")
        with self.assertRaises(ValueError):
            candidate.verify(self.bundle, "0" * 64, self.sha)
        (self.repo / "example.py").write_text("VALUE = 2\n")
        with self.assertRaises(subprocess.CalledProcessError):
            candidate.build(self.repo, self.output, self.context)

    def test_pr_bundle_is_explicitly_preview_only(self) -> None:
        report = candidate.build(self.repo, self.output, {**self.context, "GITHUB_EVENT_NAME": "pull_request", "GITHUB_REF": "refs/pull/1/merge"})
        self.assertEqual(report["qualification"], "preview_only")
        self.assertFalse(report["origin_main_push"])

    def test_tar_traversal_links_and_duplicate_members_are_rejected(self) -> None:
        for name, mode in (("../escape", tarfile.REGTYPE), ("payload/link", tarfile.SYMTYPE), ("manifest.json", tarfile.REGTYPE)):
            with self.subTest(name=name, mode=mode):
                buffer = io.BytesIO()
                with tarfile.open(fileobj=buffer, mode="w") as archive:
                    info = tarfile.TarInfo(name); info.type = mode; info.size = 2 if mode == tarfile.REGTYPE else 0
                    archive.addfile(info, io.BytesIO(b"{}") if info.size else None)
                    if name == "manifest.json":
                        archive.addfile(info, io.BytesIO(b"{}"))
                self.bundle.write_bytes(buffer.getvalue())
                with self.assertRaises(ValueError):
                    candidate.verify(self.bundle, candidate.sha256(buffer.getvalue()), self.sha)

    def test_dispatch_rejects_feature_pr_cloud_missing_activation_and_missing_acceptance(self) -> None:
        changes = [{"GITHUB_REF": "refs/heads/feature"}, {"GITHUB_EVENT_NAME": "pull_request"},
                   {"TARGET_ENVIRONMENT": "prod"}, {"DEPLOY_ENABLED": ""}, {"OWNER_APPROVAL": ""},
                   {"GITHUB_ACTOR": "another-user"}, {"CI_RUN_ID": "123; command"}]
        for change in changes:
            with self.subTest(change=change), patch.object(control, "api") as api, self.assertRaises(ValueError):
                control.check_remote({**self.dispatch(), **change})
            api.assert_not_called()

    def test_remote_provenance_gates_and_environment_rules_reject_invalid_evidence(self) -> None:
        changes = [("actions/runs/123", "event", "pull_request"), ("actions/runs/123", "conclusion", "failure"),
                   ("actions/runs/123/jobs", "jobs", []), (f"compare/{self.sha}...main", "status", "diverged"),
                   ("environments/dev", "can_admins_bypass", True), ("environments/dev", "protection_rules", []),
                   ("environments/dev/deployment-branch-policies", "branch_policies", [{"name": "*"}]),
                   ("actions/runs/123/artifacts", "artifacts", [])]
        for endpoint, key, value in changes:
            data = self.remote(); data[endpoint][key] = value
            with self.subTest(endpoint=endpoint, key=key), patch.object(control, "api", side_effect=self.api_stub(data)), self.assertRaises(ValueError):
                control.check_remote(self.dispatch())

    def test_missing_environment_is_never_created(self) -> None:
        data = self.remote()
        def api(endpoint):
            if endpoint == "environments/dev":
                raise subprocess.CalledProcessError(1, "gh")
            return self.api_stub(data)(endpoint)
        with patch.object(control, "api", side_effect=api) as mocked, self.assertRaises(subprocess.CalledProcessError):
            control.check_remote(self.dispatch())
        self.assertTrue(all(not str(call.args[0]).startswith(("PUT", "POST")) for call in mocked.call_args_list))

    def test_remote_archive_verified_twice_and_preview_cannot_be_promoted(self) -> None:
        data = self.remote()
        zipped = io.BytesIO()
        with zipfile.ZipFile(zipped, "w") as archive:
            for path in self.output.iterdir():
                archive.writestr(path.name, path.read_bytes())
        raw = zipped.getvalue()
        data["actions/runs/123/artifacts"]["artifacts"][0]["digest"] = "sha256:" + candidate.sha256(raw)
        with patch.object(control, "api", side_effect=self.api_stub(data)), patch.object(control.subprocess, "check_output", return_value=raw):
            report = control.prepare(self.dispatch(), self.root / "verified")
            self.assertFalse(report["deployment_executed"])
            with self.assertRaises(ValueError):
                control.prepare({**self.dispatch(), "CANDIDATE_SHA256": "0" * 64}, self.root / "invalid")
        data["actions/runs/123/artifacts"]["artifacts"][0]["digest"] = "sha256:" + "0" * 64
        with patch.object(control, "api", side_effect=self.api_stub(data)), patch.object(control.subprocess, "check_output", return_value=raw), self.assertRaises(ValueError):
            control.prepare(self.dispatch(), self.root / "bad-outer-digest")
        preview = candidate.build(self.repo, self.output, {**self.context, "GITHUB_EVENT_NAME": "pull_request"})
        zipped = io.BytesIO()
        with zipfile.ZipFile(zipped, "w") as archive:
            for path in self.output.iterdir():
                archive.writestr(path.name, path.read_bytes())
        raw = zipped.getvalue()
        data["actions/runs/123/artifacts"]["artifacts"][0]["digest"] = "sha256:" + candidate.sha256(raw)
        with patch.object(control, "api", side_effect=self.api_stub(data)), patch.object(control.subprocess, "check_output", return_value=raw), self.assertRaises(ValueError):
            control.prepare({**self.dispatch(), "CANDIDATE_SHA256": preview["candidate_sha256"]}, self.root / "bad-preview")

    @unittest.skipUnless(os.name == "posix", "Runtime activation requires Linux symlinks; exercised on hosted CI")
    def test_activation_is_idempotent_and_failed_import_preserves_previous_candidate(self) -> None:
        root = self.root / "runtime"; root.mkdir()
        (root / ".fraudlens-runtime.json").write_text(json.dumps({"schema_version": 1, "repository": candidate.REPOSITORY, "environment": "dev", "profile": "local"}))
        first = runtime.activate(self.bundle, self.digest, self.sha, root, lambda release: None)
        previous = (root / "current").resolve()
        again = runtime.activate(self.bundle, self.digest, self.sha, root, lambda release: None)
        self.assertEqual(first["active_release"], again["active_release"])
        (self.repo / "example.py").write_text("VALUE = 2\n")
        self.git("add", ".")
        self.git("-c", "user.name=CI Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "next candidate")
        next_report = candidate.build(self.repo, self.output, self.context)
        with self.assertRaises(ValueError):
            runtime.activate(self.bundle, next_report["candidate_sha256"], next_report["source_sha"], root,
                             lambda release: (_ for _ in ()).throw(ValueError("import failed")))
        self.assertEqual((root / "current").resolve(), previous)
        self.assertFalse((root / ".current-next").exists())
        recovered = runtime.activate(self.bundle, next_report["candidate_sha256"], next_report["source_sha"], root, lambda release: None)
        self.assertEqual(recovered["previous_release"], first["active_release"])
        self.assertNotEqual(recovered["active_release"], first["active_release"])

    @unittest.skipUnless(os.name == "posix", "Runtime activation requires Linux; exercised on hosted CI")
    def test_runtime_refuses_unmanaged_directory_and_modified_release(self) -> None:
        root = self.root / "runtime"; root.mkdir()
        (root / ".fraudlens-runtime.json").write_text(json.dumps({"schema_version": 1, "repository": candidate.REPOSITORY, "environment": "dev", "profile": "local"}))
        (root / "current").mkdir()
        with self.assertRaises(ValueError):
            runtime.activate(self.bundle, self.digest, self.sha, root, lambda release: None)
        (root / "current").rmdir()
        runtime.activate(self.bundle, self.digest, self.sha, root, lambda release: None)
        (root / "current/example.py").write_text("tampered")
        with self.assertRaises(ValueError):
            runtime.activate(self.bundle, self.digest, self.sha, root, lambda release: self.fail("must not smoke altered source"))

    def test_workflow_preflight_precedes_environment_and_prs_only_package(self) -> None:
        workflow = yaml.safe_load((candidate.ROOT / ".github/workflows/deploy.yml").read_text())
        self.assertEqual(set(workflow["on"]), {"workflow_call", "workflow_dispatch"})
        self.assertNotIn("environment", workflow["jobs"]["verify"])
        deploy = workflow["jobs"]["deploy-dev"]
        self.assertEqual(deploy["needs"], ["verify"])
        self.assertEqual(deploy["environment"], "dev")
        self.assertIn("refs/heads/main", deploy["if"])
        self.assertIn("workflow_dispatch", deploy["if"])
        self.assertFalse(deploy["concurrency"]["cancel-in-progress"])
        for job in workflow["jobs"].values():
            for step in job["steps"]:
                self.assertNotIn("continue-on-error", step)
                if "uses" in step:
                    self.assertRegex(step["uses"], r"@[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
