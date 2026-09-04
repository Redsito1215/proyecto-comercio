from decimal import Decimal
import pytest
from backend.modules.pricing.analytics import calculate_margin


def test_margin_uses_percentage_over_sale_price():
    result = calculate_margin(Decimal("10"), Decimal("6"), Decimal("20"))
    assert result == {"amount": Decimal("4.00"), "percent": Decimal("40.00"), "minimum_price": Decimal("7.50"), "status": "healthy"}


def test_margin_marks_minimum_violation():
    result = calculate_margin(Decimal("10"), Decimal("9"), Decimal("20"))
    assert result["status"] == "critical"


def test_margin_reports_unknown_cost():
    assert calculate_margin(Decimal("10"), None)["status"] == "unknown"


def test_margin_rejects_zero_price():
    with pytest.raises(ValueError): calculate_margin(Decimal("0"), Decimal("1"))
