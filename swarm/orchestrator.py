from __future__ import annotations
import asyncio, random
from .config import Settings, load_strategies
from .db import Database
from .llm import LLM, LLMError
from .sources import SearxSource, allowed_public_url
from .agents import Analyst, Worker, Verifier, StrategySelector
from .policy import Policy
from .publisher import Publisher

class EarningSwarm:
    def __init__(self,s:Settings):
        self.s=s; self.db=Database(s.db_path); self.strategies=load_strategies(); sm={x.name:x for x in self.strategies}
        self.llm=LLM(s.llm_base_url,s.llm_api_key,s.llm_model); self.source=SearxSource(s.searxng_url,s.search_language,s.search_results)
        self.analyst=Analyst(self.llm,self.strategies); self.worker=Worker(self.llm,sm,s.min_price); self.verifier=Verifier(self.llm); self.selector=StrategySelector(self.db,self.strategies)
        self.policy=Policy(s.max_cash_action,s.max_cash_day,s.min_price); self.publisher=Publisher(s.outbox,s.n8n_url,s.n8n_secret)
    async def doctor(self): return {'db':True,'llm':await self.llm.ping(),'search':await self.source.ping()}
    async def cycle(self):
        found=[]
        for strategy,q in self.selector.ordered_queries():
            if len(found)>=self.s.max_new: break
            try: items=await self.source.search(q)
            except Exception as e: self.db.event('search_error',{'query':q,'error':str(e)}); continue
            for o in items:
                if allowed_public_url(o.url) and self.db.add_opportunity(o): found.append(o)
                if len(found)>=self.s.max_new: break
        published=[]
        for o in found[:self.s.max_work]:
            score=await self.analyst.score(o); ok,_=self.policy.score_allowed(score)
            if not ok or score.utility<self.s.min_utility: self.db.set_status(o.id,'rejected'); continue
            try: work=await self.worker.build(o,score)
            except LLMError as e: self.db.event('worker_error',{'id':o.id,'error':str(e)}); continue
            vr=None
            for _ in range(self.s.max_repairs+1):
                try: vr=await self.verifier.verify(o,work)
                except LLMError as e: self.db.event('verify_error',{'id':o.id,'error':str(e)}); break
                if vr.passed and vr.score>=self.s.min_verify: break
                try: work=await self.worker.build(o,score,vr.fixes_required+vr.issues)
                except LLMError: break
            if not vr or not vr.passed or vr.score<self.s.min_verify: self.db.set_status(o.id,'failed_verification'); continue
            ok,_=self.policy.work_allowed(work)
            if not ok: self.db.set_status(o.id,'rejected'); continue
            path=await self.publisher.publish(o,score,work,vr); self.db.set_status(o.id,'published'); published.append({'id':o.id,'path':path,'utility':score.utility})
        result={'discovered':len(found),'published':published}; self.db.event('cycle',result); return result
    async def run_forever(self):
        failures=0
        while True:
            try: await self.cycle(); failures=0; await asyncio.sleep(self.s.cycle_seconds)
            except asyncio.CancelledError: raise
            except Exception as e:
                failures+=1; self.db.event('cycle_crash',{'error':str(e),'failures':failures}); await asyncio.sleep(min(self.s.cycle_seconds,30*(2**min(failures,5)))+random.random()*5)
