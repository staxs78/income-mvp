from __future__ import annotations
import os, yaml
from dataclasses import dataclass
from .models import Strategy

def _f(name, default):
    try: return float(os.getenv(name, default))
    except ValueError: return float(default)
def _i(name, default):
    try: return int(os.getenv(name, default))
    except ValueError: return int(default)

@dataclass
class Settings:
    llm_base_url: str = os.getenv('LLM_BASE_URL','http://host.docker.internal:1234/v1')
    llm_api_key: str = os.getenv('LLM_API_KEY','lm-studio')
    llm_model: str = os.getenv('LLM_MODEL','local-model')
    searxng_url: str = os.getenv('SEARXNG_URL','http://searxng:8080')
    search_language: str = os.getenv('SEARCH_LANGUAGE','en')
    search_results: int = _i('SEARCH_RESULTS_PER_QUERY',8)
    db_path: str = os.getenv('SWARM_DB','data/swarm.db')
    outbox: str = os.getenv('SWARM_OUTBOX','outbox')
    cycle_seconds: int = _i('CYCLE_SECONDS',900)
    max_new: int = _i('MAX_NEW_OPPORTUNITIES_PER_CYCLE',30)
    max_work: int = _i('MAX_WORK_ITEMS_PER_CYCLE',4)
    min_utility: float = _f('MIN_UTILITY',.48)
    min_verify: float = _f('MIN_VERIFICATION_SCORE',.80)
    max_repairs: int = _i('MAX_REPAIR_ATTEMPTS',2)
    max_cash_action: float = _f('MAX_CASH_SPEND_PER_ACTION_EUR',0)
    max_cash_day: float = _f('MAX_CASH_SPEND_PER_DAY_EUR',0)
    min_price: float = _f('MIN_PRICE_EUR',20)
    n8n_url: str = os.getenv('N8N_WEBHOOK_URL','')
    n8n_secret: str = os.getenv('N8N_WEBHOOK_SECRET','')

def load_strategies(path='config/strategies.yml') -> list[Strategy]:
    with open(path, encoding='utf-8') as f:
        data=yaml.safe_load(f)
    return [Strategy(**x) for x in data['strategies']]
