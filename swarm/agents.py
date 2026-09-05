from __future__ import annotations
import math
from pydantic import BaseModel, Field
from .models import ScoreCard, WorkProduct, VerificationResult, Strategy
from .llm import LLM, LLMError

class ScoreDraft(BaseModel):
    strategy:str; fit:float=Field(ge=0,le=1); win_probability:float=Field(ge=0,le=1); expected_revenue_eur:float=Field(ge=0); expected_hours:float=Field(gt=0); cash_cost_eur:float=Field(ge=0); risk:float=Field(ge=0,le=1); confidence:float=Field(ge=0,le=1); reasons:list[str]=[]
class WorkDraft(BaseModel):
    title:str; proposal:str; draft_deliverable:str; price_eur:float=Field(ge=0); estimated_hours:float=Field(gt=0); assumptions:list[str]=[]; sources:list[str]=[]
class VerifyDraft(BaseModel):
    passed:bool; score:float=Field(ge=0,le=1); issues:list[str]=[]; fixes_required:list[str]=[]

class Analyst:
    def __init__(self,llm:LLM,strategies:list[Strategy]): self.llm=llm; self.strategies=strategies
    async def score(self,o):
        st='\n'.join(f'- {s.name}: {s.description}; min €{s.min_price_eur}; max {s.max_hours}h' for s in self.strategies)
        try:
            d=await self.llm.structured('Score earning opportunities conservatively. Never invent buyer budget, credentials or facts. Reject scams, unpaid speculation and unclear legality/permission.',f'Opportunity: {o.model_dump_json()}\nStrategies:\n{st}\nPick one.',ScoreDraft)
            return ScoreCard(opportunity_id=o.id,**d.model_dump())
        except LLMError:
            text=(o.title+' '+o.summary).lower(); best=max(self.strategies,key=lambda s:sum(k.lower() in text for k in s.keywords)); hits=sum(k.lower() in text for k in best.keywords)
            return ScoreCard(opportunity_id=o.id,strategy=best.name,fit=min(.35+.1*hits,.75),win_probability=.12 if hits else .04,expected_revenue_eur=best.min_price_eur,expected_hours=min(best.max_hours,3),cash_cost_eur=0,risk=.4,confidence=.22,reasons=['LLM unavailable: conservative keyword fallback'])

class Worker:
    def __init__(self,llm:LLM,strategies:dict[str,Strategy],min_price:float): self.llm=llm; self.strategies=strategies; self.min_price=min_price
    async def build(self,o,s,critique=None):
        strategy=self.strategies[s.strategy]; repair='\nFix these findings:\n'+'\n'.join(critique or []) if critique else ''
        d=await self.llm.structured('Produce honest, useful work. Never invent credentials, completed work, sources, facts or customer history. Keep scope small and concrete.',f'Opportunity: {o.model_dump_json()}\nStrategy: {strategy.model_dump_json()}\nScore:{s.model_dump_json()}\n{repair}\nDraft a proposal and real sample/deliverable.',WorkDraft,.25)
        d.price_eur=max(d.price_eur,strategy.min_price_eur,self.min_price); d.estimated_hours=min(d.estimated_hours,strategy.max_hours)
        return WorkProduct(opportunity_id=o.id,strategy=s.strategy,**d.model_dump())

class Verifier:
    def __init__(self,llm): self.llm=llm
    async def verify(self,o,p):
        d=await self.llm.structured('Act as an adversarial verifier. Fail fabricated claims, fake credentials, unsupported facts, deceptive completion claims or risky/unclear actions.',f'Opportunity:{o.model_dump_json()}\nWork:{p.model_dump_json()}\nAudit factual integrity and realistic scope.',VerifyDraft,0)
        return VerificationResult(**d.model_dump())

class StrategySelector:
    def __init__(self,db,strategies): self.db=db; self.strategies=strategies
    def ordered_queries(self):
        stats=self.db.strategy_stats(); total=1+sum(v['n'] for v in stats.values()); arr=[]
        for s in self.strategies:
            st=stats.get(s.name,{'n':0,'profit':0}); n=st['n']; reward=max(-1,min(st['profit']/max(n,1)/100,2)); explore=math.sqrt(2*math.log(total+1)/(n+1))
            for q in s.queries: arr.append((reward+explore,s.name,q))
        arr.sort(reverse=True); return [(s,q) for _,s,q in arr]
