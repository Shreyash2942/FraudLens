# FraudLens Platform Validation Runbook

## Goal

Confirm that the external Data-Lab runtime satisfies the FraudLens Phase 1 platform contract.

This runbook validates logical platform capabilities. It does not require each capability to be deployed as its own container.

## Validation Order

1. Docker runtime availability
2. Airflow reachability
3. PostgreSQL metadata availability
4. MinIO accessibility
5. Prometheus availability
6. Grafana availability
7. Marquez and OpenLineage availability
8. runtime log sanity

## 1. Docker Runtime Availability

Checks:

- Docker Desktop service is running
- Docker CLI can reach the configured engine
- the Data-Lab runtime container is visible in `docker ps`

Evidence to capture:

- running container name
- container status
- exposed ports or documented internal access pattern

## 2. Airflow Reachability

Checks:

- `AIRFLOW_BASE_URL` loads in the browser
- login or home page responds successfully
- no obvious webserver startup errors are present in logs

Success criteria:

- Airflow UI is accessible
- Airflow can authenticate with the configured metadata backend

## 3. PostgreSQL Metadata Availability

Checks:

- the configured `POSTGRES_HOST:POSTGRES_PORT` is reachable
- authentication succeeds with locally supplied credentials
- the intended metadata database exists

Success criteria:

- Airflow metadata storage is available
- no repeated database connection failures appear in runtime logs

## 4. MinIO Accessibility

Checks:

- `MINIO_ENDPOINT` or `DATALAB_MINIO_ENDPOINT(_OUTSIDE)` is reachable
- the MinIO console loads if exposed
- the default FraudLens bucket can be listed or created according to local permissions

Common Data-Lab mapping:

- inside container endpoint: `http://localhost:9004`
- host endpoint: `http://localhost:9009`
- console on host: `http://localhost:9010`

Success criteria:

- object storage endpoint responds
- FraudLens has a known landing bucket for future raw data work

## 5. Prometheus Availability

Checks:

- `PROMETHEUS_BASE_URL` loads
- the targets view shows healthy targets where configured

Success criteria:

- metrics are queryable
- no broad scrape-failure condition is visible

## 6. Grafana Availability

Checks:

- `GRAFANA_BASE_URL` loads
- Grafana login is reachable
- Prometheus datasource is configured or planned as the primary datasource

Success criteria:

- dashboard UI is accessible
- Grafana can connect to Prometheus

## 7. Marquez And OpenLineage Availability

Checks:

- `MARQUEZ_BASE_URL` responds
- the Marquez health/admin endpoint responds if exposed
- the `OPENLINEAGE_URL` points to the Marquez lineage ingestion API or the configured lineage receiver

Success criteria:

- lineage UI or API is reachable
- the lineage endpoint is ready for future Airflow/dbt emitters

## 8. No Critical Errors In Logs

Review the active runtime logs and look for repeated fatal or restart-loop conditions in:

- Airflow startup
- metadata database connection
- MinIO startup
- Prometheus scraping
- Grafana datasource startup
- Marquez API or backing database startup

Acceptable condition:

- warnings may exist, but there are no recurring fatal errors that prevent the required services from being functional

## Minimum Evidence For Definition Of Done

- Docker runtime reachable
- Airflow UI accessible
- PostgreSQL metadata dependency reachable
- MinIO accessible
- Prometheus and Grafana accessible
- Marquez or OpenLineage endpoint accessible
- no critical recurring runtime errors observed

## Follow-Up If A Check Fails

- compare the local setup to the upstream Data-Lab repository instructions
- verify local `.env` values against FraudLens `.env.example`
- confirm whether the missing service is already part of Data-Lab or still needs to be added to the external runtime
- record the failure under the relevant Phase 1 sub-issue instead of changing FraudLens to silently work around it

If the capability exists inside the single container but is not exposed on the expected default port, document the actual local access pattern and keep the logical capability name unchanged.
