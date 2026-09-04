from datetime import date
from decimal import Decimal
from statistics import median


def calculate_customer_value(purchases):
    if not purchases:return {'segment':'sin_historial','spend':Decimal('0'),'margin':Decimal('0'),'frequency':0,'score':0,'explanation':'Sin compras confirmadas'}
    spend=sum((p['spend'] for p in purchases),Decimal('0'));margin=sum((p['margin'] for p in purchases),Decimal('0'));frequency=len(purchases)
    margin_rate=(margin/spend*100) if spend else Decimal('0');score=min(100,frequency*12+float(margin_rate)*.7)
    segment='leal_rentable' if frequency>=3 and margin_rate>=20 else ('frecuente' if frequency>=3 else 'ocasional')
    return {'segment':segment,'spend':spend,'margin':margin,'frequency':frequency,'score':round(score,2),'explanation':f'{frequency} compras, margen {margin_rate:.1f}% y gasto {spend:.2f}'}


def calculate_churn_signal(purchase_dates, today=None):
    today=today or date.today();ordered=sorted(purchase_dates)
    if len(ordered)<3:return {'status':'insufficient_history','confidence':0,'reason':'Se requieren al menos tres compras'}
    intervals=[(b-a).days for a,b in zip(ordered,ordered[1:])];expected=max(1,median(intervals));elapsed=(today-ordered[-1]).days;delay=elapsed-expected
    return {'status':'at_risk' if delay>max(7,expected*.25) else 'on_time','expected_interval_days':expected,'days_since_purchase':elapsed,'delay_days':delay,'confidence':min(.95,.55+len(intervals)*.08),'reason':f'Última compra hace {elapsed} días; intervalo habitual {expected} días'}
