from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from backend.auth.decorators import require_permission
from backend.common.errors import ApiError
from backend.common.serialization import to_json, to_mongo
from backend.db import get_db
from backend.modules.core.repositories import insert_product, search_products
from backend.modules.core.schemas import CatalogCreate, InventoryReceiptCreate, LocationCreate, LostSaleCreate, ProductCreate, PurchaseOrderCreate, PurchaseReceiptCreate, ReturnCreate, SaleCreate, StockCountCreate, SupplierCreate
from backend.modules.core.services import approve_stock_count, confirm_sale, create_purchase_order, create_return, create_sale_draft, create_stock_count, inventory_snapshot, list_purchase_orders, receive_inventory, receive_purchase_order, record_lost_sale, serialize_product

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


def _catalog_list(collection):
    return [to_json({**x,"id":str(x["_id"])}) for x in collection.find().sort("name",1)]


def _catalog_create(collection, model):
    doc=to_mongo(model.model_dump());doc["code"]=doc["code"].upper();doc["name_normalized"]=doc["name"].casefold()
    try: identifier=collection.insert_one(doc).inserted_id
    except Exception as error:
        if error.__class__.__name__=="DuplicateKeyError":raise ApiError("El código ya existe",409,"duplicate_catalog") from error
        raise
    return to_json({**doc,"id":str(identifier)})


@core_bp.get("/categories")
@require_permission("catalogs.read")
def categories_list():return jsonify({"data":_catalog_list(get_db().categories)})

@core_bp.post("/categories")
@require_permission("catalogs.write")
def categories_create():return jsonify({"data":_catalog_create(get_db().categories,validate(CatalogCreate,request.get_json(silent=True)))}),201

@core_bp.get("/suppliers")
@require_permission("catalogs.read")
def suppliers_list():return jsonify({"data":_catalog_list(get_db().suppliers)})

@core_bp.post("/suppliers")
@require_permission("catalogs.write")
def suppliers_create():return jsonify({"data":_catalog_create(get_db().suppliers,validate(SupplierCreate,request.get_json(silent=True)))}),201

@core_bp.get("/locations")
@require_permission("catalogs.read")
def locations_list():return jsonify({"data":_catalog_list(get_db().locations)})

@core_bp.post("/locations")
@require_permission("catalogs.write")
def locations_create():return jsonify({"data":_catalog_create(get_db().locations,validate(LocationCreate,request.get_json(silent=True)))}),201


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


@core_bp.post('/returns')
@require_permission('returns.write')
def returns_create():
    key=request.headers.get('Idempotency-Key','').strip()
    if not key:raise ApiError('Se requiere Idempotency-Key',400,'idempotency_key_required')
    return jsonify({'data':create_return(get_db(),validate(ReturnCreate,request.get_json(silent=True)),key,g.actor_id)}),201
