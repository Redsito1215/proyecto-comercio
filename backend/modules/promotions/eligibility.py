import hashlib


def experimental_group(promotion_id: str, customer_id: str, control_percent: int) -> str:
    bucket=int(hashlib.sha256(f"{promotion_id}:{customer_id}".encode()).hexdigest()[:8],16)%100
    return "control" if bucket<control_percent else "treatment"


def eligible_for_segment(segment_rule: str, segment: dict, churn: dict) -> tuple[bool,str]:
    if segment_rule=="all": return True,"Cliente activo con consentimiento vigente"
    if segment_rule=="at_risk":
        ok=churn.get("status")=="at_risk";return ok,"Retraso superior al intervalo individual" if ok else "Sin señal individual de abandono"
    if segment_rule=="frequent":
        ok=segment.get("frequency",0)>=3;return ok,"Tres o más compras confirmadas" if ok else "Frecuencia insuficiente"
    ok=segment.get("segment")=="leal_rentable"
    return ok,"Cliente recurrente con margen saludable" if ok else "No pertenece al segmento leal rentable"
