import re
import unicodedata
from datetime import UTC, datetime

from bson import ObjectId
from pymongo import ReturnDocument


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return " ".join(value.lower().split())


def next_number(db, key: str, prefix: str, session=None) -> str:
    counter = db.counters.find_one_and_update(
        {"_id": key}, {"$inc": {"value": 1}}, upsert=True,
        return_document=ReturnDocument.AFTER, session=session,
    )
    return f"{prefix}-{counter['value']:06d}"


def search_products(db, query: str = "", limit: int = 30, category_id: str = "", location_id: str = ""):
    criteria = {"active": True}
    if category_id and ObjectId.is_valid(category_id):
        criteria["category_id"] = ObjectId(category_id)
    if query:
        normalized = normalize(query)
        criteria["$or"] = [
            {"sku": {"$regex": re.escape(query), "$options": "i"}},
            {"barcodes": query},
            {"name_normalized": {"$regex": re.escape(normalized), "$options": "i"}},
        ]
    pipeline = [
        {"$match": criteria}, {"$sort": {"name_normalized": 1}}, {"$limit": min(limit, 100)},
        {"$lookup": {"from": "inventory", "let": {"pid": "$_id"}, "pipeline": [
            {"$match": {"$expr": {"$and": [
                {"$eq": ["$product_id", "$$pid"]},
                *([{"$eq": ["$location_id", location_id]}] if location_id else []),
            ]}}},
            {"$group": {"_id": None, "available": {"$sum": "$available"}}},
        ], "as": "stock"}},
        {"$set": {"available": {"$ifNull": [{"$first": "$stock.available"}, 0]}}},
        {"$unset": "stock"},
    ]
    return list(db.products.aggregate(pipeline))


def insert_product(db, payload: dict):
    now = datetime.now(UTC)
    document = {
        **payload, "sku": payload["sku"].upper(), "name_normalized": normalize(payload["name"]),
        "barcodes": [payload.pop("barcode")] if payload.get("barcode") else [],
        "active": True, "created_at": now, "updated_at": now, "version": 1,
    }
    document.pop("barcode", None)
    return db.products.insert_one(document).inserted_id


def get_sale(db, sale_id: str, session=None):
    if not ObjectId.is_valid(sale_id):
        return None
    sale = db.sales.find_one({"_id": ObjectId(sale_id)}, session=session)
    if sale:
        sale["items"] = list(db.sale_items.find({"sale_id": sale["_id"]}, session=session))
    return sale
