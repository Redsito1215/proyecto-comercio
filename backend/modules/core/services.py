from datetime import UTC, datetime
from decimal import Decimal

from bson import Decimal128, ObjectId
from pymongo.errors import DuplicateKeyError

from backend.common.errors import ApiError
from backend.common.serialization import to_json, to_mongo
from backend.db import transaction
from backend.modules.core.repositories import get_sale, next_number


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
            result = db.inventory.update_one(
                {"product_id": item["product_id"], "location_id": sale["location_id"],
                 "available": {"$gte": item["quantity"]}},
                {"$inc": {"on_hand": -item["quantity"], "available": -item["quantity"]},
                 "$set": {"updated_at": now}}, session=session,
            )
            if result.modified_count != 1:
                raise ApiError(f"Stock insuficiente para {item['name']}", 409, "insufficient_stock")
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
