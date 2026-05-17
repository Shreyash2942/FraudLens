# Phase 4 Build Validation Artifacts

Issue: `#55`  
Generated: `2026-05-17`

## Latest Successful Build Artifact

Source: `dbt/target/run_results.json`

- generated_at_utc: `2026-05-16T03:04:16.432850Z`
- invocation_id: `4073b2d1-8a3d-49c4-a181-8509827bcd89`
- result_count: `30`
- status_counts:
  - `success`: `4`
  - `pass`: `26`

## Current Build Attempt (Captured Failure Evidence)

Command:

```bash
dbt build --project-dir dbt --profiles-dir dbt/profiles --profile fraudlens_local_spark --target local
```

Outcome:

- attempted_at_local: `2026-05-17T19:24:42`
- exit_code: `2`
- failure_category: `connectivity`
- failure_detail: `Could not connect to Hive thrift endpoint at 127.0.0.1:10000`
- raw_log: `documents/validation/issue-55-build-attempt-2026-05-17.log`

## Note

Validation evidence is preserved even when runtime connectivity is unavailable, so readiness tracking can continue without losing traceability.
