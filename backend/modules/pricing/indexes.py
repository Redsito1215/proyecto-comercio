from pymongo import ASCENDING, DESCENDING


def ensure_pricing_indexes(db):
    db.price_changes.create_index([("product_id", ASCENDING), ("effective_at", DESCENDING)])
    db.competitor_prices.create_index([("product_id", ASCENDING), ("observed_at", DESCENDING)])
