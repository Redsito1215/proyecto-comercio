from datetime import UTC, datetime
from decimal import Decimal

from bson import Decimal128, ObjectId
from pymongo.errors import DuplicateKeyError

from backend.common.errors import ApiError
from backend.common.serialization import to_json, to_mongo
from backend.db import transaction
from backend.modules.core.repositories import get_sale, next_number


def allocate_lot_quantities(lots: list[dict], quantity: int) -> list[dict]:
    ordered = sorted(lots, key=lambda lot: (lot.get("expires_at") is None, lot.get("expires_at") or "9999-12-31"))
    remaining, allocations = quantity, []
    for lot in ordered:
        take = min(remaining, lot["available_quantity"])
        if take:
            allocations.append({"lot_id": lot["_id"], "quantity": take})
            remaining -= take
        if remaining == 0:
            return allocations
    raise ValueError("Existencia por lote insuficiente")


def receive_inventory(db, model, idempotency_key: str, actor_id: str):
    prior = db.inventory_movements.find_one({"idempotency_key": idempotency_key})
    if prior:
        return {"idempotency_key": idempotency_key, "status": "received"}
    with transaction() as session:
        now = datetime.now(UTC)
        for line in model.items:
            if not ObjectId.is_valid(line.product_id):
                raise ApiError("Producto inválido", 422, "validation_error")
            product_id = ObjectId(line.product_id)
            if not db.products.find_one({"_id": product_id, "active": True}, session=session):
                raise ApiError("Producto no encontrado", 404, "product_not_found")
            expiry = datetime.fromisoformat(line.expires_at).replace(tzinfo=UTC) if line.expires_at else None
            lot = db.lots.find_one_and_update(
                {"product_id": product_id, "location_id": model.location_id, "lot_number": line.lot_number},
                {"$setOnInsert": {"created_at": now, "status": "available", "expires_at": expiry},
                 "$set": {"unit_cost": Decimal128(line.unit_cost), "updated_at": now},
                 "$inc": {"quantity": line.quantity, "available_quantity": line.quantity}},
                upsert=True, return_document=True, session=session,
            )
            db.inventory.update_one(
                {"product_id": product_id, "location_id": model.location_id},
                {"$setOnInsert": {"reserved": 0, "created_at": now}, "$set": {"average_cost": Decimal128(line.unit_cost), "updated_at": now},
                 "$inc": {"on_hand": line.quantity, "available": line.quantity}}, upsert=True, session=session,
            )
            db.inventory_movements.insert_one({
                "product_id": product_id, "location_id": model.location_id, "lot_id": lot["_id"], "type": "receipt",
                "quantity": line.quantity, "unit_cost": Decimal128(line.unit_cost), "source_type": "receipt",
                "idempotency_key": idempotency_key, "actor_id": actor_id, "occurred_at": now,
            }, session=session)
    return {"idempotency_key": idempotency_key, "status": "received"}


def inventory_snapshot(db):
    now = datetime.now(UTC)
    rows = []
    for stock in db.inventory.find().sort("updated_at", -1):
        product = db.products.find_one({"_id": stock["product_id"]}) or {}
        expiring = db.lots.count_documents({"product_id": stock["product_id"], "location_id": stock["location_id"], "status": "available", "expires_at": {"$gte": now, "$lte": now.replace(year=now.year + 1)}})
        rows.append({**to_json(stock), "id": str(stock["_id"]), "product_name": product.get("name", "Producto"), "sku": product.get("sku", ""), "expiring_lots": expiring})
    return rows


def create_product(db, model):
    from backend.modules.core.repositories import insert_product
    try:
        product_id = insert_product(db, to_mongo(model.model_dump()))
    except DuplicateKeyError as error:
        raise ApiError("El SKU o código de barras ya existe", 409, "duplicate_product") from error
    return serialize_product(db.find_one({"_id": product_id}) if hasattr(db, "find_one") else db.products.find_one({"_id": product_id}))


def serialize_product(product):
    product = to_json(product)
    product["id"] = product.pop("_id")
    return product


