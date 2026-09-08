import hashlib
from datetime import UTC,datetime
from decimal import Decimal
from bson import Decimal128,ObjectId

from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.db import transaction
from backend.modules.payments.gateway import LocalSandboxGateway
from backend.modules.security.services import audit


def dec(value):return value.to_decimal() if isinstance(value,Decimal128) else Decimal(str(value))


def serialize(row):
    clean=to_json(row);clean["id"]=str(clean.pop("_id"));return clean


def create_payment(db,model,key,actor):
    prior=db.payments.find_one({"idempotency_key":key})
    if prior:return serialize(prior)
    if not ObjectId.is_valid(model.sale_id):raise ApiError("Venta no encontrada",404,"sale_not_found")
    gateway=LocalSandboxGateway();now=datetime.now(UTC)
    if model.method=="cash":result={"status":"approved","reference":f"cash_{key[:16]}","message":"Efectivo registrado"}
    else:result=gateway.charge(model.payment_method_token,model.amount)
    token_ref=hashlib.sha256(model.payment_method_token.encode()).hexdigest()[:24] if model.payment_method_token else None
    with transaction() as session:
        prior=db.payments.find_one({"idempotency_key":key},session=session)
        if prior:return serialize(prior)
        sale=db.sales.find_one({"_id":ObjectId(model.sale_id),"status":{"$in":["confirmed","partially_returned"]}},session=session)
        if not sale:raise ApiError("Venta no disponible para pago",409,"sale_state_conflict")
        cash_session=None
        if model.method=="cash":
            cash_session=db.cash_sessions.find_one({"status":"open","location_id":sale.get("location_id","main")},session=session)
            if not cash_session:raise ApiError("Abra una caja antes de registrar un pago en efectivo",409,"cash_session_required")
        approved=dec(sale.get("paid_amount",0));due=dec(sale["total"])-approved
        if model.amount>due:raise ApiError("El importe supera el saldo pendiente",409,"payment_exceeds_due")
        doc={"sale_id":sale["_id"],"method":model.method,"amount":Decimal128(model.amount),"status":result["status"],"provider":gateway.name if model.method!="cash" else "internal-cash","provider_production_ready":False if model.method!="cash" else None,"provider_reference":result["reference"],"method_ref":token_ref,"brand":model.brand,"last4":model.last4,"idempotency_key":key,"actor_id":actor,"created_at":now,"processed_at":now}
        pid=db.payments.insert_one(doc,session=session).inserted_id
        if result["status"]=="approved":
            paid=approved+model.amount
            update={"$set":{"paid_amount":Decimal128(paid)}}
            if paid==dec(sale["total"]):update["$set"].update({"payment_status":"paid","paid_at":now})
            db.sales.update_one({"_id":sale["_id"]}, {**update,"$inc":{"version":1}},session=session)
            if model.method=="cash":
                db.cash_movements.insert_one({"session_id":cash_session["_id"],"type":"sale","direction":"in","amount":Decimal128(model.amount),"source_type":"sale","source_id":model.sale_id,"reason":"Pago en efectivo registrado automáticamente","idempotency_key":f"cash-payment-{key}","actor_id":actor,"occurred_at":now},session=session)
    audit(db,actor,"payment.process","payment",pid,result["status"],{"method":model.method,"amount":str(model.amount),"provider":doc["provider"]})
    return serialize({"_id":pid,**doc})


def list_payments(db):return [serialize(x) for x in db.payments.find().sort("created_at",-1).limit(100)]


def list_payable_sales(db):
    rows=[]
    for sale in db.sales.find({"status":{"$in":["confirmed","partially_returned"]}}).sort("confirmed_at",-1).limit(200):
        total=dec(sale.get("total",0));paid=dec(sale.get("paid_amount",0));due=total-paid
        if due<=0:continue
        customer_id=sale.get("customer_id");customer=None
        if customer_id:
            identifier=customer_id if isinstance(customer_id,ObjectId) else ObjectId(customer_id) if ObjectId.is_valid(str(customer_id)) else None
            if identifier:customer=db.customers.find_one({"_id":identifier})
        rows.append({"id":str(sale["_id"]),"number":sale.get("number","Venta"),"customer":(customer or {}).get("name","Consumidor final"),"total":str(total),"paid_amount":str(paid),"due":str(due),"confirmed_at":to_json(sale.get("confirmed_at") or sale.get("created_at"))})
    return rows


