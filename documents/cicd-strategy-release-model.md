# CI/CD strategy and release model

Issue: [#84](https://github.com/Shreyash2942/FraudLens/issues/84)  
Parent: [#83 — Phase 8: CI/CD Implementation](https://github.com/Shreyash2942/FraudLens/issues/83)  
Decision date: November 17, 2026

This is the agreed design for validation, merge, promotion, and release control. The machine-readable operational contract is [`.github/cicd-release-contract.yaml`](../.github/cicd-release-contract.yaml). Issue #84 defines the operating model; issues #85–#91 implement and prove its controls.

## Priorities and task commits

| Order | Priority | Issue #84 task | Commit scope |
| --- | --- | --- | --- |
| 1 | P0 | Define CI goals and release flow | Validation gates, candidate identity, release evidence, and failure behavior. |
| 2 | P0 | Define branch and merge expectations | Branch ownership, pull requests, review, merge gates, and exceptions. |
| 3 | P0 | Define promotion path across environments | Secret-free CI, Data-Lab runtime checks, and optional Snowflake qualification. |
| 4 | P1 | Align strategy with milestones and delivery needs | Implementation dependencies, acceptance evidence, and Phase 9 handoff. |

The three P0 decisions establish the control boundaries before workflow implementation. Each task has one focused commit referencing #84.

## 1. CI goals and release flow

### Observed baseline

At the Phase 8 baseline, `main` contains merged Phase 7 at `0be6db2`. The existing [PR workflow](../.github/workflows/pr-validation.yml) runs `dbt Structure Validation` for changes under `dbt/` or its own workflow file. It performs dbt parsing, selector/governance/contract validation, and empty-catalog documentation generation using Python 3.11, dbt-core 1.8.7, and the Hive adapter.

The workflow does not yet provide repository-wide Python/standards checks, post-merge candidate validation, deployment, or release packaging. Read-only GitHub inspection on the decision date found no `main` branch protection or repository rulesets, no configured GitHub environments, and no published GitHub releases. These are baseline observations, not claims that the target policy is already enforced.

### Validation goals and gates

| Gate | Required outcome | Evidence | Implementation owner |
| --- | --- | --- | --- |
| Repository standards | Markdown links and YAML parse; governed naming, ownership, controls, and contracts remain aligned. | Validation log and structured findings. | #85, #87 |
| Python validation | Relevant generator, helper, observability, and Airflow scaffold tests pass in a clean workspace. | Test report tied to the tested commit. | #85, #87 |
| dbt validation | Parse, selectors, naming, governance metadata, contracts, failure policy, and empty-catalog docs pass. | Manifest and validator summaries. | #86 |
| CI Summary | Every applicable gate succeeds; an error, cancellation, missing result, or unjustified skip fails the summary. | Stable aggregate check with explicit applicability decisions. | #85 |

`CI Summary` is the proposed required merge check. The workflow must run for every pull request to `main`; individual jobs may classify changes, but workflow-level path filtering must not suppress the required summary. A docs-only change still runs standards/link/YAML validation and the summary. Runtime tests may be explicitly inapplicable with a recorded reason; a missing check is never evidence of success.

Use ephemeral GitHub-hosted runners for untrusted pull-request code, repository-content read permissions, and no deployment credentials. Do not execute untrusted pull-request revisions in privileged `pull_request_target` jobs or on the developer's persistent Data-Lab runner. Pin supported runner/dependency versions during implementation and record them with each run.

CI must start without ignored private `.env`, `synthetic_generator/runtime_config.yaml`, generated batches, dbt targets, or cached credentials. Cache dependency downloads only; do not reuse local data or a previous validation result. The Phase 7 clean-worktree baseline was 71 tests and 127 subtests; this is historical evidence, not a permanent test-count requirement.

### Candidate and release lifecycle

1. Develop and validate locally on an issue-linked branch.
2. Open a pull request to `main`; run secret-free checks against the pull-request merge candidate. Record both the head SHA and tested merge SHA.
3. Review and merge only after all applicable checks pass for the current revision.
4. Revalidate the resulting `main` commit. A passing pull-request SHA alone does not qualify a different merge commit.
5. Produce a candidate bundle identified by the full `main` commit SHA and workflow run/attempt. Include file digests and validation reports. A candidate is not a deployment.
6. Explicitly select that same candidate for runtime promotion. Reject arbitrary feature refs, altered artifacts, stale evidence, and changed configuration that lacks revalidation.
7. After required runtime checks and approval, create a protected, immutable release tag and GitHub release referring to that verified `main` commit. The release record identifies exactly which environment was validated.

Use `v0.MINOR.PATCH` for portfolio releases: increment MINOR for an accepted capability increment and PATCH for a compatible corrective release. Record incompatible contract changes explicitly in release notes and plan migration; a version number never substitutes for contract review. A phase boundary does not automatically publish a release, and no release tag is created by issue #84.

The candidate bundle must contain the commit SHA, pull request, workflow run/attempt, dependency versions, manifest and package digests, gate outcomes, configuration fingerprint without secrets, release notes, and operator owner. Runtime promotion adds environment identity, approver, batch/run IDs, smoke and quality results, metric/lineage evidence, and any accepted limitations. Keep reports for at least 30 days and retain a sanitized evidence index plus artifact checksums in the GitHub release record; secrets and generated banking data stay out of the bundle.

### Failure, retry, and recovery

- A failed or cancelled mandatory check blocks merge qualification and promotion. A retry may repair infrastructure failure, but must run against the same candidate and create a new run/attempt record.
- A new commit, manifest change, dependency change, or material environment/configuration change invalidates prior qualification. Build a new candidate and repeat affected checks.
- Serialize deployment per environment; do not cancel a deployment mid-migration to make way for a newer candidate. Pull-request checks may cancel superseded runs.
- On failed runtime verification, stop promotion and capture evidence. Restore the prior verified code/configuration candidate only when the operator confirms compatibility. Warehouse data/schema changes require a documented restore or forward-fix decision; checking out old code does not roll back data.

### Source references

The design follows GitHub's documented [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), and [secure workflow practices](https://docs.github.com/en/actions/reference/security/secure-use). Workflow and repository-setting implementation is tracked separately from this design.
