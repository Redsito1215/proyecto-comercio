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


def create_purchase_order(db, model, actor_id: str):
    now = datetime.now(UTC); total = Decimal("0"); prepared = []
    for line in model.items:
        if not ObjectId.is_valid(line.product_id) or not db.products.find_one({"_id": ObjectId(line.product_id), "active": True}):
            raise ApiError("Producto no encontrado", 404, "product_not_found")
        total += line.unit_cost * line.quantity
        prepared.append({"product_id":ObjectId(line.product_id),"ordered_quantity":line.quantity,"received_quantity":0,"pending_quantity":line.quantity,"unit_cost":Decimal128(line.unit_cost)})
    number = next_number(db, "purchase_orders", "OC")
    order_id = db.purchase_orders.insert_one({"number":number,"supplier_name":model.supplier_name,"location_id":model.location_id,"status":"sent","total":Decimal128(total),"actor_id":actor_id,"created_at":now,"updated_at":now}).inserted_id
    db.purchase_order_items.insert_many([{**item,"purchase_order_id":order_id} for item in prepared])
    return {"id":str(order_id),"number":number,"status":"sent","total":str(total)}


def receive_purchase_order(db, order_id: str, model, key: str, actor_id: str):
    if not ObjectId.is_valid(order_id): raise ApiError("Orden no encontrada",404,"order_not_found")
    prior = db.inventory_movements.find_one({"idempotency_key":key})
    if prior: return {"id":order_id,"status":"received"}
    oid=ObjectId(order_id)
    with transaction() as session:
        order=db.purchase_orders.find_one({"_id":oid,"status":{"$in":["sent","partially_received"]}},session=session)
        if not order: raise ApiError("Orden no disponible para recepción",409,"order_state_conflict")
        now=datetime.now(UTC)
        for line in model.items:
            pid=ObjectId(line.product_id) if ObjectId.is_valid(line.product_id) else None
            item=db.purchase_order_items.find_one({"purchase_order_id":oid,"product_id":pid,"pending_quantity":{"$gte":line.quantity}},session=session)
            if not item: raise ApiError("Cantidad recibida supera lo pendiente",409,"receipt_quantity_conflict")
            expiry=datetime.fromisoformat(line.expires_at).replace(tzinfo=UTC) if line.expires_at else None
            lot=db.lots.find_one_and_update({"product_id":pid,"location_id":order["location_id"],"lot_number":line.lot_number},{"$setOnInsert":{"created_at":now,"status":"available","expires_at":expiry},"$set":{"unit_cost":Decimal128(line.unit_cost),"updated_at":now},"$inc":{"quantity":line.quantity,"available_quantity":line.quantity}},upsert=True,return_document=True,session=session)
            db.inventory.update_one({"product_id":pid,"location_id":order["location_id"]},{"$setOnInsert":{"reserved":0,"created_at":now},"$set":{"average_cost":Decimal128(line.unit_cost),"updated_at":now},"$inc":{"on_hand":line.quantity,"available":line.quantity}},upsert=True,session=session)
            db.purchase_order_items.update_one({"_id":item["_id"]},{"$inc":{"received_quantity":line.quantity,"pending_quantity":-line.quantity}},session=session)
            db.inventory_movements.insert_one({"product_id":pid,"location_id":order["location_id"],"lot_id":lot["_id"],"type":"receipt","quantity":line.quantity,"unit_cost":Decimal128(line.unit_cost),"source_type":"purchase_order","source_id":oid,"idempotency_key":key,"actor_id":actor_id,"occurred_at":now},session=session)
        pending=db.purchase_order_items.count_documents({"purchase_order_id":oid,"pending_quantity":{"$gt":0}},session=session)
        status="partially_received" if pending else "received"
        db.purchase_orders.update_one({"_id":oid},{"$set":{"status":status,"updated_at":now}},session=session)
    return {"id":order_id,"status":status}


def list_purchase_orders(db):
    return [{**to_json(row),"id":str(row["_id"])} for row in db.purchase_orders.find().sort("created_at",-1).limit(100)]


def create_stock_count(db, model, actor_id):
    now=datetime.now(UTC); count_id=db.stock_counts.insert_one({'location_id':model.location_id,'status':'open','actor_id':actor_id,'created_at':now}).inserted_id; rows=[]
    for line in model.items:
        pid=ObjectId(line.product_id) if ObjectId.is_valid(line.product_id) else None
        stock=db.inventory.find_one({'product_id':pid,'location_id':model.location_id})
        if not stock: raise ApiError('No existe inventario para el producto',404,'inventory_not_found')
        rows.append({'stock_count_id':count_id,'product_id':pid,'theoretical_quantity':stock['on_hand'],'physical_quantity':line.physical_quantity,'difference':line.physical_quantity-stock['on_hand'],'reason':line.reason})
    db.stock_count_items.insert_many(rows); return {'id':str(count_id),'status':'open'}


