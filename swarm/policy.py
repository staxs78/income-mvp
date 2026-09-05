from __future__ import annotations
from dataclasses import dataclass
from .models import ScoreCard, WorkProduct
@dataclass
class Policy:
    max_cash_action: float=0
    max_cash_day: float=0
    min_price: float=20
    def score_allowed(self,s:ScoreCard)->tuple[bool,str]:
        if s.cash_cost_eur>self.max_cash_action: return False,'cash limit'
        if s.risk>.72: return False,'risk too high'
        return True,'ok'
    def work_allowed(self,w:WorkProduct)->tuple[bool,str]:
        if w.price_eur<self.min_price: return False,'below minimum price'
        return True,'ok'
