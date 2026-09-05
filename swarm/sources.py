from __future__ import annotations
import hashlib
from urllib.parse import urlparse
import httpx
from .models import Opportunity

class SearxSource:
    def __init__(self,base_url,language='en',limit=8): self.base=base_url.rstrip('/'); self.lang=language; self.limit=limit
    async def search(self,query):
        async with httpx.AsyncClient(timeout=30,follow_redirects=True) as c:
            r=await c.get(self.base+'/search',params={'q':query,'format':'json','language':self.lang}); r.raise_for_status(); data=r.json()
        out=[]
        for x in data.get('results',[])[:self.limit]:
            url=x.get('url',''); title=x.get('title','').strip(); summary=x.get('content','').strip()
            if not url or not title: continue
            oid=hashlib.sha256(url.encode()).hexdigest()[:20]
            out.append(Opportunity(id=oid,title=title,url=url,summary=summary,query=query))
        return out
    async def ping(self):
        try: return bool(await self.search('paid freelance research'))
        except Exception: return False

def allowed_public_url(url):
    p=urlparse(url)
    return p.scheme in {'http','https'} and bool(p.netloc)