def create_sale_draft(db, model, actor_id: str):
    now = datetime.now(UTC)
    items, subtotal = [], Decimal("0")
    for line in model.items:
        if not ObjectId.is_valid(line.product_id):
            raise ApiError("Producto inválido", 422, "validation_error")
        product = db.products.find_one({"_id": ObjectId(line.product_id), "active": True})
        if not product:
            raise ApiError("Producto no encontrado o inactivo", 404, "product_not_found")
        price = product["current_price"].to_decimal()
        total = price * line.quantity
        subtotal += total
        items.append({
            "product_id": product["_id"], "sku": product["sku"], "name": product["name"],
            "quantity": line.quantity, "unit_price": Decimal128(price), "line_total": Decimal128(total),
            "unit_cost": product.get("average_cost", Decimal128("0")),
        })
    sale_id = db.sales.insert_one({
        "location_id": model.location_id, "customer_id": model.customer_id, "status": "draft",
        "subtotal": Decimal128(subtotal), "total": Decimal128(subtotal), "actor_id": actor_id,
        "created_at": now, "updated_at": now, "version": 1,
    }).inserted_id
    db.sale_items.insert_many([{**item, "sale_id": sale_id} for item in items])
    return serialize_sale(get_sale(db, str(sale_id)))


def confirm_sale(db, sale_id: str, idempotency_key: str, actor_id: str):
    prior = db.sales.find_one({"idempotency_key": idempotency_key})
    if prior:
        return serialize_sale(get_sale(db, str(prior["_id"])))
    with transaction() as session:
        sale = get_sale(db, sale_id, session=session)
        if not sale:
            raise ApiError("Venta no encontrada", 404, "sale_not_found")
        if sale["status"] != "draft":
            raise ApiError("La venta ya no está disponible para confirmar", 409, "sale_state_conflict")
        now = datetime.now(UTC)
        for item in sale["items"]:
            product = db.products.find_one({"_id": item["product_id"]}, session=session) or {}
            allocations = []
            if product.get("perishable"):
                lots = list(db.lots.find({"product_id": item["product_id"], "location_id": sale["location_id"], "status": "available", "available_quantity": {"$gt": 0}}).sort("expires_at", 1))
                try:
                    allocations = allocate_lot_quantities(lots, item["quantity"])
                except ValueError as error:
                    raise ApiError(str(error), 409, "insufficient_lot_stock") from error
            result = db.inventory.update_one(
                {"product_id": item["product_id"], "location_id": sale["location_id"],
                 "available": {"$gte": item["quantity"]}},
                {"$inc": {"on_hand": -item["quantity"], "available": -item["quantity"]},
                 "$set": {"updated_at": now}}, session=session,
            )
            if result.modified_count != 1:
                raise ApiError(f"Stock insuficiente para {item['name']}", 409, "insufficient_stock")
            for allocation in allocations:
                db.lots.update_one({"_id": allocation["lot_id"]}, {"$inc": {"available_quantity": -allocation["quantity"]}}, session=session)
            db.inventory_movements.insert_one({
                "product_id": item["product_id"], "location_id": sale["location_id"],
                "type": "sale", "quantity": -item["quantity"], "unit_cost": item["unit_cost"],
                "source_type": "sale", "source_id": sale["_id"], "actor_id": actor_id,
                "occurred_at": now,
            }, session=session)
        number = next_number(db, "sales", "VTA", session=session)
        db.sales.update_one({"_id": sale["_id"]}, {"$set": {
            "number": number, "status": "confirmed", "idempotency_key": idempotency_key,
            "confirmed_at": now, "updated_at": now, "confirmed_by": actor_id,
        }, "$inc": {"version": 1}}, session=session)
    return serialize_sale(get_sale(db, sale_id))


def serialize_sale(sale):
    sale = to_json(sale)
    sale["id"] = sale.pop("_id")
    for item in sale.get("items", []):
        item["id"] = item.pop("_id")
    return sale
