# Standards

This directory defines the rules that keep FraudLens consistent across design and future implementation.

## Standards Index

- `naming-conventions.md`
- `modeling-standard.md`
- `governance-controls.md`
- `auditability-standard.md`

Each contract under `specs/` should be interpretable against these standards without requiring hidden assumptions.

## Automated CI Baseline

Issue #87 implements these checks in [Code Validation](../.github/workflows/ci.yml):

| Standard | Automated scope |
| --- | --- |
| Naming and modeling | Versioned `specs/<domain>/vN/<entity>.yaml` identity, snake_case entity/field names, unique fields, declared required primary key, supported field types, descriptions, boolean nullability, and enumerated `_status` values. Business keys end in `_id`; the existing calendar/reference natural keys are explicitly documented exceptions. |
| Governance | Business owner, technical steward and approval model on every entity; boolean financial/fraud control classification; the seven minimum critical entities must remain present and critical. |
| Auditability | All ten shared audit fields remain in semantic conventions; entities declare inheritance or explicitly contain every shared audit field. |
| Documentation | Parsed Markdown links/images resolve to Git-tracked files or directories, including reference links, encoded spaces, and repository-root paths. Fenced/inline code examples are excluded. |
| Python | Ruff correctness rules `E9`, `F63`, `F7`, `F82` with Python 3.11 semantics; the complete `tests` and `airflow/tests` offline regression suite in a clean tracked-source snapshot. |
| Hygiene | Tracked Python/YAML syntax, required foundations, and rejection of tracked private configuration, generated artifacts and unsafe file references. |

External URLs and fragment/HTML anchors are outside the offline destination check. Semantic modeling decisions, relationship-map agreement, lineage design, issue linkage, approval quality, segregation of duties, and actual runtime data quality still require their existing review/runtime controls. This baseline does not certify all narrative standards automatically. Required status enforcement remains #89.

Checks produce sanitized JSON reports for 30 days; raw JUnit, generated banking data, logs, and private configuration are excluded. See the [execution and reproduction guide](../documents/phase-8-plan/issue-87-python-standards.md).
