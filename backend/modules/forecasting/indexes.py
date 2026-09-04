from pymongo import ASCENDING, DESCENDING, IndexModel


def ensure_forecast_indexes(db):
    db.demand_daily.create_index([("product_id", ASCENDING), ("location_id", ASCENDING), ("date", ASCENDING)], unique=True)
    db.forecast_runs.create_index([("created_at", DESCENDING)])
    db.forecasts.create_indexes([IndexModel([("run_id", ASCENDING), ("product_id", ASCENDING), ("location_id", ASCENDING)], unique=True), IndexModel([("product_id", ASCENDING), ("created_at", DESCENDING)])])
