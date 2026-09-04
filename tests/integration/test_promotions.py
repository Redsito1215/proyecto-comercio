from datetime import UTC,datetime,timedelta
from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def clear(db):
    assert db.name.endswith('_test')
    for name in ('products','customers','customer_consents','customer_segments','churn_signals','promotions','promotion_audience','promotion_coupons','notification_outbox'):db[name].delete_many({})


def test_promotion_respects_consent_and_control():
    db=get_db();clear(db);now=datetime.now(UTC)
    pid=db.products.insert_one({'sku':'PROMO-1','name':'Producto rentable','name_normalized':'producto rentable','active':True,'current_price':Decimal128('10'),'average_cost':Decimal128('4'),'minimum_margin_percent':Decimal128('20')}).inserted_id
    consented=db.customers.insert_one({'name':'Cliente acepta','status':'active'}).inserted_id
    excluded=db.customers.insert_one({'name':'Cliente sin permiso','status':'active'}).inserted_id
    db.customer_consents.insert_one({'customer_id':consented,'purpose':'marketing','channel':'email','status':'granted'})
    client=create_app(testing=True).test_client();payload={'name':'Campaña rentable','discount_percent':'10','product_ids':[str(pid)],'segment':'all','channel':'email','valid_from':(now-timedelta(minutes=1)).isoformat(),'valid_until':(now+timedelta(days=7)).isoformat(),'control_percent':10,'usage_limit':1}
    created=client.post('/api/v1/promotions',json=payload);assert created.status_code==201;promotion_id=created.json['data']['id']
    audience=client.post(f'/api/v1/promotions/{promotion_id}/audience');assert audience.status_code==200
    assert db.promotion_audience.find_one({'customer_id':excluded})['eligible'] is False
    activated=client.post(f'/api/v1/promotions/{promotion_id}/activate');assert activated.status_code==200
    treatment=db.promotion_audience.count_documents({'promotion_id':db.promotions.find_one()['_id'],'group':'treatment'})
    assert db.notification_outbox.count_documents({})==treatment


def test_unprofitable_promotion_is_rejected():
    db=get_db();clear(db);now=datetime.now(UTC)
    pid=db.products.insert_one({'sku':'PROMO-2','name':'Margen corto','name_normalized':'margen corto','active':True,'current_price':Decimal128('10'),'average_cost':Decimal128('8'),'minimum_margin_percent':Decimal128('20')}).inserted_id
    payload={'name':'Descuento ruinoso','discount_percent':'20','product_ids':[str(pid)],'valid_from':now.isoformat(),'valid_until':(now+timedelta(days=2)).isoformat()}
    assert create_app(testing=True).test_client().post('/api/v1/promotions',json=payload).status_code==409
