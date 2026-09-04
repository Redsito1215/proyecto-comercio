from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def test_approved_count_creates_compensating_movement():
    db=get_db(); assert db.name.endswith('_test')
    for name in ('products','inventory','stock_counts','stock_count_items','inventory_movements'): db[name].delete_many({})
    pid=db.products.insert_one({'sku':'CNT-1','name':'Arroz','name_normalized':'arroz','active':True,'barcodes':[]}).inserted_id
    db.inventory.insert_one({'product_id':pid,'location_id':'main','on_hand':10,'reserved':0,'available':10,'average_cost':Decimal128('1')})
    c=create_app(testing=True).test_client(); opened=c.post('/api/v1/stock-counts',json={'location_id':'main','items':[{'product_id':str(pid),'physical_quantity':8,'reason':'Conteo físico'}]})
    assert opened.status_code==201
    approved=c.post(f"/api/v1/stock-counts/{opened.json['data']['id']}/approve")
    assert approved.status_code==200
    assert db.inventory.find_one({'product_id':pid})['available']==8
    assert db.inventory_movements.find_one({'type':'count_adjustment'})['quantity']==-2
