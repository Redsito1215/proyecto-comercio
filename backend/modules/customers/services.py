from datetime import UTC,datetime,timedelta
from decimal import Decimal
from bson import Decimal128,ObjectId
from pymongo.errors import DuplicateKeyError
from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.modules.customers.analytics import calculate_churn_signal,calculate_customer_value


def create_customer(db,model,actor):
    now=datetime.now(UTC);email=model.email.lower().strip() if model.email else None;doc=model.document.strip() if model.document else None
    payload={'name':model.name.strip(),'email':model.email,'email_normalized':email,'document':doc,'phone':model.phone,'birthday':datetime.combine(model.birthday,datetime.min.time(),UTC) if model.birthday else None,'status':'active','created_at':now,'updated_at':now,'actor_id':actor}
    try:cid=db.customers.insert_one(payload).inserted_id
    except DuplicateKeyError as e:raise ApiError('Ya existe un cliente con ese email o documento',409,'duplicate_customer') from e
    return {'id':str(cid),**to_json(payload)}


def record_consent(db,cid,model,actor):
    if not ObjectId.is_valid(cid) or not db.customers.find_one({'_id':ObjectId(cid)}):raise ApiError('Cliente no encontrado',404,'customer_not_found')
    now=datetime.now(UTC);db.customer_consents.update_one({'customer_id':ObjectId(cid),'purpose':model.purpose,'channel':model.channel},{'$set':{'status':'granted' if model.granted else 'revoked','source':model.source,'actor_id':actor,'updated_at':now,'granted_at':now if model.granted else None,'revoked_at':None if model.granted else now}},upsert=True)
    return {'status':'granted' if model.granted else 'revoked'}


def recalculate_customer(db,cid):
    oid=ObjectId(cid);sales=list(db.sales.find({'customer_id':{'$in':[cid,oid]},'status':{'$in':['confirmed','partially_returned']}}).sort('confirmed_at',1));purchases=[]
    for sale in sales:
        items=list(db.sale_items.find({'sale_id':sale['_id']}));spend=sum((i['line_total'].to_decimal() for i in items),Decimal('0'));margin=sum(((i['unit_price'].to_decimal()-i.get('unit_cost',Decimal128('0')).to_decimal())*i['quantity'] for i in items),Decimal('0'));purchases.append({'date':(sale.get('confirmed_at') or sale.get('created_at')).date(),'spend':spend,'margin':margin})
    value=calculate_customer_value(purchases);churn=calculate_churn_signal([p['date'] for p in purchases])
    now=datetime.now(UTC);db.customer_segments.update_one({'customer_id':oid},{'$set':{**value,'spend':Decimal128(value['spend']),'margin':Decimal128(value['margin']),'calculated_at':now}},upsert=True);db.churn_signals.update_one({'customer_id':oid},{'$set':{**churn,'calculated_at':now}},upsert=True)
    return {'value':to_json(value),'churn':to_json(churn)}


def customer_profile(db,cid):
    if not ObjectId.is_valid(cid):raise ApiError('Cliente no encontrado',404,'customer_not_found')
    customer=db.customers.find_one({'_id':ObjectId(cid)}); 
    if not customer:raise ApiError('Cliente no encontrado',404,'customer_not_found')
    customer=to_json(customer);customer['id']=customer.pop('_id');customer['segment']=to_json(db.customer_segments.find_one({'customer_id':ObjectId(cid)}) or {});customer['churn']=to_json(db.churn_signals.find_one({'customer_id':ObjectId(cid)}) or {});return customer


def birthday_coupon(db,cid,actor):
    customer=db.customers.find_one({'_id':ObjectId(cid)}) if ObjectId.is_valid(cid) else None
    consent=db.customer_consents.find_one({'customer_id':ObjectId(cid),'purpose':'marketing','status':'granted'}) if customer else None
    if not customer:raise ApiError('Cliente no encontrado',404,'customer_not_found')
    if not consent:raise ApiError('El cliente no tiene consentimiento vigente',409,'consent_required')
    now=datetime.now(UTC);code=f"CUM-{str(customer['_id'])[-6:].upper()}-{now.year}";db.coupons.update_one({'code':code},{'$setOnInsert':{'customer_id':customer['_id'],'purpose':'birthday','discount_percent':10,'usage_limit':1,'usage_count':0,'status':'active','valid_from':now,'valid_until':now+timedelta(days=30),'created_by':actor}},upsert=True);return {'code':code,'valid_until':(now+timedelta(days=30)).isoformat()}