def approve_stock_count(db, count_id, actor_id):
    if not ObjectId.is_valid(count_id): raise ApiError('Conteo no encontrado',404,'count_not_found')
    cid=ObjectId(count_id)
    with transaction() as session:
        count=db.stock_counts.find_one({'_id':cid,'status':'open'},session=session)
        if not count: raise ApiError('Conteo no disponible',409,'count_state_conflict')
        now=datetime.now(UTC)
        for item in db.stock_count_items.find({'stock_count_id':cid},session=session):
            diff=item['difference']
            if diff:
                db.inventory.update_one({'product_id':item['product_id'],'location_id':count['location_id']},{'$inc':{'on_hand':diff,'available':diff},'$set':{'updated_at':now}},session=session)
                db.inventory_movements.insert_one({'product_id':item['product_id'],'location_id':count['location_id'],'type':'count_adjustment','quantity':diff,'source_type':'stock_count','source_id':cid,'reason':item['reason'],'actor_id':actor_id,'occurred_at':now},session=session)
        db.stock_counts.update_one({'_id':cid},{'$set':{'status':'approved','approved_by':actor_id,'approved_at':now}},session=session)
    return {'id':count_id,'status':'approved'}


def record_lost_sale(db, model, actor_id):
    if not ObjectId.is_valid(model.product_id) or not db.products.find_one({'_id':ObjectId(model.product_id)}): raise ApiError('Producto no encontrado',404,'product_not_found')
    doc={'product_id':ObjectId(model.product_id),'requested_quantity':model.requested_quantity,'reason':model.reason,'actor_id':actor_id,'occurred_at':datetime.now(UTC)}
    return str(db.lost_sales.insert_one(doc).inserted_id)


def validate_return_quantity(sold: int, previously_returned: int, requested: int) -> int:
    available=sold-previously_returned
    if requested<1 or requested>available: raise ValueError('Cantidad de devolución fuera del límite disponible')
    return available


def create_return(db, model, key, actor_id):
    prior=db.returns.find_one({'idempotency_key':key})
    if prior:return {'id':str(prior['_id']),'number':prior['number'],'status':prior['status']}
    if not ObjectId.is_valid(model.sale_id):raise ApiError('Venta no encontrada',404,'sale_not_found')
    sid=ObjectId(model.sale_id)
    with transaction() as session:
        sale=db.sales.find_one({'_id':sid,'status':{'$in':['confirmed','partially_returned']}},session=session)
        if not sale:raise ApiError('Venta no disponible para devolución',409,'return_state_conflict')
        now=datetime.now(UTC); rid=ObjectId(); number=next_number(db,'returns','DEV',session=session); docs=[]
        for line in model.items:
            pid=ObjectId(line.product_id) if ObjectId.is_valid(line.product_id) else None
            sold=db.sale_items.find_one({'sale_id':sid,'product_id':pid},session=session)
            if not sold:raise ApiError('Producto no pertenece a la venta',422,'return_product_invalid')
            previous=sum(x.get('fit_quantity',0)+x.get('damaged_quantity',0) for x in db.return_items.find({'sale_id':sid,'product_id':pid},session=session))
            requested=line.fit_quantity+line.damaged_quantity
            try:validate_return_quantity(sold['quantity'],previous,requested)
            except ValueError as error:raise ApiError(str(error),409,'return_quantity_conflict') from error
            if line.fit_quantity:
                db.inventory.update_one({'product_id':pid,'location_id':sale['location_id']},{'$inc':{'on_hand':line.fit_quantity,'available':line.fit_quantity},'$set':{'updated_at':now}},session=session)
                db.inventory_movements.insert_one({'product_id':pid,'location_id':sale['location_id'],'type':'return_fit','quantity':line.fit_quantity,'source_type':'return','source_id':rid,'actor_id':actor_id,'occurred_at':now},session=session)
            if line.damaged_quantity:
                db.loss_events.insert_one({'product_id':pid,'location_id':sale['location_id'],'type':'damaged_return','quantity':line.damaged_quantity,'unit_cost':sold.get('unit_cost',Decimal128('0')),'source_id':rid,'reason':line.reason,'actor_id':actor_id,'occurred_at':now},session=session)
            docs.append({'return_id':rid,'sale_id':sid,'product_id':pid,'fit_quantity':line.fit_quantity,'damaged_quantity':line.damaged_quantity,'reason':line.reason})
        db.returns.insert_one({'_id':rid,'number':number,'sale_id':sid,'status':'confirmed','idempotency_key':key,'actor_id':actor_id,'created_at':now},session=session)
        db.return_items.insert_many(docs,session=session)
        db.sales.update_one({'_id':sid},{'$set':{'status':'partially_returned','updated_at':now}},session=session)
    return {'id':str(rid),'number':number,'status':'confirmed'}


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
