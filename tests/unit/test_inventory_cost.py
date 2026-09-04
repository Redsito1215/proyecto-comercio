from decimal import Decimal

from bson import Decimal128

from backend.modules.core.services import weighted_average_cost


def test_weighted_average_cost_uses_existing_units():
    result = weighted_average_cost(10, Decimal128("2.00"), 5, Decimal("5.00"))
    assert result == Decimal("3.00")


def test_weighted_average_cost_ignores_negative_stock_value():
    result = weighted_average_cost(-2, Decimal128("100.00"), 4, Decimal("3.00"))
    assert result == Decimal("3.00")
