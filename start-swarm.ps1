$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

Write-Host '=== Persistent Earning Swarm launcher ==='

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker command not found. Install/start Docker Desktop first.'
}

docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop is installed but its engine is not running.' }

try {
    $models = Invoke-RestMethod -Uri 'http://127.0.0.1:1234/v1/models' -Method Get -TimeoutSec 5
} catch {
    throw 'LM Studio server is not reachable at http://127.0.0.1:1234. Load a model and start the Local Server first.'
}

$modelId = $models.data | Select-Object -First 1 -ExpandProperty id
if (-not $modelId) { throw 'LM Studio responded but no loaded model was found.' }
Write-Host "Using LM Studio model: $modelId"

if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
$envText = Get-Content '.env' -Raw
if ($envText -match '(?m)^LLM_MODEL=') {
    $envText = [regex]::Replace($envText, '(?m)^LLM_MODEL=.*$', "LLM_MODEL=$modelId")
} else {
    $envText += "`nLLM_MODEL=$modelId`n"
}
Set-Content '.env' $envText -Encoding utf8

Write-Host 'Starting local search...'
docker compose up -d searxng

Write-Host 'Building earning swarm...'
docker compose build earning-swarm

Write-Host 'Running health check...'
docker compose run --rm earning-swarm python -m swarm doctor
if ($LASTEXITCODE -ne 0) { throw 'Health check failed.' }

Write-Host 'Running one earning cycle...'
docker compose run --rm earning-swarm python -m swarm once
if ($LASTEXITCODE -ne 0) { throw 'First cycle failed.' }

Write-Host 'Starting persistent daemon...'
docker compose up -d earning-swarm

Write-Host ''
Write-Host 'SWARM IS RUNNING.'
Write-Host 'Outbox: .\outbox'
Write-Host 'Status: docker compose exec earning-swarm python -m swarm status'
Write-Host 'Logs:   docker compose logs -f earning-swarm'
Write-Host 'Stop:   .\stop-swarm.ps1'
