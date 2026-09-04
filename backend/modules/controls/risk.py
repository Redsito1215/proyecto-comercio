from decimal import Decimal


def expected_balance(opening:Decimal,movements:list[dict])->Decimal:
    total=opening
    for row in movements:total+=row["amount"] if row["direction"]=="in" else -row["amount"]
    return total


def classify_difference(difference:Decimal,prior_material_counts:int=0)->dict|None:
    absolute=abs(difference)
    if absolute<Decimal("2"):return None
    severity="high" if absolute>=Decimal("20") or prior_material_counts>=2 else "medium" if absolute>=Decimal("5") else "low"
    return {"severity":severity,"reason":f"Diferencia de caja de {difference:.2f}; requiere revisión", "amount":difference}
