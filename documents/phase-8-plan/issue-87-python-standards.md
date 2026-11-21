# Issue #87: Python checks and repository standards

Issue: [#87](https://github.com/Shreyash2942/FraudLens/issues/87)

Parent: [#83](https://github.com/Shreyash2942/FraudLens/issues/83)

Branch: `83-phase-8-cicd-implementation`

Validation date: November 20, 2026 (America/New_York; live runs use November 21 UTC)

## Priorities and task commits

| Priority | Task | Delivery |
| --- | --- | --- |
| 1 | Add Python environment setup | `028860f`: hosted Ubuntu 24.04/Python 3.11, pinned compatible generator/test/lint dependencies, `pip check`, tool versions, no runtime services or deployment secrets. |
| 2 | Add script validation or lint checks | `4ca1ecd`: tracked-file Ruff correctness rules, no source rewriting, sanitized lint report, failure handling tests. |
| 3 | Validate generator and helper scripts | `0bab8df`: complete offline generator/helper suite in a temporary tracked-source snapshot, sanitized test counts, aggregate gate and all 216 result combinations. |
| 4 | Align checks with repository standards | This commit: governed metadata/audit/naming and Markdown destination validation, policy/reproduction documentation, live pass/failure proof, evidence and scoped graph refresh. |

The [workflow](../../.github/workflows/ci.yml) runs baseline/standards, dbt and Python validation for every PR to `main`, including drafts and all paths, plus configured push-to-main revalidation. `CI Summary` uses `always()` and accepts only `success` from all three jobs. Failure, cancellation, skip, missing and unknown results fail qualification. Enforcement of required checks remains #89; the phase PR remains draft until the remaining Phase 8 work is ready.

## Python environment and validation

`requirements-python-ci.txt` includes the runtime bounds in `requirements-phase2.txt`, the baseline requirements, and exact pins for Faker 37.12.0, minio 7.2.20, pytest 9.0.3 and Ruff 0.17.6. These pins keep the established generator generation compatible; the independent Hive/dbt job retains its own dependencies.

Ruff evaluates only explicit Git-tracked `.py` paths with `ruff.toml`, Python 3.11 semantics, correctness rules `E9`, `F63`, `F7`, `F82`, and no fixes. Baseline Python AST/YAML validation remains in place. Undefined names, invalid control flow/comparisons, syntax, missing inventory and linter/tool errors fail validation. Diagnostics in the uploaded JSON include only rule, repository-relative path and location.

The test stage requires successful lint and a valid tracked-file baseline. It copies current tracked source, including staged new files and edits, into a temporary workspace. It excludes ignored `.env`, generator runtime configuration, caches, existing generated data, inherited MinIO settings and injected pytest/Python import options. Plugin autoload is disabled. It runs:

```bash
python -m pytest tests airflow/tests -q --strict-config --strict-markers
```

The suite generates temporary small synthetic batches, validates the 21 datasets and curated blueprint behavior, exercises configuration/MinIO clients through mocks, tests dbt naming helpers, and checks orchestration/logging/lineage/metrics/documentation utilities. Airflow checks are offline tests; CI does not start a scheduler or claim full DAG runtime execution. Existing MinIO tests now resolve the mocked client before clearing the environment, so native library loading does not depend on an erased Windows `PATH`.

Test failure, missing/malformed result XML, empty discovery or an all-skipped suite fails the job. Temporary JUnit is reduced to counts; only sanitized JSON is uploaded for 30 days. Raw JUnit, logs, profiles and generated data are not uploaded. JUnit counts include unittest subtests, so they differ from pytest's top-level test count.

## Repository standards

The baseline job additionally runs `python -m scripts.ci.validate_standards`, checking the [automated standards policy](../../standards/README.md): required standards files, versioned entity identity, snake_case fields, declared required primary keys, field descriptions/types/nullability, enumerated statuses, owners/stewards/approval, control classification and inherited or explicit audit fields. The seven minimum critical entities must remain critical and present. Shared semantic conventions retain all ten audit fields. Existing `calendar_date` and `code_set_name` natural keys remain documented exceptions.

Markdown links/images, including references, encoded spaces, root-relative paths and directories, must resolve to tracked content. Code examples are parsed as code. External URL availability, fragments/HTML anchors, relationship-map agreement and deeper business semantics remain their existing manual/runtime review controls; this baseline does not claim complete automated certification of every narrative standard.

## Reproduction and execution evidence

Use Python 3.11 in a clean checkout or virtual environment:

```bash
python -m pip install -r requirements-python-ci.txt
python -m pip check
python -m scripts.ci.validate_python --stage lint
python -m scripts.ci.validate_python --stage tests
python -m scripts.ci.validate_standards
```

Stage newly added files before validating: `git add` supplies the input inventory; the test runner uses current tracked source instead of ignored local configuration or only the previous commit. No live services are needed.

Execution evidence records the passing project and controlled failures, exact source/merge SHAs, report inspection and probe cleanup. The final documentation/evidence commit receives another normal PR run. Default-branch execution before merge is not claimed. Environment controls #89 precede privileged deployment #88, followed by #90 runtime qualification and #91 handoff; parent #83 remains open.
