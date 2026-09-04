from decimal import Decimal
from backend.modules.customers.analytics import calculate_customer_value
def test_frequency_and_margin_can_beat_single_large_purchase():
    loyal=calculate_customer_value([{'spend':Decimal('20'),'margin':Decimal('8')}] * 4)
    large=calculate_customer_value([{'spend':Decimal('200'),'margin':Decimal('10')}])
    assert loyal['score']>large['score'] and loyal['segment']=='leal_rentable'
