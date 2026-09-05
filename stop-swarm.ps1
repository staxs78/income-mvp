$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
docker compose stop earning-swarm
Write-Host 'Earning swarm stopped. SQLite memory and outbox were preserved.'
