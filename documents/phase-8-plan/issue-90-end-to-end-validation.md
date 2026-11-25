# Issue #90: end-to-end CI/CD qualification

Historical pre-merge qualification record. The owner subsequently merged PR #122, closed #83/#90, and main-push CI passed with strict required `CI Summary` enforcement enabled. Runtime activation/pipeline/failure-recovery proof is still not established. See the [current CI/CD handoff](../cicd-workflows-release-process.md); pending merge/issue-state statements below describe this record's original date.

Issue: [#90](https://github.com/Shreyash2942/FraudLens/issues/90). Parent: [#83](https://github.com/Shreyash2942/FraudLens/issues/83).

Validation started November 23, 2026 (America/New_York).

## Priorities and four task commits

| Priority | Issue task | Required proof |
| --- | --- | --- |
| P0 / task 1 | Trigger CI from a pull request | Push this scoped documentation change to the phase branch; record the real PR-triggered run, head identity and gate results. |
| P0 / task 2 | Confirm invalid changes fail correctly | Use a disposable PR with an actual undefined Python name; require Python and CI Summary failure, baseline/dbt success and packaging/deployment skipped. Close the probe without merging and remove its branch/worktree. |
| P1 / task 3 | Confirm valid changes pass and promote | After owner-approved main merge: require successful exact-main push CI, seal required CI Summary, verify its candidate, dispatch the protected dev handoff, record owner environment approval and explicitly activate through the local Docker operator. |
| P1 / task 4 | Review workflow logs and outcomes | Correlate source/run/attempt/artifact identities, approvals and local activation/service outcomes. Preserve sanitized evidence and document failure/recovery and any remaining runtime limits before issue closure. |

Keep one commit per issue task. The first two commits establish pre-merge evidence; they do not complete promotion. The later task commits must record actual outcomes, never a predicted success.

## Execution boundaries

Use the [#89 environment controls](issue-89-environment-controls.md): one existing Docker dev runtime, disabled test/prod policy records, public standard GitHub runners and private local service credentials. Provision no paid cloud resources, new containers, self-hosted runners or test/prod compute.

PR previews are not deployment candidates. The [release contract](../../.github/cicd-release-contract.yaml) requires a reviewed merge, successful push CI on the actual main SHA and explicit owner approval before promotion. The draft [Phase 8 PR #122](https://github.com/Shreyash2942/FraudLens/pull/122) has not been merged at the start of this qualification. Do not bypass main identity, environment approval or required gate checks to finish this issue.

After approved merge and successful main CI:

1. Run `python -m scripts.deployment.environments --section protections --seal-main --apply` from the reviewed main source.
2. Download and verify the current main CI candidate's GitHub ZIP, tar, provenance and all file digests; retain its exact SHA, run/attempt and digest.
3. Dispatch `deploy.yml` on main with `operation=verify`, target dev, and those exact candidate inputs. Inspect the result before dispatching `operation=deploy` and completing owner environment approval.
4. From a clean checkout matching the deployment controller SHA, run `python -m scripts.deployment.operator --deployment-run <run-id>` to inspect the plan, then repeat with `--apply` for explicit local activation.
5. Inspect actual Airflow imports/paused-and-drained metadata and local service checks. Perform controlled failure/recovery qualification within the managed dev sandbox; record precisely whether the full data pipeline was exercised. Leave test/prod disabled.

No main merge, real main handoff, local source activation, pipeline execution or end-to-end completion is claimed by this initial plan. Keep #90, parent #83 and final handoff #91 open until their respective evidence is available.

## Pre-merge execution evidence

Sanitized machine evidence: [issue-90-premerge-validation.json](../evidence/phase-8/issue-90-premerge-validation.json).

| Case | Actual outcome |
| --- | --- |
| Valid PR change | [Run 45251226338](https://github.com/Shreyash2942/FraudLens/actions/runs/45251226338), task-1 commit `c38cf9d`: repository, dbt, Python, candidate packaging and CI Summary passed. Hosted Linux passed 123 tests/1,471 subtests; 147 Python files linted, no skips. Protected dispatch jobs remained skipped. |
| Invalid PR change | [Run 45251287212](https://github.com/Shreyash2942/FraudLens/actions/runs/45251287212): an actual undefined name produced Ruff `F821`; Python and CI Summary failed. Repository/dbt passed, deployment validation was skipped and no candidate/handoff artifact was produced. |
| Preview integrity | Downloaded GitHub ZIP, tar and every source-file digest verified. The valid bundle remains preview-only and excludes the negative probe, private runtime configuration and generated batches. |
| Promotion refusal | The actual local operator rejected the PR CI run as a deployment handoff. It did not activate source or produce a successful operator report. This validates blocking, not successful promotion. |
| Local readiness | Actual Airflow import and paused/drained gate passed against the existing checkout; four DAGs paused, zero runs, no current source pointer. Local Hive/metastore/Marquez/Prometheus/Grafana TCP ports responded; TCP readiness does not prove pipeline or service semantics. |
| Probe cleanup | [PR #128](https://github.com/Shreyash2942/FraudLens/pull/128) closed without merge. Its exact remote branch, local branch and checked temporary worktree were removed. No intentional failure is on the phase branch. |

Task 1 is commit `c38cf9d`; task 2 is the containing evidence commit. No deployment implementation changed: this issue's pre-merge diff is documentation and sanitized evidence only. The final evidence commit receives fresh normal PR validation before merge approval is requested.

Tasks 3 and 4 remain pending owner approval of the reviewed Phase 8 merge candidate. PR #122 is still draft, main still points to `0be6db22652c135df81aaad885e251a52d1bf314`, and its main-push/deployment workflow cannot run before merge. Neither prior fixture tests nor the readiness probe substitute for that proof. The next action is an explicit owner decision on the merge, followed by actual main CI and protected local promotion; do not close #90 based only on these PR checks.
