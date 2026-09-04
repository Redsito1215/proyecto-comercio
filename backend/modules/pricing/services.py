from datetime import UTC, datetime
from decimal import Decimal
from bson import Decimal128, ObjectId

from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.modules.pricing.analytics import calculate_margin


def _decimal(value):
    return value.to_decimal() if isinstance(value, Decimal128) else Decimal(str(value))


def _product(db, product_id):
    if not ObjectId.is_valid(product_id): raise ApiError("Producto no encontrado", 404, "product_not_found")
    product = db.products.find_one({"_id": ObjectId(product_id), "active": True})
    if not product: raise ApiError("Producto no encontrado", 404, "product_not_found")
    return product


def margin_row(product):
    price = _decimal(product["current_price"])
    raw_cost = product.get("average_cost")
    cost = _decimal(raw_cost) if raw_cost is not None else None
    minimum = _decimal(product.get("minimum_margin_percent", Decimal128("20")))
    result = calculate_margin(price, cost, minimum)
    return {"id": str(product["_id"]), "sku": product["sku"], "name": product["name"],
            "current_price": str(price), "average_cost": str(cost) if cost is not None else None,
            "minimum_margin_percent": str(minimum), **{k: str(v) if isinstance(v, Decimal) else v for k,v in result.items()}}


def list_margins(db):
    return [margin_row(product) for product in db.products.find({"active": True}).sort("name_normalized", 1)]


def simulate_price(db, model):
    product = _product(db, model.product_id); row = margin_row({**product, "current_price": Decimal128(model.proposed_price)})
    row["allowed"] = row["status"] != "critical"
    row["proposed_price"] = str(model.proposed_price)
    return row


def apply_price(db, product_id, model, actor_id):
    if model.product_id != product_id: raise ApiError("El producto no coincide", 422, "product_mismatch")
    product = _product(db, product_id); simulation = simulate_price(db, model)
    if not simulation["allowed"]: raise ApiError("El precio deja el margen bajo el mínimo", 409, "minimum_margin_violation")
    now = datetime.now(UTC); old_price = product["current_price"]
    db.products.update_one({"_id": product["_id"]}, {"$set": {"current_price": Decimal128(model.proposed_price), "pricing_updated_at": now}})
    change_id = db.price_changes.insert_one({"product_id": product["_id"], "old_price": old_price,
        "new_price": Decimal128(model.proposed_price), "cost_snapshot": product.get("average_cost"),
        "margin_percent": Decimal128(simulation["percent"]), "reason": model.reason,
        "actor_id": actor_id, "effective_at": now, "created_at": now}).inserted_id
    return {**simulation, "change_id": str(change_id)}


def record_competitor_price(db, model, actor_id):
    product = _product(db, model.product_id); now = datetime.now(UTC)
    doc = model.model_dump(); doc.update({"product_id": product["_id"], "observed_price": Decimal128(model.observed_price), "actor_id": actor_id, "created_at": now})
    result = db.competitor_prices.insert_one(doc)
    return {"id": str(result.inserted_id), **to_json(doc)}


def market_comparison(db, product_id):
    product = _product(db, product_id); own = _decimal(product["current_price"])
    rows = list(db.competitor_prices.find({"product_id": product["_id"]}).sort("observed_at", -1).limit(50))
    values = sorted(_decimal(row["observed_price"]) for row in rows)
    median = values[len(values)//2] if values else None
    return {"product_id": product_id, "own_price": str(own), "minimum": str(values[0]) if values else None,
            "median": str(median) if median else None, "gap_to_median": str(own-median) if median else None,
            "observations": to_json(rows)}
