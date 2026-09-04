from datetime import UTC,datetime
from decimal import Decimal
from bson import Decimal128,ObjectId
from pymongo.errors import DuplicateKeyError

from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.db import transaction
from backend.modules.controls.risk import classify_difference,expected_balance


def dec(value):return value.to_decimal() if isinstance(value,Decimal128) else Decimal(str(value))


def open_session(db,model,actor):
    now=datetime.now(UTC);doc={"register_id":model.register_id,"location_id":model.location_id,"status":"open","opening_amount":Decimal128(model.opening_amount),"opened_by":actor,"opened_at":now,"created_at":now}
    try:sid=db.cash_sessions.insert_one(doc).inserted_id
    except DuplicateKeyError as error:raise ApiError("La caja ya tiene una sesión abierta",409,"cash_session_exists") from error
    return {"id":str(sid),**to_json(doc),"expected_balance":str(model.opening_amount)}


def get_session(db,sid,open_only=False):
    if not ObjectId.is_valid(sid):raise ApiError("Sesión no encontrada",404,"cash_session_not_found")
    query={"_id":ObjectId(sid)}
    if open_only:query["status"]="open"
    session=db.cash_sessions.find_one(query)
    if not session:raise ApiError("Sesión no disponible",409,"cash_session_state")
    return session


def session_balance(db,session):
    movements=[{"amount":dec(x["amount"]),"direction":x["direction"]} for x in db.cash_movements.find({"session_id":session["_id"]})]
    return expected_balance(dec(session["opening_amount"]),movements)


def add_movement(db,sid,model,key,actor):
    session=get_session(db,sid,True);prior=db.cash_movements.find_one({"idempotency_key":key})
    if prior:return {"id":str(prior["_id"]),"status":"recorded","expected_balance":str(session_balance(db,session))}
    direction="in" if model.type in ("sale","deposit") else "out"
    if model.source_type=="sale" and model.source_id:
        if not ObjectId.is_valid(model.source_id) or not db.sales.find_one({"_id":ObjectId(model.source_id),"status":{"$in":["confirmed","partially_returned"]}}):raise ApiError("Venta no encontrada",404,"sale_not_found")
        if db.cash_movements.find_one({"source_type":"sale","source_id":model.source_id}):raise ApiError("La venta ya fue registrada en caja",409,"sale_cash_duplicate")
    now=datetime.now(UTC);doc={"session_id":session["_id"],"type":model.type,"direction":direction,"amount":Decimal128(model.amount),"source_type":model.source_type,"source_id":model.source_id,"reason":model.reason,"idempotency_key":key,"actor_id":actor,"occurred_at":now}
    mid=db.cash_movements.insert_one(doc).inserted_id
    return {"id":str(mid),"status":"recorded","expected_balance":str(session_balance(db,session))}


def record_count(db,sid,model,actor,close=False):
    session=get_session(db,sid,True);expected=session_balance(db,session);difference=model.counted_amount-expected;now=datetime.now(UTC)
    prior=db.cash_counts.count_documents({"session_id":session["_id"],"difference":{"$not":{"$gte":Decimal128("-2"),"$lte":Decimal128("2")}}})
    count_id=db.cash_counts.insert_one({"session_id":session["_id"],"expected":Decimal128(expected),"counted":Decimal128(model.counted_amount),"difference":Decimal128(difference),"reason":model.reason,"actor_id":actor,"counted_at":now,"is_closing":close}).inserted_id
    signal=classify_difference(difference,prior)
    if signal:db.risk_alerts.insert_one({"type":"cash_difference","severity":signal["severity"],"entity_type":"cash_session","entity_id":session["_id"],"evidence":{"cash_count_id":count_id,"difference":Decimal128(difference),"reason":model.reason},"status":"open","message":signal["reason"],"created_at":now})
    if close:db.cash_sessions.update_one({"_id":session["_id"]},{"$set":{"status":"closed","expected_balance":Decimal128(expected),"counted_balance":Decimal128(model.counted_amount),"difference":Decimal128(difference),"close_reason":model.reason,"closed_by":actor,"closed_at":now}})
    return {"id":str(count_id),"status":"closed" if close else "counted","expected":str(expected),"counted":str(model.counted_amount),"difference":str(difference),"alert_created":bool(signal)}


