from __future__ import annotations

import os
import itertools
import io
import shlex
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml


ROOT = Path(__file__).resolve().parents[2]


class WorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))

    def test_every_main_pr_and_main_push_is_covered_without_path_filtering(self) -> None:
        events = self.workflow["on"]
        self.assertEqual(events["pull_request"]["branches"], ["main"])
        self.assertEqual(events["push"]["branches"], ["main"])
        self.assertIn("workflow_dispatch", events)
        self.assertNotIn("pull_request_target", events)
        for trigger in ("pull_request", "push"):
            self.assertNotIn("paths", events[trigger])
            self.assertNotIn("paths-ignore", events[trigger])

    def test_summary_executes_for_failure_and_requires_a_result(self) -> None:
        job = self.workflow["jobs"]["ci-summary"]
        self.assertEqual(job["name"], "CI Summary")
        self.assertEqual(job["needs"], ["repository-checks", "dbt-validation", "python-validation", "deployment-validation"])
        self.assertIn("always()", job["if"])
        command = shlex.split(job["steps"][0]["run"])
        self.assertEqual(command[:2], ["python", "-c"])
        self.assertEqual(job["steps"][0]["env"]["DBT_RESULT"], "${{ needs.dbt-validation.result }}")
        self.assertEqual(job["steps"][0]["env"]["PYTHON_RESULT"], "${{ needs.python-validation.result }}")
        code = compile(command[2], "<workflow-summary>", "exec")
        self.assertEqual(job["steps"][0]["env"]["DEPLOYMENT_RESULT"], "${{ needs.deployment-validation.result }}")
        for baseline, dbt, python, deployment in itertools.product(("success", "failure", "cancelled", "skipped", "", "unknown"), repeat=4):
            with self.subTest(baseline=baseline, dbt=dbt, python=python, deployment=deployment), \
                 patch.dict(os.environ, BASELINE_RESULT=baseline, DBT_RESULT=dbt, PYTHON_RESULT=python, DEPLOYMENT_RESULT=deployment), \
                 redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                exec(code, {})
            self.assertEqual(result.exception.code == 0, baseline == dbt == python == deployment == "success")

    def test_jobs_are_bounded_read_only_and_do_not_use_deployment_environments(self) -> None:
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        for job in self.workflow["jobs"].values():
            if "uses" in job:
                self.assertEqual(job["uses"], "./.github/workflows/deploy.yml")
                self.assertNotIn("secrets", job)
                self.assertEqual(job["with"], {"ci_bundle": True})
                self.assertEqual(job["needs"], ["repository-checks", "dbt-validation", "python-validation"])
                continue
            self.assertEqual(job["runs-on"], "ubuntu-24.04")
            self.assertLessEqual(job["timeout-minutes"], 10)
            self.assertNotIn("environment", job)
            self.assertNotIn("continue-on-error", job)
            for step in job["steps"]:
                if "uses" in step:
                    self.assertRegex(step["uses"], r"@[0-9a-f]{40}$")
                    if step["uses"].startswith("actions/checkout@"):
                        self.assertFalse(step["with"]["persist-credentials"])

    def test_pr_cancellation_does_not_cancel_main_candidate_validation(self) -> None:
        self.assertEqual(self.workflow["concurrency"]["cancel-in-progress"], "${{ github.event_name == 'pull_request' }}")


if __name__ == "__main__":
    unittest.main()
