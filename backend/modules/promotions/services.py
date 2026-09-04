from datetime import UTC,datetime
from decimal import Decimal,ROUND_HALF_UP
from bson import Decimal128,ObjectId

from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.modules.promotions.eligibility import eligible_for_segment,experimental_group
from backend.db import transaction


def dec(value): return value.to_decimal() if isinstance(value,Decimal128) else Decimal(str(value))


def validate_margin(products,discount):
    results=[]
    for product in products:
        price=dec(product["current_price"]);cost=dec(product.get("average_cost",Decimal128("0")));after=(price*(Decimal("100")-discount)/100).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
        margin=((after-cost)/after*100).quantize(Decimal("0.01")) if after else Decimal("-100")
        minimum=dec(product.get("minimum_margin_percent",Decimal128("20")))
        results.append({"product_id":str(product["_id"]),"name":product["name"],"price_after":str(after),"margin_after":str(margin),"minimum_margin":str(minimum),"allowed":margin>=minimum})
    return results


def create_promotion(db,model,actor):
    ids=[ObjectId(x) for x in model.product_ids if ObjectId.is_valid(x)]
    if len(ids)!=len(model.product_ids):raise ApiError("Producto inválido",422,"validation_error")
    products=list(db.products.find({"_id":{"$in":ids},"active":True}))
    if len(products)!=len(ids):raise ApiError("Producto no encontrado",404,"product_not_found")
    margin=validate_margin(products,model.discount_percent)
    if not all(x["allowed"] for x in margin):raise ApiError("El descuento reduce un producto bajo su margen mínimo",409,"minimum_margin_violation")
    now=datetime.now(UTC);doc=model.model_dump();doc.update({"discount_percent":Decimal128(model.discount_percent),"product_ids":ids,"status":"draft","margin_simulation":margin,"actor_id":actor,"created_at":now,"updated_at":now})
    pid=db.promotions.insert_one(doc).inserted_id
    return {"id":str(pid),**to_json(doc)}


def list_promotions(db):return [to_json({**p,"id":str(p["_id"])}) for p in db.promotions.find().sort("created_at",-1)]


def get_promotion(db,pid,statuses=None):
    if not ObjectId.is_valid(pid):raise ApiError("Promoción no encontrada",404,"promotion_not_found")
    query={"_id":ObjectId(pid)}
    if statuses:query["status"]={"$in":statuses}
    promotion=db.promotions.find_one(query)
    if not promotion:raise ApiError("Promoción no disponible",409,"promotion_state_conflict")
    return promotion


def prepare_audience(db,pid):
    promotion=get_promotion(db,pid,["draft","audience_ready"]);now=datetime.now(UTC);db.promotion_audience.delete_many({"promotion_id":promotion["_id"]});docs=[]
    for customer in db.customers.find({"status":"active"}):
        consent=db.customer_consents.find_one({"customer_id":customer["_id"],"purpose":"marketing","channel":promotion["channel"],"status":"granted"})
        segment=db.customer_segments.find_one({"customer_id":customer["_id"]}) or {};churn=db.churn_signals.find_one({"customer_id":customer["_id"]}) or {}
        eligible,reason=eligible_for_segment(promotion["segment"],segment,churn)
        if not consent:eligible=False;reason="Sin consentimiento vigente para el canal"
        group=experimental_group(pid,str(customer["_id"]),promotion["control_percent"]) if eligible else "excluded"
        docs.append({"promotion_id":promotion["_id"],"customer_id":customer["_id"],"customer_name":customer["name"],"eligible":eligible,"reason":reason,"group":group,"consent_snapshot":bool(consent),"assigned_at":now})
    if docs:db.promotion_audience.insert_many(docs)
    db.promotions.update_one({"_id":promotion["_id"]},{"$set":{"status":"audience_ready","updated_at":now}})
    return {"eligible":sum(x["eligible"] for x in docs),"treatment":sum(x["group"]=="treatment" for x in docs),"control":sum(x["group"]=="control" for x in docs),"excluded":sum(not x["eligible"] for x in docs)}


