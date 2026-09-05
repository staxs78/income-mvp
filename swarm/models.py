from __future__ import annotations
from pydantic import BaseModel, Field

class Strategy(BaseModel):
    name: str
    description: str
    keywords: list[str] = []
    min_price_eur: float = 20
    max_hours: float = 5
    queries: list[str] = []

class Opportunity(BaseModel):
    id: str
    title: str
    url: str
    summary: str = ""
    query: str = ""

class ScoreCard(BaseModel):
    opportunity_id: str
    strategy: str
    fit: float = Field(ge=0, le=1)
    win_probability: float = Field(ge=0, le=1)
    expected_revenue_eur: float = Field(ge=0)
    expected_hours: float = Field(gt=0)
    cash_cost_eur: float = Field(ge=0)
    risk: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    reasons: list[str] = []

    @property
    def utility(self) -> float:
        hourly = self.expected_revenue_eur / max(self.expected_hours, .25)
        return max(0.0, min(1.0, self.fit * self.win_probability * self.confidence * (hourly / 25) * (1-self.risk)))

class WorkProduct(BaseModel):
    opportunity_id: str
    strategy: str
    title: str
    proposal: str
    draft_deliverable: str
    price_eur: float
    estimated_hours: float
    assumptions: list[str] = []
    sources: list[str] = []

class VerificationResult(BaseModel):
    passed: bool
    score: float = Field(ge=0, le=1)
    issues: list[str] = []
    fixes_required: list[str] = []

class Outcome(BaseModel):
    opportunity_id: str
    strategy: str
    result: str
    revenue_eur: float = 0
    cost_eur: float = 0
    notes: str = ""
