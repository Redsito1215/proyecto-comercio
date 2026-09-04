from datetime import UTC,datetime,time
from decimal import Decimal
from bson import Decimal128
from backend.common.serialization import to_json
from backend.modules.pricing.services import list_margins


def dec(value):return value.to_decimal() if isinstance(value,Decimal128) else Decimal(str(value or 0))


def date_filter(model,field="created_at"):
    query={}
    if model.date_from:query["$gte"]=datetime.combine(model.date_from,time.min,UTC)
    if model.date_to:query["$lte"]=datetime.combine(model.date_to,time.max,UTC)
    return {field:query} if query else {}


def sales_section(db,model):
    query={"status":{"$in":["confirmed","partially_returned"]},**date_filter(model,"confirmed_at")};rows=list(db.sales.find(query).sort("confirmed_at",-1).limit(500));total=sum((dec(x.get("total")) for x in rows),Decimal("0"))
    return {"label":"Ventas","columns":["Número","Fecha","Estado","Total"],"rows":[[x.get("number","-"),to_json(x.get("confirmed_at","-")),x["status"],str(dec(x.get("total")))] for x in rows],"metrics":{"operaciones":len(rows),"total":str(total)}}


def inventory_section(db,_model):
    rows=[]
    for stock in db.inventory.find().sort("available",1).limit(500):
        product=db.products.find_one({"_id":stock["product_id"]}) or {};rows.append([product.get("sku","-"),product.get("name","Producto"),stock["location_id"],stock.get("available",0),str(dec(stock.get("average_cost")))])
    return {"label":"Inventario","columns":["SKU","Producto","Ubicación","Disponible","Costo medio"],"rows":rows,"metrics":{"referencias":len(rows),"unidades":sum(x[3] for x in rows)}}


def margins_section(db,_model):
    data=list_margins(db);return {"label":"Márgenes","columns":["SKU","Producto","Precio","Costo","Margen %","Estado"],"rows":[[x["sku"],x["name"],x["current_price"],x["average_cost"] or "-",x["percent"] or "-",x["status"]] for x in data],"metrics":{"productos":len(data),"críticos":sum(x["status"]=="critical" for x in data)}}


def customers_section(db,_model):
    rows=[]
    for customer in db.customers.find({"status":"active"}).sort("name",1).limit(500):
        seg=db.customer_segments.find_one({"customer_id":customer["_id"]}) or {};churn=db.churn_signals.find_one({"customer_id":customer["_id"]}) or {};rows.append([customer["name"],customer.get("email","-"),seg.get("segment","sin_historial"),seg.get("frequency",0),churn.get("status","sin_datos")])
    return {"label":"Clientes","columns":["Cliente","Correo","Segmento","Frecuencia","Riesgo"],"rows":rows,"metrics":{"clientes":len(rows)}}


def losses_section(db,model):
    rows=list(db.loss_events.find(date_filter(model,"occurred_at")).sort("occurred_at",-1).limit(500));total=sum((dec(x.get("total_cost",dec(x.get("unit_cost"))*x.get("quantity",0))) for x in rows),Decimal("0"))
    return {"label":"Mermas","columns":["Fecha","Tipo","Cantidad","Costo","Motivo"],"rows":[[to_json(x.get("occurred_at")),x["type"],x["quantity"],str(dec(x.get("total_cost",dec(x.get("unit_cost"))*x["quantity"]))),x.get("reason","")] for x in rows],"metrics":{"eventos":len(rows),"costo":str(total)}}


def payments_section(db,model):
    rows=list(db.payments.find(date_filter(model,"created_at")).sort("created_at",-1).limit(500));return {"label":"Pagos","columns":["Fecha","Medio","Estado","Importe","Proveedor"],"rows":[[to_json(x["created_at"]),x["method"],x["status"],str(dec(x["amount"])),x["provider"]] for x in rows],"metrics":{"pagos":len(rows),"aprobados":sum(x["status"]=="approved" for x in rows)}}


def forecasts_section(db,_model):
    run=db.forecast_runs.find_one({"status":"completed"},sort=[("created_at",-1)]);rows=list(db.forecasts.find({"run_id":run["_id"]}).sort("recommended_quantity",-1).limit(500)) if run else []
    return {"label":"Pronóstico","columns":["SKU","Producto","Esperado","Intervalo","Disponible","Sugerido"],"rows":[[x["sku"],x["product_name"],x["expected_units"],f'{x["lower_bound"]}-{x["upper_bound"]}',x["available"],x["recommended_quantity"]] for x in rows],"metrics":{"productos":len(rows),"compra_sugerida":sum(x["recommended_quantity"] for x in rows)}}


BUILDERS={"sales":sales_section,"inventory":inventory_section,"margins":margins_section,"customers":customers_section,"losses":losses_section,"payments":payments_section,"forecasts":forecasts_section}


def build_snapshot(db,model):
    sections=[BUILDERS[name](db,model) for name in model.sections]
    return {"title":model.title,"period":{"from":str(model.date_from) if model.date_from else None,"to":str(model.date_to) if model.date_to else None},"generated_at":datetime.now(UTC).isoformat(),"source":"MongoDB operativo; ClickHouse alimentado por Airflow para analítica histórica","sections":sections}
