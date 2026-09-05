from __future__ import annotations
import json, re
import httpx
from pydantic import BaseModel

class LLMError(RuntimeError): pass
class LLM:
    def __init__(self,base_url,api_key,model): self.base=base_url.rstrip('/'); self.key=api_key; self.model=model
    async def text(self,system,user,temperature=.2):
        payload={'model':self.model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'temperature':temperature}
        try:
            async with httpx.AsyncClient(timeout=90) as c:
                r=await c.post(self.base+'/chat/completions',headers={'Authorization':f'Bearer {self.key}'},json=payload); r.raise_for_status(); return r.json()['choices'][0]['message']['content']
        except Exception as e: raise LLMError(str(e)) from e
    async def structured(self,system,user,schema:type[BaseModel],temperature=.1):
        prompt=user+'\nReturn ONLY valid JSON matching this schema:\n'+json.dumps(schema.model_json_schema())
        raw=await self.text(system,prompt,temperature)
        m=re.search(r'\{.*\}',raw,re.S)
        if not m: raise LLMError('No JSON object in model response')
        try: return schema.model_validate_json(m.group(0))
        except Exception as e: raise LLMError(f'Invalid structured output: {e}') from e
    async def ping(self):
        try: return bool(await self.text('Reply exactly OK','health check',0))
        except LLMError: return False
