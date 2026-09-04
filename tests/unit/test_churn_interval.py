from datetime import date
from backend.modules.customers.analytics import calculate_churn_signal
def test_churn_uses_individual_interval():
    signal=calculate_churn_signal([date(2026,1,1),date(2026,1,11),date(2026,1,21)],date(2026,2,10))
    assert signal['expected_interval_days']==10 and signal['status']=='at_risk'
def test_churn_requires_history():
    assert calculate_churn_signal([date(2026,1,1)])['status']=='insufficient_history'
