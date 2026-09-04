from decimal import Decimal, ROUND_HALF_UP

MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def calculate_margin(price: Decimal, cost: Decimal | None, minimum_percent: Decimal = Decimal("20")) -> dict:
    if cost is None:
        return {"amount": None, "percent": None, "minimum_price": None, "status": "unknown"}
    if price <= 0:
        raise ValueError("El precio debe ser mayor que cero")
    amount = money(price - cost)
    percent = ((price - cost) / price * Decimal("100")).quantize(MONEY, rounding=ROUND_HALF_UP)
    denominator = Decimal("1") - minimum_percent / Decimal("100")
    minimum_price = money(cost / denominator) if denominator > 0 else None
    if percent < minimum_percent:
        status = "critical"
    elif percent < minimum_percent + Decimal("10"):
        status = "tight"
    else:
        status = "healthy"
    return {"amount": amount, "percent": percent, "minimum_price": minimum_price, "status": status}
