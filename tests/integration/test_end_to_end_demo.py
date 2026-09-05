from uuid import uuid4

from bson import ObjectId

from backend.app import create_app
from backend.db import get_db
from scripts.seed_demo import seed


def test_demo_sale_inventory_customer_cash_payment_and_pdf():
    db=get_db()
    assert db.name.endswith('_test')
    seed()
    product=db.products.find_one({'sku':'CAF-001'})
    assert product is not None
    inventory=db.inventory.find_one({'product_id':product['_id'],'location_id':'main'})
    before=inventory['available']
    suffix=uuid4().hex[:8]
    client=create_app(testing=True).test_client()

    customer=client.post('/api/v1/customers',json={'name':'Cliente E2E','email':f'e2e-{suffix}@example.com','birthday':'1990-09-04'})
    assert customer.status_code==201
    customer_id=customer.json['data']['id']
    consent=client.post(f'/api/v1/customers/{customer_id}/consents',json={'channel':'email','granted':True})
    assert consent.status_code==201

    draft=client.post('/api/v1/sales',json={'location_id':'main','customer_id':customer_id,'items':[{'product_id':str(product['_id']),'quantity':1}]})
    assert draft.status_code==201
    sale_id=draft.json['data']['id']
    confirmed=client.post(f'/api/v1/sales/{sale_id}/confirm',headers={'Idempotency-Key':f'sale-{suffix}'})
    assert confirmed.status_code==200
    assert db.inventory.find_one({'product_id':ObjectId(product['_id']),'location_id':'main'})['available']==before-1

    opened=client.post('/api/v1/controls/cash-sessions',json={'register_id':f'CAJA-{suffix}','opening_amount':'100'})
    assert opened.status_code==201
    cash_id=opened.json['data']['id']
    payment=client.post('/api/v1/payments',headers={'Idempotency-Key':f'pay-{suffix}'},json={'sale_id':sale_id,'method':'card','amount':confirmed.json['data']['total'],'payment_method_token':'tok_approved_demo','brand':'Tokenizada','last4':'4242'})
    assert payment.status_code==201 and payment.json['data']['status']=='approved'
    closed=client.post(f'/api/v1/controls/cash-sessions/{cash_id}/close',json={'counted_amount':'100','reason':'Cierre prueba integral'})
    assert closed.status_code==200

    preview=client.post('/api/v1/reports/preview',json={'title':'Prueba integral','sections':['sales','inventory','customers','payments']})
    assert preview.status_code==200
    pdf=client.post('/api/v1/reports/pdf',json={'title':'Prueba integral','sections':['sales','inventory','customers','payments']})
    assert pdf.status_code==200 and pdf.mimetype=='application/pdf' and len(pdf.data)>1000
