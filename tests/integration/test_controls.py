from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def clear(db):
    assert db.name.endswith('_test')
    for name in ('cash_sessions','cash_movements','cash_counts','risk_alerts','products','inventory','loss_events','inventory_movements'):db[name].delete_many({})


def test_cash_count_creates_review_signal_and_closes():
    db=get_db();clear(db);client=create_app(testing=True).test_client()
    opened=client.post('/api/v1/controls/cash-sessions',json={'register_id':'C1','opening_amount':'20'});assert opened.status_code==201;sid=opened.json['data']['id']
    movement=client.post(f'/api/v1/controls/cash-sessions/{sid}/movements',headers={'Idempotency-Key':'cash-1'},json={'type':'deposit','amount':'10','reason':'Ingreso autorizado'});assert movement.status_code==201
    closed=client.post(f'/api/v1/controls/cash-sessions/{sid}/close',json={'counted_amount':'25','reason':'Cierre supervisor'});assert closed.status_code==200
    assert closed.json['data']['difference']=='-5'
    assert db.risk_alerts.find_one({'entity_id':db.cash_sessions.find_one()['_id'],'status':'open'}) is not None


def test_loss_reduces_inventory_transactionally():
    db=get_db();clear(db);pid=db.products.insert_one({'sku':'LOSS-1','name':'Lácteo','active':True,'average_cost':Decimal128('2')}).inserted_id
    db.inventory.insert_one({'product_id':pid,'location_id':'main','on_hand':10,'available':10,'reserved':0,'average_cost':Decimal128('2')})
    response=create_app(testing=True).test_client().post('/api/v1/controls/losses',json={'product_id':str(pid),'location_id':'main','type':'expiry','quantity':3,'reason':'Fecha de caducidad vencida'})
    assert response.status_code==201 and response.json['data']['total_cost']=='6'
    assert db.inventory.find_one({'product_id':pid})['available']==7
    assert db.inventory_movements.find_one({'source_type':'loss_event'})['quantity']==-3
