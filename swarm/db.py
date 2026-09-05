from __future__ import annotations
import sqlite3, json
from datetime import datetime, timezone
from pathlib import Path
from .models import Opportunity, Outcome

class Database:
    def __init__(self, path:str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.c=sqlite3.connect(path)
        self.c.row_factory=sqlite3.Row
        self.c.executescript('''
        create table if not exists opportunities(id text primary key,title text,url text,summary text,query text,status text default 'new',created_at text);
        create table if not exists outcomes(id integer primary key autoincrement,opportunity_id text,strategy text,result text,revenue real,cost real,notes text,created_at text);
        create table if not exists events(id integer primary key autoincrement,kind text,payload text,created_at text);
        ''')
        self.c.commit()
    def add_opportunity(self,o:Opportunity)->bool:
        cur=self.c.execute('insert or ignore into opportunities(id,title,url,summary,query,created_at) values(?,?,?,?,?,?)',(o.id,o.title,o.url,o.summary,o.query,self.now()))
        self.c.commit(); return cur.rowcount>0
    def set_status(self,oid,status): self.c.execute('update opportunities set status=? where id=?',(status,oid)); self.c.commit()
    def record_outcome(self,o:Outcome):
        self.c.execute('insert into outcomes(opportunity_id,strategy,result,revenue,cost,notes,created_at) values(?,?,?,?,?,?,?)',(o.opportunity_id,o.strategy,o.result,o.revenue_eur,o.cost_eur,o.notes,self.now())); self.c.commit()
    def strategy_stats(self):
        rows=self.c.execute("select strategy,count(*) n,sum(case when result in ('won','paid') then 1 else 0 end) wins,coalesce(sum(revenue-cost),0) profit from outcomes group by strategy").fetchall()
        return {r['strategy']:dict(r) for r in rows}
    def event(self,kind,payload): self.c.execute('insert into events(kind,payload,created_at) values(?,?,?)',(kind,json.dumps(payload,ensure_ascii=False),self.now())); self.c.commit()
    def recent_events(self,limit=20): return [dict(r) for r in self.c.execute('select * from events order by id desc limit ?',(limit,)).fetchall()]
    def counts(self): return {r['status']:r['n'] for r in self.c.execute('select status,count(*) n from opportunities group by status')}
    @staticmethod
    def now(): return datetime.now(timezone.utc).isoformat()