def activate(db,pid,actor):
    promotion=get_promotion(db,pid,["audience_ready"]);now=datetime.now(UTC)
    comparable_now=now.replace(tzinfo=None) if promotion["valid_from"].tzinfo is None else now
    if not(promotion["valid_from"]<=comparable_now<=promotion["valid_until"]):raise ApiError("La promoción no está dentro de su vigencia",409,"promotion_outside_validity")
    treatment=list(db.promotion_audience.find({"promotion_id":promotion["_id"],"eligible":True,"group":"treatment"}))
    for row in treatment:
        code=f"PR-{str(promotion['_id'])[-5:].upper()}-{str(row['customer_id'])[-5:].upper()}"
        coupon=db.promotion_coupons.find_one_and_update({"promotion_id":promotion["_id"],"customer_id":row["customer_id"]},{"$setOnInsert":{"code":code,"status":"active","usage_limit":promotion["usage_limit"],"usage_count":0,"valid_from":promotion["valid_from"],"valid_until":promotion["valid_until"],"created_at":now}},upsert=True,return_document=True)
        db.notification_outbox.update_one({"promotion_id":promotion["_id"],"customer_id":row["customer_id"]},{"$setOnInsert":{"channel":promotion["channel"],"status":"pending","payload":{"coupon_code":coupon["code"],"promotion":promotion["name"]},"created_at":now}},upsert=True)
    db.promotions.update_one({"_id":promotion["_id"]},{"$set":{"status":"active","activated_by":actor,"activated_at":now,"updated_at":now}})
    return {"status":"active","notifications_pending":len(treatment)}


def redeem(db,model,actor):
    now=datetime.now(UTC)
    if not ObjectId.is_valid(model.sale_id):raise ApiError("Venta no encontrada",404,"sale_not_found")
    with transaction() as session:
        coupon=db.promotion_coupons.find_one({"code":model.code,"status":"active","valid_from":{"$lte":now},"valid_until":{"$gte":now}},session=session)
        if not coupon:raise ApiError("Cupón inválido o vencido",409,"coupon_invalid")
        if coupon["usage_count"]>=coupon["usage_limit"]:raise ApiError("Cupón sin usos disponibles",409,"coupon_limit")
        sale=db.sales.find_one({"_id":ObjectId(model.sale_id),"customer_id":{"$in":[coupon["customer_id"],str(coupon["customer_id"])]},"status":"draft"},session=session)
        if not sale:raise ApiError("El cupón debe aplicarse a la venta del cliente antes de confirmarla",409,"coupon_customer_mismatch")
        prior=db.promotion_redemptions.find_one({"coupon_id":coupon["_id"],"sale_id":sale["_id"]},session=session)
        if prior:return {"id":str(prior["_id"]),"status":"redeemed"}
        promotion=db.promotions.find_one({"_id":coupon["promotion_id"]},session=session)
        eligible_total=sum((dec(row["line_total"]) for row in db.sale_items.find({"sale_id":sale["_id"],"product_id":{"$in":promotion["product_ids"]}},session=session)),Decimal("0"))
        if not eligible_total:raise ApiError("La venta no contiene productos de la promoción",409,"coupon_product_mismatch")
        discount=(eligible_total*dec(promotion["discount_percent"])/100).quantize(Decimal("0.01"));net=dec(sale["total"])-discount
        rid=db.promotion_redemptions.insert_one({"promotion_id":promotion["_id"],"coupon_id":coupon["_id"],"customer_id":coupon["customer_id"],"sale_id":sale["_id"],"discount_amount":Decimal128(discount),"actor_id":actor,"redeemed_at":now},session=session).inserted_id
        db.sales.update_one({"_id":sale["_id"]},{"$set":{"discount_total":Decimal128(discount),"total":Decimal128(net),"promotion_id":promotion["_id"],"updated_at":now}},session=session)
        db.promotion_coupons.update_one({"_id":coupon["_id"]},{"$inc":{"usage_count":1},"$set":{"status":"redeemed" if coupon["usage_count"]+1>=coupon["usage_limit"] else "active"}},session=session)
    return {"id":str(rid),"status":"redeemed","discount_amount":str(discount)}


def metrics(db,pid):
    promotion=get_promotion(db,pid);audience=list(db.promotion_audience.find({"promotion_id":promotion["_id"],"eligible":True}));groups={"treatment":[],"control":[]}
    for row in audience:groups[row["group"]].append(row["customer_id"])
    output={}
    for name,ids in groups.items():
        sales=list(db.sales.find({"customer_id":{"$in":ids+[str(x) for x in ids]},"status":{"$in":["confirmed","partially_returned"]},"confirmed_at":{"$gte":promotion["valid_from"],"$lte":promotion["valid_until"]}}))
        buyers=len({str(x["customer_id"]) for x in sales});eligible=len(ids);revenue=sum((dec(x["total"]) for x in sales),Decimal("0"))
        output[name]={"eligible":eligible,"buyers":buyers,"conversion":round(buyers/eligible,4) if eligible else 0,"revenue":str(revenue)}
    output["incremental_conversion"]=round(output["treatment"]["conversion"]-output["control"]["conversion"],4)
    return output
