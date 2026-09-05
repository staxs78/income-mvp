# Architecture

- **Strategy selector** uses profit-aware exploration/exploitation.
- **Scout** searches through SearXNG and deduplicates by URL hash.
- **Analyst** estimates fit, win chance, revenue, time, cost, risk and confidence. If the LLM is unavailable it falls back conservatively.
- **Worker** drafts a concrete proposal and sample/deliverable.
- **Verifier** is adversarial and rejects fabricated or unsupported work.
- **Repair loop** retries verifier findings up to a configured limit.
- **Publisher** writes verified items to the outbox and optionally sends them to n8n.
- **SQLite memory** records opportunities, events and actual paid/lost/refunded outcomes.
- **Daemon** persists through transient failures with exponential backoff.
