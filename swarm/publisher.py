from __future__ import annotations
from pathlib import Path
import httpx
class Publisher:
    def __init__(self,outbox,n8n_url='',secret=''): self.out=Path(outbox); self.out.mkdir(parents=True,exist_ok=True); self.url=n8n_url; self.secret=secret
    async def publish(self,o,s,w,v):
        payload={'opportunity':o.model_dump(),'score':s.model_dump(),'work':w.model_dump(),'verification':v.model_dump()}
        path=self.out/f'{o.id}.md'
        path.write_text(f"# {w.title}\n\nSource: {o.url}\n\n## Proposal\n{w.proposal}\n\n## Draft deliverable\n{w.draft_deliverable}\n\nPrice: €{w.price_eur:.2f}\n",encoding='utf-8')
        if self.url:
            headers={'X-Swarm-Secret':self.secret} if self.secret else {}
            async with httpx.AsyncClient(timeout=30) as c:
                r=await c.post(self.url,json=payload,headers=headers); r.raise_for_status()
        return str(path)
