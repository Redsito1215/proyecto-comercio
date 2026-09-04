from decimal import Decimal, ROUND_HALF_UP
from statistics import median

TWO = Decimal("0.01")


def forecast_demand(observations: list[dict], horizon_days: int) -> dict:
    """Robust, deterministic forecast with explicit censored-demand signals."""
    if not observations:
        return {"expected_units": 0, "lower_bound": 0, "upper_bound": 0, "confidence": "low",
                "factors": ["Sin historial suficiente"], "daily_rate": Decimal("0.00")}
    normal = [Decimal(str(row.get("sold", 0))) for row in observations if not row.get("promotion")]
    sample = normal or [Decimal(str(row.get("sold", 0))) for row in observations]
    base = Decimal(str(median(sample)))
    lost = sum(Decimal(str(row.get("lost", 0))) for row in observations)
    lost_daily = lost / Decimal(len(observations))
    rate = base + lost_daily
    factors = [f"Mediana diaria sin promociones: {base.quantize(TWO)}"]
    if lost:
        factors.append(f"Demanda no atendida incorporada: {lost} unidades")
    promo_days = sum(bool(row.get("promotion")) for row in observations)
    if promo_days:
        factors.append(f"Se aislaron {promo_days} días promocionales")
    price_change_days = sum(bool(row.get("price_changed")) for row in observations)
    if price_change_days:
        factors.append(f"Se detectaron {price_change_days} días bajo un precio diferente al vigente")
    substitute_days = sum(bool(row.get("substitute_unavailable")) for row in observations)
    if substitute_days:
        factors.append(f"La ausencia de sustitutos pudo elevar {substitute_days} días de demanda")
    stockout_days = sum(bool(row.get("stockout")) for row in observations)
    if stockout_days:
        factors.append(f"{stockout_days} días con señal de agotado reducen la confianza")
    expected = int((rate * horizon_days).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    spread = max(1, int(expected * (Decimal("0.35") if len(observations) < 28 or stockout_days else Decimal("0.20"))))
    confidence = "high" if len(observations) >= 42 and not stockout_days and not substitute_days else "medium" if len(observations) >= 21 else "low"
    return {"expected_units": expected, "lower_bound": max(0, expected-spread), "upper_bound": expected+spread,
            "confidence": confidence, "factors": factors, "daily_rate": rate.quantize(TWO)}
