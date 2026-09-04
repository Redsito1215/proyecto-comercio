import hashlib
from datetime import UTC,datetime
from decimal import Decimal
from bson import Decimal128,ObjectId

from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.modules.payments.gateway import LocalSandboxGateway
from backend.modules.security.services import audit


def dec(value):return value.to_decimal() if isinstance(value,Decimal128) else Decimal(str(value))


def serialize(row):
    clean=to_json(row);clean["id"]=str(clean.pop("_id"));return clean


def create_payment(db,model,key,actor):
    prior=db.payments.find_one({"idempotency_key":key})
    if prior:return serialize(prior)
    if not ObjectId.is_valid(model.sale_id):raise ApiError("Venta no encontrada",404,"sale_not_found")
    sale=db.sales.find_one({"_id":ObjectId(model.sale_id),"status":{"$in":["confirmed","partially_returned"]}})
    if not sale:raise ApiError("Venta no disponible para pago",409,"sale_state_conflict")
    approved=sum((dec(x["amount"]) for x in db.payments.find({"sale_id":sale["_id"],"status":"approved"})),Decimal("0"));due=dec(sale["total"])-approved
    if model.amount>due:raise ApiError("El importe supera el saldo pendiente",409,"payment_exceeds_due")
    gateway=LocalSandboxGateway();now=datetime.now(UTC)
    if model.method=="cash":result={"status":"approved","reference":f"cash_{key[:16]}","message":"Efectivo registrado"}
    else:result=gateway.charge(model.payment_method_token,model.amount)
    token_ref=hashlib.sha256(model.payment_method_token.encode()).hexdigest()[:24] if model.payment_method_token else None
    doc={"sale_id":sale["_id"],"method":model.method,"amount":Decimal128(model.amount),"status":result["status"],"provider":gateway.name if model.method!="cash" else "internal-cash","provider_production_ready":False if model.method!="cash" else None,"provider_reference":result["reference"],"method_ref":token_ref,"brand":model.brand,"last4":model.last4,"idempotency_key":key,"actor_id":actor,"created_at":now,"processed_at":now}
    pid=db.payments.insert_one(doc).inserted_id
    if result["status"]=="approved" and approved+model.amount==dec(sale["total"]):db.sales.update_one({"_id":sale["_id"]},{"$set":{"payment_status":"paid","paid_at":now}})
    audit(db,actor,"payment.process","payment",pid,result["status"],{"method":model.method,"amount":str(model.amount),"provider":doc["provider"]})
    return serialize({"_id":pid,**doc})


def list_payments(db):return [serialize(x) for x in db.payments.find().sort("created_at",-1).limit(100)]


def refund_payment(db,pid,model,key,actor):
    prior=db.refunds.find_one({"idempotency_key":key})
    if prior:return serialize(prior)
    if not ObjectId.is_valid(pid):raise ApiError("Pago no encontrado",404,"payment_not_found")
    payment=db.payments.find_one({"_id":ObjectId(pid),"status":"approved"})
    if not payment:raise ApiError("Pago no disponible para reembolso",409,"payment_state_conflict")
    refunded=sum((dec(x["amount"]) for x in db.refunds.find({"payment_id":payment["_id"],"status":"approved"})),Decimal("0"))
    if refunded+model.amount>dec(payment["amount"]):raise ApiError("El reembolso supera el importe aprobado",409,"refund_exceeds_payment")
    gateway=LocalSandboxGateway();result=gateway.refund(payment["provider_reference"],model.amount);now=datetime.now(UTC)
    doc={"payment_id":payment["_id"],"sale_id":payment["sale_id"],"amount":Decimal128(model.amount),"reason":model.reason,"status":result["status"],"provider_reference":result["reference"],"idempotency_key":key,"actor_id":actor,"created_at":now}
    rid=db.refunds.insert_one(doc).inserted_id
    if refunded+model.amount==dec(payment["amount"]):db.payments.update_one({"_id":payment["_id"]},{"$set":{"status":"refunded","refunded_at":now}})
    audit(db,actor,"payment.refund","refund",rid,result["status"],{"amount":str(model.amount)})
    return serialize({"_id":rid,**doc})
