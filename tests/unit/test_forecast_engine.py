from backend.modules.forecasting.engine import forecast_demand


def test_promotion_peak_is_not_extrapolated():
    rows=[{"sold":2,"lost":0} for _ in range(20)]+[{"sold":30,"lost":0,"promotion":True}]
    result=forecast_demand(rows,7)
    assert result["expected_units"] == 14
    assert any("promocionales" in factor for factor in result["factors"])


def test_lost_sales_reveal_hidden_demand():
    rows=[{"sold":1,"lost":1,"stockout":True} for _ in range(28)]
    result=forecast_demand(rows,7)
    assert result["expected_units"] == 14
    assert result["confidence"] == "medium"


def test_empty_history_expresses_uncertainty():
    result=forecast_demand([],14)
    assert result["confidence"] == "low" and result["expected_units"] == 0
