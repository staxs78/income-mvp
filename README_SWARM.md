# Persistent Earning Swarm v0.1

A local-first agent loop optimized for **real net income**, not activity:

`discover -> score -> produce -> adversarially verify -> repair -> publish -> learn from real outcomes -> repeat`

State lives in SQLite. Search is local SearXNG. Reasoning defaults to LM Studio through its OpenAI-compatible API. Verified work lands in `outbox/` and can optionally be POSTed to n8n for platform-specific permitted actions.

## Windows activation

Load a capable instruct model in LM Studio and start its Local Server. Make sure Docker Desktop is running. Then from PowerShell in this repository run:

```powershell
.\start-swarm.ps1
```

The launcher auto-detects the loaded LM Studio model, creates `.env`, starts SearXNG, builds the swarm, runs a health check, runs one complete earning cycle, and then starts the persistent daemon.

Useful commands:

```powershell
docker compose logs -f earning-swarm
docker compose exec earning-swarm python -m swarm status
.\stop-swarm.ps1
```

## Teach it with money

```powershell
docker compose exec earning-swarm python -m swarm record <opportunity_id> <strategy> paid --revenue 50
docker compose exec earning-swarm python -m swarm record <opportunity_id> <strategy> lost
```

Strategy allocation uses actual profit and an exploration bonus, so winning strategies get more search while untested ones are not starved.

## Default authority envelope

The default spend limit is €0. The daemon can search, score, draft, verify, repair, publish locally, and send verified payloads to a configured n8n webhook. Credentials stay outside the repo. Platform-specific actions should use permitted APIs/flows and the system must not fabricate qualifications, identity, results, or completed work.

## Kill switch

```powershell
.\stop-swarm.ps1
```
