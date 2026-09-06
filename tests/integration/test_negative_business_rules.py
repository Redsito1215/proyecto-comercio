from datetime import UTC,datetime

from bson import Decimal128,ObjectId
from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.db import get_db


def product_with_stock(db,available=1):
    product_id=db.products.insert_one({'sku':'NEG-001','name':'Producto reglas negativas','name_normalized':'producto reglas negativas','unit':'unidad','current_price':Decimal128('5.00'),'average_cost':Decimal128('3.00'),'minimum_margin_percent':Decimal128('20.00'),'perishable':False,'active':True,'created_at':datetime.now(UTC)}).inserted_id
    db.inventory.insert_one({'product_id':product_id,'location_id':'main','on_hand':available,'available':available,'reserved':0,'average_cost':Decimal128('3.00'),'updated_at':datetime.now(UTC)})
    return product_id


def confirmed_sale(db,product_id,total='5.00'):
    sale_id=db.sales.insert_one({'number':f'VTA-{ObjectId()}','location_id':'main','status':'confirmed','subtotal':Decimal128(total),'total':Decimal128(total),'paid_amount':Decimal128('0'),'created_at':datetime.now(UTC),'confirmed_at':datetime.now(UTC),'version':1}).inserted_id
    db.sale_items.insert_one({'sale_id':sale_id,'product_id':product_id,'sku':'NEG-001','name':'Producto reglas negativas','quantity':1,'unit_price':Decimal128('5.00'),'line_total':Decimal128(total),'unit_cost':Decimal128('3.00')})
    return sale_id


def test_negative_rules_reject_without_partial_changes():
    db=get_db();assert db.name.endswith('_test');client=create_app(testing=True).test_client();product_id=product_with_stock(db,1)

    draft=client.post('/api/v1/sales',json={'location_id':'main','items':[{'product_id':str(product_id),'quantity':2}]})
    sale_id=draft.json['data']['id'];rejected=client.post(f'/api/v1/sales/{sale_id}/confirm',headers={'Idempotency-Key':'negative-insufficient-stock'})
    assert rejected.status_code==409 and rejected.json['error']['code']=='insufficient_stock'
    assert db.inventory.find_one({'product_id':product_id})['available']==1
    assert db.sales.find_one({'_id':ObjectId(sale_id)})['status']=='draft'
    assert db.inventory_movements.count_documents({'source_id':ObjectId(sale_id)})==0

    payable_id=confirmed_sale(db,product_id)
    no_cash=client.post('/api/v1/payments',headers={'Idempotency-Key':'negative-no-cash'},json={'sale_id':str(payable_id),'method':'cash','amount':'5.00'})
    assert no_cash.status_code==409 and no_cash.json['error']['code']=='cash_session_required'
    assert db.payments.count_documents({'sale_id':payable_id})==0

    opened=client.post('/api/v1/controls/cash-sessions',json={'register_id':'CAJA-NEG','location_id':'main','opening_amount':'10.00'});cash_id=opened.json['data']['id']
    headers={'Idempotency-Key':'negative-cash-retry'};payload={'sale_id':str(payable_id),'method':'cash','amount':'5.00'}
    first=client.post('/api/v1/payments',headers=headers,json=payload);second=client.post('/api/v1/payments',headers=headers,json=payload)
    assert first.status_code==201 and second.status_code==201 and first.json['data']['id']==second.json['data']['id']
    assert db.payments.count_documents({'sale_id':payable_id})==1
    assert db.cash_movements.count_documents({'source_type':'sale','source_id':str(payable_id)})==1

    invalid_return=client.post('/api/v1/returns',headers={'Idempotency-Key':'negative-return'},json={'sale_id':str(payable_id),'items':[{'product_id':str(product_id),'fit_quantity':2,'damaged_quantity':0,'reason':'Cantidad mayor a la vendida'}]})
    assert invalid_return.status_code==409 and invalid_return.json['error']['code']=='return_quantity_conflict'
    assert db.returns.count_documents({'sale_id':payable_id})==0

    excessive_loss=client.post('/api/v1/controls/losses',json={'product_id':str(product_id),'location_id':'main','type':'damage','quantity':2,'reason':'Cantidad mayor al inventario'})
    assert excessive_loss.status_code==409 and excessive_loss.json['error']['code']=='insufficient_stock'
    assert db.loss_events.count_documents({'product_id':product_id})==0
    closed=client.post(f'/api/v1/controls/cash-sessions/{cash_id}/close',json={'counted_amount':'15.00','reason':'Cierre de prueba negativa'})
    assert closed.status_code==200 and closed.json['data']['difference']=='0.00'


def test_authentication_and_permissions_are_enforced_without_test_bypass():
    db=get_db();assert db.name.endswith('_test')
    db.roles.update_one({'code':'auditor'},{'$set':{'name':'Auditor','permissions':['products.read','reports.read'],'system':True}},upsert=True)
    password='Clave-Auditor-Segura-2026';user_id=db.users.insert_one({'name':'Auditor de prueba','email':'auditor@example.com','email_normalized':'auditor@example.com','password_hash':generate_password_hash(password,method='scrypt'),'roles':['auditor'],'status':'active','failed_attempts':0,'locked_until':None,'created_at':datetime.now(UTC)}).inserted_id
    app=create_app(testing=False);client=app.test_client()
    assert client.post('/api/v1/products',json={}).status_code==401
    login=client.post('/api/v1/security/login',json={'email':'auditor@example.com','password':password});token=login.json['data']['access_token']
    denied=client.post('/api/v1/products',headers={'Authorization':f'Bearer {token}'},json={})
    assert denied.status_code==403 and denied.json['error']=={'code':'forbidden','message':'No tiene permiso para esta operación'}
    denied_audit=db.audit_events.find_one({'actor_id':str(user_id),'action':'security.permission_denied'})
    assert denied_audit['outcome']=='blocked' and denied_audit['metadata']['permission']=='products.write'
    allowed=client.get('/api/v1/products',headers={'Authorization':f'Bearer {token}'})
    assert allowed.status_code==200
    assert db.audit_events.count_documents({'actor_id':str(user_id),'action':'auth.login'})==1
