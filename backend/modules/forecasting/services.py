from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from bson import Decimal128

from backend.common.serialization import to_json
from backend.modules.forecasting.engine import forecast_demand


def aggregate_daily(db, location_id: str, lookback_days: int, cutoff: datetime):
    start = cutoff - timedelta(days=lookback_days)
    products = {p["_id"]: p for p in db.products.find({"active": True})}
    buckets = defaultdict(lambda: {"sold": 0, "returned": 0, "lost": 0, "promotion": False, "stockout": False, "prices": set()})
    sales = list(db.sales.find({"location_id": location_id, "status": {"$in": ["confirmed", "partially_returned"]}, "confirmed_at": {"$gte": start, "$lte": cutoff}}))
    sale_map = {s["_id"]: s for s in sales}
    for line in db.sale_items.find({"sale_id": {"$in": list(sale_map)}}):
        day = sale_map[line["sale_id"]]["confirmed_at"].date().isoformat(); key = (line["product_id"], day)
        buckets[key]["sold"] += line["quantity"]; buckets[key]["promotion"] = bool(line.get("promotion_id"))
        if line.get("unit_price") is not None: buckets[key]["prices"].add(str(line["unit_price"]))
    for row in db.return_items.find({"sale_id": {"$in": list(sale_map)}}):
        day = sale_map[row["sale_id"]]["confirmed_at"].date().isoformat()
        buckets[(row["product_id"], day)]["returned"] += row.get("fit_quantity", 0) + row.get("damaged_quantity", 0)
    lost_by_day=defaultdict(set)
    for row in db.lost_sales.find({"location_id": {"$in": [location_id, None]}, "occurred_at": {"$gte": start, "$lte": cutoff}}):
        day = row["occurred_at"].date().isoformat(); key = (row["product_id"], day)
        buckets[key]["lost"] += row["requested_quantity"]; buckets[key]["stockout"] = row.get("reason") == "out_of_stock"
        if buckets[key]["stockout"]: lost_by_day[day].add(row["product_id"])
    series = defaultdict(list)
    for offset in range(lookback_days):
        day = (start + timedelta(days=offset+1)).date().isoformat()
        for pid, product in products.items():
            row={"date":day,**buckets[(pid,day)]}; prices=row.pop("prices")
            row["price_changed"]=bool(prices and str(product.get("current_price")) not in prices)
            row["substitute_unavailable"]=bool(set(product.get("substitute_ids",[])) & lost_by_day[day])
            series[pid].append(row)
    return products, series


def create_run(db, model, actor_id):
    now = datetime.now(UTC); products, series = aggregate_daily(db, model.location_id, model.lookback_days, now)
    run_id = db.forecast_runs.insert_one({"cutoff_at": now, "horizon_days": model.horizon_days, "lookback_days": model.lookback_days,
        "location_id": model.location_id, "method_version": "robust-median-v1", "status": "completed", "actor_id": actor_id, "created_at": now}).inserted_id
    docs=[]
    for pid, product in products.items():
        result=forecast_demand(series[pid], model.horizon_days)
        on_hand=sum(x.get("available",0) for x in db.inventory.find({"product_id":pid,"location_id":model.location_id}))
        recommended=max(0,result["upper_bound"]-on_hand)
        docs.append({"run_id":run_id,"product_id":pid,"location_id":model.location_id,"product_name":product["name"],"sku":product["sku"],
            **{k:Decimal128(v) if isinstance(v,Decimal) else v for k,v in result.items()},"available":on_hand,"recommended_quantity":recommended,"created_at":now})
    if docs: db.forecasts.insert_many(docs)
    return {"id":str(run_id),"status":"completed","products":len(docs),"horizon_days":model.horizon_days}


def latest_forecasts(db, location_id="main"):
    run=db.forecast_runs.find_one({"location_id":location_id,"status":"completed"},sort=[("created_at",-1)])
    if not run:return []
    return [to_json({**row,"id":str(row["_id"])}) for row in db.forecasts.find({"run_id":run["_id"]}).sort("recommended_quantity",-1)]


def list_runs(db):
    return [to_json({**row,"id":str(row["_id"])}) for row in db.forecast_runs.find().sort("created_at",-1).limit(30)]
