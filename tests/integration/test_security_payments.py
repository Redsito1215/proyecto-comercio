from datetime import UTC,datetime
from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def clear(db):
    assert db.name.endswith('_test')
    for name in ('users','auth_sessions','audit_events','payments','refunds','sales','bootstrap_state'):db[name].delete_many({})


def test_bootstrap_login_hashes_password_and_session_token():
    db=get_db();clear(db);client=create_app(testing=True).test_client();password='Una-Clave-Muy-Segura-2026'
    created=client.post('/api/v1/security/bootstrap',json={'name':'Administrador','email':'admin@example.com','password':password});assert created.status_code==201
    user=db.users.find_one();assert user['password_hash']!=password and 'scrypt' in user['password_hash']
    logged=client.post('/api/v1/security/login',json={'email':'admin@example.com','password':password});assert logged.status_code==200;raw=logged.json['data']['access_token']
    assert logged.json['data']['user']['permissions']==['*']
    session=db.auth_sessions.find_one();assert session['token_hash']!=raw and raw not in str(session)
    assert db.audit_events.count_documents({'action':'auth.login'})==1


def test_bootstrap_is_visible_once_and_then_closes():
    db=get_db();clear(db);client=create_app(testing=True).test_client();payload={'name':'Administradora','email':'owner@example.com','password':'Clave-Inicial-Segura-2026'}
    assert client.get('/api/v1/security/bootstrap/status').json['data']['available'] is True
    assert client.post('/api/v1/security/bootstrap',json=payload).status_code==201
    assert client.get('/api/v1/security/bootstrap/status').json['data']['available'] is False
    duplicate=client.post('/api/v1/security/bootstrap',json={**payload,'email':'other@example.com'})
    assert duplicate.status_code==409 and duplicate.json['error']['code']=='bootstrap_closed'


def test_login_returns_effective_permissions_for_cashier():
    db=get_db();clear(db);client=create_app(testing=True).test_client();password='Clave-Cajero-Segura-2026'
    db.roles.update_one({'code':'cashier'},{'$set':{'name':'Cajero','permissions':['products.read','sales.read','sales.write','sales.confirm','payments.write','returns.write'],'system':True}},upsert=True)
    created=client.post('/api/v1/security/users',json={'name':'Cajero de prueba','email':'cashier@example.com','password':password,'roles':['cashier']})
    assert created.status_code==201
    logged=client.post('/api/v1/security/login',json={'email':'cashier@example.com','password':password})
    assert logged.status_code==200
    user=logged.json['data']['user']
    assert user['roles']==['cashier']
    assert user['permissions']==['payments.write','products.read','returns.write','sales.confirm','sales.read','sales.write']


def test_payment_is_idempotent_and_stores_no_pan_or_cvv():
    db=get_db();clear(db);sid=db.sales.insert_one({'number':'VTA-PAY-1','status':'confirmed','total':Decimal128('10'),'created_at':datetime.now(UTC)}).inserted_id;client=create_app(testing=True).test_client()
    payload={'sale_id':str(sid),'method':'card','amount':'10','payment_method_token':'tok_approved_opaque','brand':'Visa','last4':'4242'};headers={'Idempotency-Key':'payment-integration-1'}
    first=client.post('/api/v1/payments',headers=headers,json=payload);second=client.post('/api/v1/payments',headers=headers,json=payload)
    assert first.status_code==201 and second.status_code==201 and first.json['data']['id']==second.json['data']['id']
    payment=db.payments.find_one();serialized=str(payment).lower();assert '4111111111111111' not in serialized and 'cvv' not in serialized and 'tok_approved_opaque' not in serialized
    assert payment['status']=='approved' and db.payments.count_documents({})==1
    receipt=client.get(f"/api/v1/payments/{first.json['data']['id']}/receipt.pdf")
    assert receipt.status_code==200 and receipt.mimetype=='application/pdf' and receipt.data.startswith(b'%PDF')


def test_payment_cannot_exceed_sale_balance():
    db=get_db();clear(db);sid=db.sales.insert_one({'number':'VTA-PAY-2','status':'confirmed','total':Decimal128('5'),'created_at':datetime.now(UTC)}).inserted_id
    response=create_app(testing=True).test_client().post('/api/v1/payments',headers={'Idempotency-Key':'too-much'},json={'sale_id':str(sid),'method':'cash','amount':'6'})
    assert response.status_code==409


def test_pending_sales_lists_only_balance_due():
    db=get_db();clear(db);now=datetime.now(UTC)
    pending=db.sales.insert_one({'number':'VTA-PENDIENTE','status':'confirmed','total':Decimal128('12'),'paid_amount':Decimal128('2'),'created_at':now,'confirmed_at':now}).inserted_id
    db.sales.insert_one({'number':'VTA-PAGADA','status':'confirmed','total':Decimal128('5'),'paid_amount':Decimal128('5'),'created_at':now,'confirmed_at':now})
    response=create_app(testing=True).test_client().get('/api/v1/payments/pending-sales')
    assert response.status_code==200
    assert len(response.json['data'])==1
    assert response.json['data'][0]['id']==str(pending)
    assert response.json['data'][0]['due']=='10'
