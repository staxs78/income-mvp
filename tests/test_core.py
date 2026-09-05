from swarm.models import ScoreCard, WorkProduct
from swarm.policy import Policy
from swarm.db import Database
from swarm.models import Outcome

def test_utility_bounds():
    s=ScoreCard(opportunity_id='x',strategy='a',fit=.8,win_probability=.5,expected_revenue_eur=100,expected_hours=2,cash_cost_eur=0,risk=.1,confidence=.8)
    assert 0<=s.utility<=1

def test_policy_cash_and_price():
    p=Policy(0,0,20)
    s=ScoreCard(opportunity_id='x',strategy='a',fit=.5,win_probability=.5,expected_revenue_eur=50,expected_hours=1,cash_cost_eur=1,risk=.2,confidence=.5)
    assert not p.score_allowed(s)[0]
    w=WorkProduct(opportunity_id='x',strategy='a',title='x',proposal='p',draft_deliverable='d',price_eur=10,estimated_hours=1)
    assert not p.work_allowed(w)[0]

def test_db_learning(tmp_path):
    db=Database(str(tmp_path/'x.db')); db.record_outcome(Outcome(opportunity_id='1',strategy='research',result='paid',revenue_eur=50,cost_eur=5))
    st=db.strategy_stats()['research']; assert st['wins']==1 and st['profit']==45
