from decimal import Decimal
from backend.modules.controls.risk import classify_difference,expected_balance


def test_expected_balance_uses_append_only_movements():
    rows=[{"direction":"in","amount":Decimal("10")},{"direction":"out","amount":Decimal("3.50")}]
    assert expected_balance(Decimal("20"),rows)==Decimal("26.50")


def test_immaterial_difference_creates_no_alert():
    assert classify_difference(Decimal("-1.99")) is None


def test_repeated_difference_increases_severity():
    assert classify_difference(Decimal("3"),2)["severity"]=="high"
