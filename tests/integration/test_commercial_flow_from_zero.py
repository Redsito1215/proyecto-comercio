from uuid import uuid4

from bson import ObjectId

from backend.app import create_app
from backend.db import get_db


def test_commercial_flow_from_empty_database_to_pdf():
    db=get_db();assert db.name.endswith('_test')
    client=create_app(testing=True).test_client();suffix=uuid4().hex[:8]

    category=client.post('/api/v1/categories',json={'code':f'CAT-{suffix}','name':'Bebidas de prueba'})
    supplier=client.post('/api/v1/suppliers',json={'code':f'SUP-{suffix}','name':'Proveedor de prueba'})
    assert category.status_code==201 and supplier.status_code==201

    product=client.post('/api/v1/products',json={'sku':f'PROD-{suffix}','name':'Producto flujo completo','unit':'unidad','current_price':'5.00','average_cost':'3.00','minimum_margin_percent':'20.00','category_id':category.json['data']['id'],'supplier_id':supplier.json['data']['id'],'perishable':False})
    assert product.status_code==201;product_id=product.json['data']['id']

    order=client.post('/api/v1/purchase-orders',json={'supplier_name':'Proveedor de prueba','location_id':'main','items':[{'product_id':product_id,'quantity':10,'unit_cost':'3.00'}]})
    assert order.status_code==201;order_id=order.json['data']['id']
    receipt=client.post(f'/api/v1/purchase-orders/{order_id}/receipts',headers={'Idempotency-Key':f'receipt-{suffix}'},json={'items':[{'product_id':product_id,'lot_number':f'LOT-{suffix}','quantity':10,'unit_cost':'3.00','expires_at':None}]})
    assert receipt.status_code==201 and receipt.json['data']['status']=='received'

    customer=client.post('/api/v1/customers',json={'name':'Cliente flujo completo','email':f'flow-{suffix}@example.com'})
    assert customer.status_code==201;customer_id=customer.json['data']['id']
    cash=client.post('/api/v1/controls/cash-sessions',json={'register_id':f'CAJA-{suffix}','location_id':'main','opening_amount':'20.00'})
    assert cash.status_code==201;cash_id=cash.json['data']['id']

    draft=client.post('/api/v1/sales',json={'location_id':'main','customer_id':customer_id,'items':[{'product_id':product_id,'quantity':2}]})
    assert draft.status_code==201;sale_id=draft.json['data']['id']
    confirmed=client.post(f'/api/v1/sales/{sale_id}/confirm',headers={'Idempotency-Key':f'sale-{suffix}'})
    assert confirmed.status_code==200 and confirmed.json['data']['total']=='10.00'
    assert db.inventory.find_one({'product_id':ObjectId(product_id),'location_id':'main'})['available']==8

    payment=client.post('/api/v1/payments',headers={'Idempotency-Key':f'payment-{suffix}'},json={'sale_id':sale_id,'method':'cash','amount':'10.00'})
    assert payment.status_code==201 and payment.json['data']['status']=='approved'
    movement=db.cash_movements.find_one({'source_type':'sale','source_id':sale_id})
    assert movement is not None and str(movement['amount'])=='10.00'

    closed=client.post(f'/api/v1/controls/cash-sessions/{cash_id}/close',json={'counted_amount':'30.00','reason':'Cierre exacto del flujo completo'})
    assert closed.status_code==200 and closed.json['data']['difference']=='0.00'

    sections=['sales','inventory','margins','customers','payments']
    preview=client.post('/api/v1/reports/preview',json={'title':'Flujo comercial completo','sections':sections})
    pdf=client.post('/api/v1/reports/pdf',json={'title':'Flujo comercial completo','sections':sections})
    assert preview.status_code==200 and len(preview.json['data']['sections'])==5
    assert pdf.status_code==200 and pdf.mimetype=='application/pdf' and len(pdf.data)>1000
