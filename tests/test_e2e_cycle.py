import pytest

from swarm.config import Settings
from swarm.models import Opportunity, ScoreCard, WorkProduct, VerificationResult
from swarm.orchestrator import EarningSwarm


class FakeSource:
    async def search(self, query):
        return [
            Opportunity(
                id="smoke-opportunity-1",
                title="Paid competitor research task",
                url="https://example.com/jobs/competitor-research",
                summary="Buyer requests a concise five-competitor comparison for EUR 120.",
                query=query,
            )
        ]

    async def ping(self):
        return True


class FakeAnalyst:
    async def score(self, opportunity):
        return ScoreCard(
            opportunity_id=opportunity.id,
            strategy="research_intelligence",
            fit=0.95,
            win_probability=0.80,
            expected_revenue_eur=120,
            expected_hours=2,
            cash_cost_eur=0,
            risk=0.05,
            confidence=0.90,
            reasons=["Strong scope match and explicit paid task."],
        )


class FakeWorker:
    def __init__(self):
        self.calls = 0

    async def build(self, opportunity, score, critique=None):
        self.calls += 1
        repaired = bool(critique)
        proposal = (
            "I will compare five named competitors using only verifiable public sources and provide a concise report."
            if repaired
            else "I already know your market is dominated by five competitors and can prove it immediately."
        )
        deliverable = (
            "Repaired sample: evidence table with source URL, observed price, feature and date checked."
            if repaired
            else "Initial sample contains an unsupported market-dominance claim."
        )
        return WorkProduct(
            opportunity_id=opportunity.id,
            strategy=score.strategy,
            title="Five-competitor research report",
            proposal=proposal,
            draft_deliverable=deliverable,
            price_eur=60,
            estimated_hours=2,
            assumptions=[],
            sources=[],
        )


class FakeVerifier:
    def __init__(self):
        self.calls = 0

    async def verify(self, opportunity, work):
        self.calls += 1
        if self.calls == 1:
            return VerificationResult(
                passed=False,
                score=0.55,
                issues=["Proposal claims market dominance without evidence."],
                fixes_required=["Remove unsupported claim and promise only verifiable research."],
            )
        return VerificationResult(passed=True, score=0.97, issues=[], fixes_required=[])


@pytest.mark.asyncio
async def test_full_cycle_repairs_verifies_publishes_and_remembers(tmp_path):
    settings = Settings(
        db_path=str(tmp_path / "swarm.db"),
        outbox=str(tmp_path / "outbox"),
        max_new=3,
        max_work=1,
        min_utility=0.40,
        min_verify=0.80,
        max_repairs=2,
        max_cash_action=0,
        max_cash_day=0,
        min_price=20,
        n8n_url="",
        n8n_secret="",
    )
    swarm = EarningSwarm(settings)
    swarm.source = FakeSource()
    swarm.analyst = FakeAnalyst()
    worker = FakeWorker()
    verifier = FakeVerifier()
    swarm.worker = worker
    swarm.verifier = verifier

    result = await swarm.cycle()

    assert result["discovered"] == 1
    assert len(result["published"]) == 1
    assert result["published"][0]["id"] == "smoke-opportunity-1"
    assert worker.calls == 2, "first rejected draft should be repaired exactly once"
    assert verifier.calls == 2

    outbox_file = tmp_path / "outbox" / "smoke-opportunity-1.md"
    assert outbox_file.exists()
    text = outbox_file.read_text(encoding="utf-8")
    assert "Repaired sample" in text
    assert "unsupported market-dominance claim" not in text
    assert "Price: €60.00" in text

    counts = swarm.db.counts()
    assert counts.get("published") == 1
    events = swarm.db.recent_events(5)
    assert any(e["kind"] == "cycle" for e in events)
