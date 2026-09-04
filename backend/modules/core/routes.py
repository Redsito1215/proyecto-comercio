from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from backend.auth.decorators import require_permission
from backend.common.errors import ApiError
from backend.common.serialization import to_json, to_mongo
from backend.db import get_db
from backend.modules.core.repositories import insert_product, search_products
from backend.modules.core.schemas import InventoryReceiptCreate, LostSaleCreate, ProductCreate, PurchaseOrderCreate, PurchaseReceiptCreate, SaleCreate, StockCountCreate
from backend.modules.core.services import approve_stock_count, confirm_sale, create_purchase_order, create_sale_draft, create_stock_count, inventory_snapshot, list_purchase_orders, receive_inventory, receive_purchase_order, record_lost_sale, serialize_product

core_bp = Blueprint("core", __name__, url_prefix="/api/v1")


def validate(model, payload):
    try:
        return model.model_validate(payload or {})
    except ValidationError as error:
        raise ApiError(error.errors(include_url=False)[0]["msg"], 422, "validation_error") from error


@core_bp.get("/products")
@require_permission("products.read")
def products_list():
    products = [serialize_product(item) for item in search_products(get_db(), request.args.get("q", ""))]
    return jsonify({"data": products})


@core_bp.post("/products")
@require_permission("products.write")
def products_create():
    model = validate(ProductCreate, request.get_json(silent=True))
    db = get_db()
    try:
        product_id = insert_product(db, to_mongo(model.model_dump()))
    except Exception as error:
        if error.__class__.__name__ == "DuplicateKeyError":
            raise ApiError("El SKU o código de barras ya existe", 409, "duplicate_product") from error
        raise
    return jsonify({"data": serialize_product(db.products.find_one({"_id": product_id}))}), 201


@core_bp.post("/sales")
@require_permission("sales.write")
def sales_create():
    model = validate(SaleCreate, request.get_json(silent=True))
    return jsonify({"data": create_sale_draft(get_db(), model, g.actor_id)}), 201


@core_bp.post("/sales/<sale_id>/confirm")
@require_permission("sales.confirm")
def sales_confirm(sale_id):
    key = request.headers.get("Idempotency-Key", "").strip()
    if not key:
        raise ApiError("Se requiere Idempotency-Key", 400, "idempotency_key_required")
    return jsonify({"data": confirm_sale(get_db(), sale_id, key, g.actor_id)})


@core_bp.get("/inventory")
@require_permission("inventory.read")
def inventory_list():
    return jsonify({"data": inventory_snapshot(get_db())})


@core_bp.post("/inventory/receipts")
@require_permission("inventory.receive")
def inventory_receive():
    key = request.headers.get("Idempotency-Key", "").strip()
    if not key:
        raise ApiError("Se requiere Idempotency-Key", 400, "idempotency_key_required")
    model = validate(InventoryReceiptCreate, request.get_json(silent=True))
    return jsonify({"data": receive_inventory(get_db(), model, key, g.actor_id)}), 201


@core_bp.get("/purchase-orders")
@require_permission("purchases.read")
def purchase_orders_list():
    return jsonify({"data": list_purchase_orders(get_db())})


@core_bp.post("/purchase-orders")
@require_permission("purchases.write")
def purchase_orders_create():
    model=validate(PurchaseOrderCreate,request.get_json(silent=True))
    return jsonify({"data":create_purchase_order(get_db(),model,g.actor_id)}),201


@core_bp.post("/purchase-orders/<order_id>/receipts")
@require_permission("purchases.receive")
def purchase_orders_receive(order_id):
    key=request.headers.get("Idempotency-Key","").strip()
    if not key: raise ApiError("Se requiere Idempotency-Key",400,"idempotency_key_required")
    model=validate(PurchaseReceiptCreate,request.get_json(silent=True))
    return jsonify({"data":receive_purchase_order(get_db(),order_id,model,key,g.actor_id)}),201


@core_bp.post('/stock-counts')
@require_permission('inventory.count')
def stock_counts_create():
    return jsonify({'data':create_stock_count(get_db(),validate(StockCountCreate,request.get_json(silent=True)),g.actor_id)}),201


@core_bp.post('/stock-counts/<count_id>/approve')
@require_permission('inventory.adjust')
def stock_counts_approve(count_id):
    return jsonify({'data':approve_stock_count(get_db(),count_id,g.actor_id)})


@core_bp.post('/lost-sales')
@require_permission('sales.write')
def lost_sales_create():
    model=validate(LostSaleCreate,request.get_json(silent=True)); return jsonify({'data':{'id':record_lost_sale(get_db(),model,g.actor_id)}}),201
