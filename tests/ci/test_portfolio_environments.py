from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.deployment import environment_audit, environments, handoff, operator, runtime


class PortfolioEnvironmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="fraudlens-portfolio-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def context() -> dict:
        dev = environments.contract()["environments"]["dev"]
        return {"EXECUTION_MODE": "local_docker_operator", "CLOUD_RESOURCES_ENABLED": "false",
                "DOCKER_CONTAINER": dev["container"], "DEPLOY_ROOT": dev["managed_root"],
                "AIRFLOW_PYTHON": dev["runtime_python"], "SOURCE_ROOT": dev["source_root"],
                "GITHUB_SHA": "a" * 40, "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1"}

    def test_policy_rejects_cloud_activation_and_extra_active_environment(self) -> None:
        original = environments.contract()
        for change in ({"cloud_resources_enabled": True}, {"execution_mode": "cloud"}):
            path = self.root / "contract.json"
            path.write_text(json.dumps({**original, **change}))
            with self.subTest(change=change), patch.object(environments, "CONTRACT", path), self.assertRaises(ValueError):
                environments.contract()
        original["environments"]["prod"]["enabled"] = True
        path.write_text(json.dumps(original))
        with patch.object(environments, "CONTRACT", path), self.assertRaises(ValueError):
            environments.contract()

    def test_handoff_rejects_cloud_and_arbitrary_runtime_configuration(self) -> None:
        for change in ({"CLOUD_RESOURCES_ENABLED": "true"}, {"DEPLOY_ROOT": "/"},
                       {"DOCKER_CONTAINER": "unrelated-container"}, {"EXECUTION_MODE": "self_hosted"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                handoff.configuration({**self.context(), **change})

    def test_handoff_does_not_export_extra_secret_environment_values(self) -> None:
        verification = {"source_sha": "b" * 40, "ci_run_id": 99, "ci_run_attempt": 1,
                        "candidate_sha256": "c" * 64, "environment": "dev", "deployment_executed": False}
        context = {**self.context(), "FRAUDLENS_MONGODB_URI": "DO_NOT_EXPORT_SECRET"}
        with patch.object(handoff, "prepare", return_value=verification):
            record = handoff.create(context, self.root)
        self.assertFalse(record["deployment_executed"])
        self.assertNotIn("DO_NOT_EXPORT_SECRET", (self.root / "handoff.json").read_text())
        self.assertEqual(record["configuration_sha256"], handoff.fingerprint(record["configuration"]))

    @staticmethod
    def approval_fixture() -> tuple:
        run = {"id": 123, "run_attempt": 1, "head_sha": "a" * 40, "event": "workflow_dispatch",
               "head_branch": "main", "path": ".github/workflows/deploy.yml", "status": "completed", "conclusion": "success",
               "head_repository": {"full_name": "Shreyash2942/FraudLens"}, "actor": {"login": "Shreyash2942"}}
        reviews = [{"state": "approved", "user": {"login": "Shreyash2942"}, "environments": [{"name": "dev"}]}]
        jobs = [{"name": name, "conclusion": "success"} for name in ("Verify Main Candidate", "Prepare Approved Dev Handoff")]
        return run, reviews, jobs

    def test_operator_requires_real_main_owner_approval_and_handoff_job(self) -> None:
        run, reviews, jobs = self.approval_fixture()
        operator.approved_run(run, reviews, jobs)
        for change in ({"event": "pull_request"}, {"head_branch": "feature"}, {"conclusion": "failure"}, {"actor": {"login": "unrelated"}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                operator.approved_run({**run, **change}, reviews, jobs)
        for bad_reviews in ([], [{**reviews[0], "state": "rejected"}], [{**reviews[0], "user": {"login": "unrelated"}}]):
            with self.subTest(reviews=bad_reviews), self.assertRaises(ValueError):
                operator.approved_run(run, bad_reviews, jobs)
        with self.assertRaises(ValueError):
            operator.approved_run(run, reviews, jobs[:1])

    def test_operator_rejects_changed_configuration_before_docker(self) -> None:
        run, reviews, jobs = self.approval_fixture()
        settings = handoff.configuration(self.context())
        record = {"deployment_run_id": "123", "deployment_run_attempt": "1", "controller_sha": "a" * 40,
                  "environment": "dev", "execution_mode": "local_docker_operator", "deployment_executed": False,
                  "state": "approved_handoff_awaiting_local_operator", "configuration": settings,
                  "configuration_sha256": "0" * 64}
        data = {"actions/runs/123": run, "actions/runs/123/approvals": reviews}
        def pages(endpoint, key):
            if endpoint.endswith("jobs"):
                return jobs
            return [{"name": "dev-handoff-123-1", "expired": False, "id": 1}]
        with patch.object(operator, "github", return_value={"login": "Shreyash2942"}), \
             patch.object(operator.control, "api", side_effect=lambda endpoint: data[endpoint]), \
             patch.object(operator.control, "pages", side_effect=pages), \
             patch.object(operator.control, "download_artifact", return_value={"handoff.json": json.dumps(record).encode()}), \
             patch.object(operator, "configuration_context", return_value=self.context()), \
             patch.object(operator, "apply") as apply, self.assertRaises(ValueError):
            operator.prepare("123", self.root)
        apply.assert_not_called()

    def test_operator_default_is_plan_without_docker_execution(self) -> None:
        record = {"source_sha": "a" * 40, "deployment_run_id": "123", "configuration_sha256": "b" * 64}
        with patch.object(sys, "argv", ["operator", "--deployment-run", "123", "--report", str(self.root / "report.json")]), \
             patch.object(operator, "prepare", return_value=record), patch.object(operator, "apply") as apply, \
             redirect_stdout(io.StringIO()):
            operator.main()
        apply.assert_not_called()
        self.assertFalse(json.loads((self.root / "report.json").read_text())["deployment_executed"])

    def test_operator_accepts_approved_bound_handoff_without_executing_docker(self) -> None:
        run, reviews, jobs = self.approval_fixture()
        settings = handoff.configuration(self.context())
        record = {"deployment_run_id": "123", "deployment_run_attempt": "1", "controller_sha": "a" * 40,
                  "environment": "dev", "execution_mode": "local_docker_operator", "deployment_executed": False,
                  "state": "approved_handoff_awaiting_local_operator", "configuration": settings,
                  "configuration_sha256": handoff.fingerprint(settings), "source_sha": "b" * 40,
                  "candidate_sha256": "c" * 64, "ci_run_id": 99, "ci_run_attempt": 1}
        data = {"actions/runs/123": run, "actions/runs/123/approvals": reviews,
                "actions/variables/FRAUDLENS_DEV_DEPLOY_ENABLED": {"value": "true"},
                "actions/variables/FRAUDLENS_COST_PROFILE": {"value": "local_only_no_new_paid_resources"}}
        with patch.object(operator, "github", return_value={"login": "Shreyash2942"}), \
             patch.object(operator.control, "api", side_effect=lambda endpoint: data[endpoint]), \
             patch.object(operator.control, "pages", side_effect=lambda endpoint, key: jobs if key == "jobs" else [{"name": "dev-handoff-123-1", "expired": False}]), \
             patch.object(operator.control, "download_artifact", return_value={"handoff.json": json.dumps(record).encode()}), \
             patch.object(operator, "configuration_context", return_value=self.context()), \
             patch.object(operator.control, "prepare", return_value={"ci_run_attempt": 1}) as prepare:
            self.assertEqual(operator.prepare("123", self.root), record)
        self.assertEqual(prepare.call_args.args[0]["OWNER_APPROVAL"], "b" * 40)

    def test_operator_refuses_changed_local_controller_before_docker(self) -> None:
        with patch.object(operator.subprocess, "check_output", return_value=b"wrong\n"), \
             patch.object(operator.subprocess, "run") as run, self.assertRaises(ValueError):
            operator.apply({"controller_sha": "a" * 40}, self.root / "not-read.tar")
        run.assert_not_called()

    def test_docker_transport_does_not_forward_host_github_token_or_secret_values(self) -> None:
        settings = handoff.configuration(self.context())
        bundle = self.root / "candidate.tar"; bundle.write_bytes(b"public fixture source")
        record = {"controller_sha": "a" * 40, "source_sha": "b" * 40, "candidate_sha256": "c" * 64,
                  "configuration": settings, "configuration_sha256": handoff.fingerprint(settings), "deployment_run_id": "123"}
        result = subprocess.CompletedProcess([], 0, stdout=b'{"deployment_executed":true}\n')
        with patch.dict(os.environ, GH_TOKEN="DO_NOT_EXPORT_HOST_TOKEN"), \
             patch.object(operator.subprocess, "check_output", return_value=b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"), \
             patch.object(operator.subprocess, "run", side_effect=[subprocess.CompletedProcess([], 0), result]) as run:
            operator.apply(record, bundle)
        call = run.call_args
        self.assertEqual(call.args[0][:5], ["docker", "exec", "-i", "--user", "datalab"])
        self.assertNotIn("DO_NOT_EXPORT_HOST_TOKEN", call.kwargs["input"].decode())
        self.assertNotIn("-e", call.args[0])

    def test_airflow_process_does_not_receive_github_tokens(self) -> None:
        with patch.dict(os.environ, GH_TOKEN="DO_NOT_EXPORT", GITHUB_TOKEN="DO_NOT_EXPORT"), \
             patch.object(runtime.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            runtime.smoke(self.root, Path(sys.executable))
        self.assertNotIn("GH_TOKEN", run.call_args.kwargs["env"])
        self.assertNotIn("GITHUB_TOKEN", run.call_args.kwargs["env"])

    def test_workflow_audit_rejects_paid_self_hosted_unpinned_and_secret_routes(self) -> None:
        source = environments.ROOT / ".github/workflows"
        for kind in ("runner", "secret", "pin"):
            with self.subTest(kind=kind):
                target = self.root / kind / ".github/workflows"; target.mkdir(parents=True)
                for name in ("ci.yml", "deploy.yml"):
                    shutil.copyfile(source / name, target / name)
                path = target / "deploy.yml"; text = path.read_text()
                if kind == "runner":
                    text = text.replace("runs-on: ubuntu-24.04", "runs-on: self-hosted", 1)
                elif kind == "secret":
                    text = text.replace("${{ github.token }}", "${{ secrets.RUNTIME_PASSWORD }}", 1)
                else:
                    text = text.replace("actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803", "actions/checkout@main", 1)
                path.write_text(text)
                self.assertFalse(environment_audit.audit(target.parents[1])["valid"])

    def test_required_status_cannot_be_activated_using_only_feature_evidence(self) -> None:
        values = [{"commit": {"sha": "a" * 40}}, {"workflow_runs": [{"head_sha": "b" * 40, "path": ".github/workflows/ci.yml"}]}]
        with patch.object(environments, "github", side_effect=values), self.assertRaises(ValueError):
            environments.main_check_ready()


if __name__ == "__main__":
    unittest.main()