def receipt_data(db,payment_id):
    if not ObjectId.is_valid(payment_id):raise ApiError("Pago no encontrado",404,"payment_not_found")
    payment=db.payments.find_one({"_id":ObjectId(payment_id),"status":{"$in":["approved","refunded"]}})
    if not payment:raise ApiError("Pago no disponible para comprobante",404,"payment_not_found")
    sale=db.sales.find_one({"_id":payment["sale_id"]})
    if not sale:raise ApiError("Venta no encontrada",404,"sale_not_found")
    customer_id=sale.get("customer_id");customer=None
    if customer_id:
        identifier=customer_id if isinstance(customer_id,ObjectId) else ObjectId(customer_id) if ObjectId.is_valid(str(customer_id)) else None
        if identifier:customer=db.customers.find_one({"_id":identifier})
    items=[]
    for line in db.sale_items.find({"sale_id":sale["_id"]}):
        product=db.products.find_one({"_id":line["product_id"]}) or {};price=dec(line.get("unit_price",line.get("price",0)));quantity=line.get("quantity",0)
        items.append({"name":product.get("name",line.get("product_name","Producto")),"sku":product.get("sku",line.get("sku","-")),"quantity":quantity,"unit_price":f"${price:.2f}","line_total":f"${(price*quantity):.2f}"})
    total=dec(sale.get("total",0));paid=dec(sale.get("paid_amount",0));settings=db.settings.find_one({"key":"business"}) or {};occurred=payment.get("processed_at") or payment.get("created_at")
    methods={"cash":"Efectivo","card":"Tarjeta tokenizada","wallet":"Billetera electrónica","transfer":"Transferencia"}
    return {"business_name":settings.get("business_name","Comercio Inteligente"),"sale_number":sale.get("number","Venta"),"sale_date":to_json(sale.get("confirmed_at") or sale.get("created_at"))[:19].replace("T"," "),"customer_name":(customer or {}).get("name","Consumidor final"),"customer_document":(customer or {}).get("document","No registrado"),"payment_id":str(payment["_id"]),"payment_method":methods.get(payment.get("method"),payment.get("method","-")),"items":items,"sale_total":f"${total:.2f}","payment_amount":f"${dec(payment['amount']):.2f}","remaining_due":f"${max(total-paid,Decimal('0')):.2f}","generated_at":to_json(occurred)[:19].replace("T"," ")}


def refund_payment(db,pid,model,key,actor):
    prior=db.refunds.find_one({"idempotency_key":key})
    if prior:return serialize(prior)
    if not ObjectId.is_valid(pid):raise ApiError("Pago no encontrado",404,"payment_not_found")
    gateway=LocalSandboxGateway();now=datetime.now(UTC)
    with transaction() as session:
        prior=db.refunds.find_one({"idempotency_key":key},session=session)
        if prior:return serialize(prior)
        payment=db.payments.find_one({"_id":ObjectId(pid),"status":"approved"},session=session)
        if not payment:raise ApiError("Pago no disponible para reembolso",409,"payment_state_conflict")
        refunded=dec(payment.get("refunded_amount",0))
        if refunded+model.amount>dec(payment["amount"]):raise ApiError("El reembolso supera el importe aprobado",409,"refund_exceeds_payment")
        result=gateway.refund(payment["provider_reference"],model.amount)
        doc={"payment_id":payment["_id"],"sale_id":payment["sale_id"],"amount":Decimal128(model.amount),"reason":model.reason,"status":result["status"],"provider_reference":result["reference"],"idempotency_key":key,"actor_id":actor,"created_at":now}
        rid=db.refunds.insert_one(doc,session=session).inserted_id
        if result["status"]=="approved":
            total_refunded=refunded+model.amount;update={"refunded_amount":Decimal128(total_refunded)}
            if total_refunded==dec(payment["amount"]):update.update({"status":"refunded","refunded_at":now})
            db.payments.update_one({"_id":payment["_id"],"refunded_amount":payment.get("refunded_amount")},{"$set":update},session=session)
    audit(db,actor,"payment.refund","refund",rid,result["status"],{"amount":str(model.amount)})
    return serialize({"_id":rid,**doc})
