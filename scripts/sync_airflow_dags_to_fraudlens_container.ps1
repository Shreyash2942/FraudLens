param(
    [string]$ContainerName = "fraudlens",
    [string]$DagsSourceDir = "airflow/dags",
    [string]$ContainerDagsDir = "/home/datalab/airflow/dags"
)

$ErrorActionPreference = "Stop"

Write-Host "Syncing DAGs from '$DagsSourceDir' to container '${ContainerName}:$ContainerDagsDir'..."

$existing = docker ps --format "{{.Names}}" | Select-String -Pattern "^$ContainerName$"
if (-not $existing) {
    throw "Container '$ContainerName' is not running."
}

# Ensure target folder exists
docker exec $ContainerName sh -lc "mkdir -p $ContainerDagsDir"

# Copy only DAG python files
Get-ChildItem -Path $DagsSourceDir -Filter *.py | ForEach-Object {
    $src = $_.FullName
    $dst = "${ContainerName}:${ContainerDagsDir}/$($_.Name)"
    docker cp $src $dst
}

# Set ownership and list imported DAGs/errors
docker exec $ContainerName sh -lc "chown -R datalab:datalab $ContainerDagsDir"
docker exec $ContainerName sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list | sed -n '1,120p'"
docker exec $ContainerName sh -lc "export FRAUDLENS_REPO_ROOT=/home/datalab/fraudlens; airflow dags list-import-errors || true"

Write-Host "DAG sync complete."
