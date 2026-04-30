# FraudLens Phase 1 Platform Foundation Guide

## Purpose

Phase 1 establishes how FraudLens connects to a reproducible local platform runtime without recreating that runtime inside this repository.

FraudLens treats the following repository as the canonical runtime source for local platform services:

- `https://github.com/Shreyash2942/Data-Lab.git`

## Runtime Strategy

- Data-Lab remains the Docker/runtime project
- FraudLens remains the project that defines business domains, platform expectations, and downstream data engineering work
- Phase 1 in FraudLens is integration-and-documentation focused
- No Docker Compose files, DAGs, dbt configs, SQL, or executable health-check scripts are added here in this phase
- a single all-in-one local container is acceptable for this project as long as the logical platform capabilities remain documented clearly

## Portfolio Positioning

- Snowflake is still the intended analytical target for the project
- Data-Lab is the practical local sandbox used for development and cost control
- Spark and Hive can be used behind the scenes to replicate selected warehouse behavior before spending money on real Snowflake runs
- this is a professional portfolio project, not a claim of production deployment parity

## What Data-Lab Provides

The public Data-Lab README currently describes:

- a single-container data engineering sandbox
- Airflow on `http://localhost:8080/`
- PostgreSQL on `localhost:5432`

FraudLens uses that runtime as its local platform anchor. FraudLens also expects the broader platform capability set below, whether those capabilities are already exposed by Data-Lab today or represented inside the all-in-one runtime in a less isolated way.

The URLs and ports below are the expected FraudLens-side defaults for local integration. If your Data-Lab runtime exposes different ports, update your local `.env` without changing the documented service roles.

## Required Platform Capabilities

The list below describes logical capabilities FraudLens depends on. They do not need to be packaged as separate containers for this project.

### Airflow

- Role: orchestration entry point for future ingestion, transformation, quality, and lineage workflows
- Expected base URL: `http://localhost:8080`
- Expected health signal: login page or Airflow UI loads successfully
- Future FraudLens dependency: DAG execution, operator configuration, connection management

### PostgreSQL

- Role: metadata backend for Airflow and supporting metadata persistence
- Expected endpoint: `localhost:5432`
- Expected health signal: TCP connectivity and successful authentication with the configured database
- Future FraudLens dependency: Airflow metadata, possibly Marquez backing metadata depending on runtime implementation

### MinIO

- Role: object landing zone for synthetic data, raw extracts, and intermediate exchange assets
- Expected API endpoint: `http://localhost:9000`
- Expected console endpoint: `http://localhost:9001`
- Expected health signal: console loads and a configured FraudLens bucket is accessible
- Future FraudLens dependency: raw zone, staged files, dataset exchange, landing-to-warehouse patterns
- Default bucket convention: `fraudlensdata` for initial raw-zone landing, with future expansion for curated or transient buckets as later phases require

### Prometheus

- Role: metrics collection and scrape aggregation
- Expected base URL: `http://localhost:9090`
- Expected health signal: Prometheus UI loads and configured targets report healthy
- Future FraudLens dependency: platform health metrics, service-level observability, pipeline monitoring

### Grafana

- Role: dashboarding and operational visualization on top of Prometheus metrics
- Expected base URL: `http://localhost:3000`
- Expected health signal: Grafana UI loads and Prometheus datasource is configured
- Future FraudLens dependency: dashboards for pipeline runs, failures, latency, and service health
- Expected initial dashboard scope: service availability, scrape health, pipeline run status, failure count, and runtime latency

### Marquez

- Role: lineage backend and lineage UI
- Expected web URL: `http://localhost:3003`
- Expected API endpoint: `http://localhost:5000`
- Expected admin/health endpoint: `http://localhost:5001`
- Expected health signal: UI or health endpoint responds successfully
- Future FraudLens dependency: visibility into job, run, and dataset lineage

### OpenLineage

- Role: lineage event protocol used by Airflow and later dbt integrations
- Expected ingestion endpoint: `http://localhost:5000`
- Expected health signal: Marquez API is reachable and accepts lineage traffic once configured
- Future FraudLens dependency: emitting lineage from orchestration and transformation workloads

## Startup Prerequisites

- Docker Desktop installed
- Docker Desktop service running on the local machine
- access to the `Shreyash2942/Data-Lab` repository
- local `.env` created from FraudLens `.env.example`
- local credentials supplied outside source control

## Runtime Startup Reference

Use the Data-Lab repository as the source of truth for runtime startup. At the time this guide was written, the upstream README documents a compose-based quick start similar to:

```powershell
cp datalabcontainer/.env.example datalabcontainer/.env
cd datalabcontainer
docker compose build
docker compose up -d
docker compose exec data-lab bash
su - datalab
```

FraudLens does not mirror those files. Developers should follow the upstream Data-Lab runtime instructions directly.

## Dependency Order

The expected dependency order for FraudLens is:

1. Docker runtime available
2. Data-Lab runtime container started
3. PostgreSQL reachable
4. Airflow reachable and backed by metadata storage
5. MinIO reachable for object storage
6. Prometheus scraping targets successfully
7. Grafana connected to Prometheus
8. Marquez reachable
9. OpenLineage endpoint configured for future emitters

## FraudLens Workstream Mapping

### #22 Setup Docker Environment

- treat Data-Lab as the canonical runtime source
- do not add local Compose duplication in FraudLens
- document startup prerequisites and external runtime reference

### #23 Configure Airflow & Metadata Database

- document Airflow access and the metadata database dependency
- define the FraudLens environment variable contract for later Airflow work

### #24 Setup Object Storage (MinIO)

- define MinIO endpoint expectations
- standardize the default FraudLens bucket naming pattern

### #25 Implement Monitoring (Prometheus + Grafana)

- define the monitoring service pair and expected dashboard posture
- document datasource dependency from Grafana to Prometheus

### #26 Setup Lineage Tracking (Marquez + OpenLineage)

- define Marquez and OpenLineage endpoints
- document how later Airflow/dbt integrations should emit lineage

### #27 Validate Platform & Service Connectivity

- use the validation runbook in `documents/platform-validation-runbook.md`
- confirm reachability, health, and log sanity

### #28 Document Platform Setup

- use this guide, `platform/service-inventory.yaml`, `platform/connectivity-matrix.md`, and `platform/local-setup.md` as the Phase 1 documentation baseline

## Notes On Current Runtime Shape

Your current local runtime is described as one actual container rather than multiple service containers. That is acceptable for this project.

FraudLens documents separate platform capabilities because:

- later phases still need stable interfaces and connection targets
- the logical architecture should stay understandable even if the local packaging is simplified
- the portfolio story is stronger when the target architecture and the local cost-saving runtime are both explained clearly
