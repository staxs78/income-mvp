from __future__ import annotations
import argparse, asyncio, json
from .config import Settings
from .db import Database
from .models import Outcome
from .orchestrator import EarningSwarm

def parser():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='cmd',required=True)
    for x in ['doctor','once','daemon','status']: sp.add_parser(x)
    r=sp.add_parser('record'); r.add_argument('opportunity_id'); r.add_argument('strategy'); r.add_argument('result',choices=['won','lost','ignored','paid','refunded']); r.add_argument('--revenue',type=float,default=0); r.add_argument('--cost',type=float,default=0); r.add_argument('--notes',default='')
    return p
async def amain(a):
    s=Settings()
    if a.cmd in {'doctor','once','daemon'}:
        sw=EarningSwarm(s)
        if a.cmd=='doctor': print(json.dumps(await sw.doctor(),indent=2))
        elif a.cmd=='once': print(json.dumps(await sw.cycle(),indent=2))
        else: await sw.run_forever()
        return
    db=Database(s.db_path)
    if a.cmd=='status': print(json.dumps({'counts':db.counts(),'strategy_stats':db.strategy_stats(),'events':db.recent_events()},indent=2))
    else: db.record_outcome(Outcome(opportunity_id=a.opportunity_id,strategy=a.strategy,result=a.result,revenue_eur=a.revenue,cost_eur=a.cost,notes=a.notes)); print('recorded')
def main(): asyncio.run(amain(parser().parse_args()))
