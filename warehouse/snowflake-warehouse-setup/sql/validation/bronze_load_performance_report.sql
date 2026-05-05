-- Phase 3 Stage 7 (#45): initial load performance baseline report
-- Expected source table:
--   FRAUDLENS.BRONZE.BRONZE_LOAD_BENCHMARK_RUNS
-- Required columns:
--   batch_id, dataset, run_index, status, row_count,
--   duration_seconds_wall_clock, duration_seconds_contract,
--   started_at_utc, finished_at_utc

WITH base AS (
  SELECT
    batch_id,
    dataset,
    run_index,
    status,
    row_count,
    duration_seconds_wall_clock,
    duration_seconds_contract,
    started_at_utc,
    finished_at_utc
  FROM FRAUDLENS.BRONZE.BRONZE_LOAD_BENCHMARK_RUNS
  WHERE batch_id = :batch_id
),
dataset_rollup AS (
  SELECT
    dataset,
    COUNT(*) AS total_runs,
    SUM(CASE WHEN status IN ('success', 'scaffold') THEN 1 ELSE 0 END) AS succeeded_runs,
    SUM(CASE WHEN status NOT IN ('success', 'scaffold') THEN 1 ELSE 0 END) AS failed_runs,
    AVG(duration_seconds_wall_clock) AS avg_wall_clock_seconds,
    MIN(duration_seconds_wall_clock) AS min_wall_clock_seconds,
    MAX(duration_seconds_wall_clock) AS max_wall_clock_seconds,
    SUM(CASE WHEN row_count > 0 THEN row_count ELSE 0 END) AS rows_loaded,
    CASE
      WHEN SUM(duration_seconds_wall_clock) > 0
      THEN SUM(CASE WHEN row_count > 0 THEN row_count ELSE 0 END) / SUM(duration_seconds_wall_clock)
      ELSE 0
    END AS rows_per_second
  FROM base
  GROUP BY dataset
),
batch_rollup AS (
  SELECT
    batch_id,
    COUNT(*) AS total_runs,
    SUM(CASE WHEN status IN ('success', 'scaffold') THEN 1 ELSE 0 END) AS succeeded_runs,
    SUM(CASE WHEN status NOT IN ('success', 'scaffold') THEN 1 ELSE 0 END) AS failed_runs,
    SUM(CASE WHEN row_count > 0 THEN row_count ELSE 0 END) AS rows_loaded,
    SUM(duration_seconds_wall_clock) AS total_wall_clock_seconds,
    AVG(duration_seconds_wall_clock) AS avg_run_wall_clock_seconds,
    CASE
      WHEN SUM(duration_seconds_wall_clock) > 0
      THEN SUM(CASE WHEN row_count > 0 THEN row_count ELSE 0 END) / SUM(duration_seconds_wall_clock)
      ELSE 0
    END AS rows_per_second
  FROM base
  GROUP BY batch_id
)
SELECT
  'BATCH_SUMMARY' AS section,
  batch_id,
  NULL AS dataset,
  total_runs,
  succeeded_runs,
  failed_runs,
  rows_loaded,
  total_wall_clock_seconds AS metric_1,
  avg_run_wall_clock_seconds AS metric_2,
  rows_per_second AS metric_3
FROM batch_rollup

UNION ALL

SELECT
  'DATASET_SUMMARY' AS section,
  NULL AS batch_id,
  dataset,
  total_runs,
  succeeded_runs,
  failed_runs,
  rows_loaded,
  avg_wall_clock_seconds AS metric_1,
  max_wall_clock_seconds AS metric_2,
  rows_per_second AS metric_3
FROM dataset_rollup
ORDER BY section, dataset;
