# Persistent Earning Swarm v0.1

A local-first agent loop optimized for **real net income**, not activity:

`discover -> score -> produce -> adversarially verify -> repair -> publish -> learn from real outcomes -> repeat`

State lives in SQLite. Search is local SearXNG. Reasoning defaults to LM Studio through its OpenAI-compatible API. Verified work lands in `outbox/` and can optionally be POSTed to n8n for platform-specific permitted actions.

## Start

1. Load a capable instruct model in LM Studio and start the local server.
2. `cp .env.example .env` and set `LLM_MODEL` to the model id shown by LM Studio.
3. `docker compose up -d searxng`
4. `docker compose run --rm earning-swarm python -m swarm doctor`
5. `docker compose run --rm earning-swarm python -m swarm once`
6. Inspect `outbox/`, then `docker compose up -d` for persistent operation.

## Teach it with money

`docker compose exec earning-swarm python -m swarm record <opportunity_id> <strategy> paid --revenue 50`

or

`docker compose exec earning-swarm python -m swarm record <opportunity_id> <strategy> lost`

Strategy allocation uses actual profit and an exploration bonus, so winning strategies get more search while untested ones are not starved.

## Default authority envelope

The default spend limit is €0. The daemon can search, score, draft, verify, repair, publish locally, and send verified payloads to a configured n8n webhook. Credentials stay outside the repo. Platform-specific actions should use permitted APIs/flows and the system must not fabricate qualifications, identity, results, or completed work.

## Kill switch

`docker compose stop earning-swarm`
