# Issue #90: end-to-end CI/CD qualification

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