def record_loss(db,model,actor):
    if not ObjectId.is_valid(model.product_id):raise ApiError("Producto no encontrado",404,"product_not_found")
    pid=ObjectId(model.product_id);lot_id=ObjectId(model.lot_id) if model.lot_id and ObjectId.is_valid(model.lot_id) else None;now=datetime.now(UTC)
    with transaction() as session:
        product=db.products.find_one({"_id":pid,"active":True},session=session)
        stock=db.inventory.find_one({"product_id":pid,"location_id":model.location_id},session=session)
        if not product or not stock:raise ApiError("Inventario no encontrado",404,"inventory_not_found")
        if stock["available"]<model.quantity:raise ApiError("Cantidad de merma supera el disponible",409,"insufficient_stock")
        cost=dec(stock.get("average_cost",product.get("average_cost",Decimal128("0"))));total=cost*model.quantity
        db.inventory.update_one({"_id":stock["_id"]},{"$inc":{"on_hand":-model.quantity,"available":-model.quantity},"$set":{"updated_at":now}},session=session)
        if lot_id:
            result=db.lots.update_one({"_id":lot_id,"product_id":pid,"available_quantity":{"$gte":model.quantity}},{"$inc":{"available_quantity":-model.quantity}},session=session)
            if result.modified_count!=1:raise ApiError("Lote sin cantidad suficiente",409,"insufficient_lot_stock")
        lid=db.loss_events.insert_one({"product_id":pid,"location_id":model.location_id,"lot_id":lot_id,"type":model.type,"quantity":model.quantity,"unit_cost":Decimal128(cost),"total_cost":Decimal128(total),"reason":model.reason,"evidence":model.evidence,"actor_id":actor,"occurred_at":now},session=session).inserted_id
        db.inventory_movements.insert_one({"product_id":pid,"location_id":model.location_id,"lot_id":lot_id,"type":"loss","quantity":-model.quantity,"unit_cost":Decimal128(cost),"source_type":"loss_event","source_id":lid,"actor_id":actor,"occurred_at":now},session=session)
    return {"id":str(lid),"total_cost":str(total),"status":"recorded"}


def dashboard(db):
    session=db.cash_sessions.find_one({"status":"open"},sort=[("opened_at",-1)]);open_data=None
    if session:open_data={**to_json(session),"id":str(session["_id"]),"expected_balance":str(session_balance(db,session))}
    pipeline=[{"$group":{"_id":"$type","quantity":{"$sum":"$quantity"},"cost":{"$sum":{"$ifNull":["$total_cost",0]}}}}]
    losses=[{"type":x["_id"],"quantity":x["quantity"],"cost":str(dec(x["cost"]))} for x in db.loss_events.aggregate(pipeline)]
    return {"open_session":open_data,"losses":losses,"open_alerts":db.risk_alerts.count_documents({"status":"open"})}


def list_alerts(db):return [to_json({**x,"id":str(x["_id"])}) for x in db.risk_alerts.find().sort("created_at",-1).limit(100)]


def resolve_alert(db,aid,model,actor):
    if not ObjectId.is_valid(aid):raise ApiError("Alerta no encontrada",404,"alert_not_found")
    result=db.risk_alerts.update_one({"_id":ObjectId(aid),"status":"open"},{"$set":{"status":"resolved","resolution":model.resolution,"resolved_by":actor,"resolved_at":datetime.now(UTC)}})
    if result.modified_count!=1:raise ApiError("Alerta no disponible",409,"alert_state_conflict")
    return {"id":aid,"status":"resolved"}
