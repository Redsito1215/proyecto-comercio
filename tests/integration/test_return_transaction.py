from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def test_return_restock_only_fit_units_and_records_damage():
    db=get_db(); assert db.name.endswith('_test')
    for n in ('products','inventory','sales','sale_items','returns','return_items','loss_events','inventory_movements'): db[n].delete_many({})
    pid=db.products.insert_one({'sku':'RET-1','name':'Yogur','name_normalized':'yogur','active':True,'barcodes':[]}).inserted_id
    db.inventory.insert_one({'product_id':pid,'location_id':'main','on_hand':8,'reserved':0,'available':8,'average_cost':Decimal128('1')})
    sid=db.sales.insert_one({'number':'VTA-R1','location_id':'main','status':'confirmed','total':Decimal128('6')}).inserted_id
    db.sale_items.insert_one({'sale_id':sid,'product_id':pid,'name':'Yogur','quantity':3,'unit_price':Decimal128('2'),'unit_cost':Decimal128('1')})
    c=create_app(testing=True).test_client(); r=c.post('/api/v1/returns',headers={'Idempotency-Key':'return-1'},json={'sale_id':str(sid),'items':[{'product_id':str(pid),'fit_quantity':1,'damaged_quantity':1,'reason':'Producto dañado'}]})
    assert r.status_code==201
    assert db.inventory.find_one({'product_id':pid})['available']==9
    assert db.loss_events.find_one({'product_id':pid})['quantity']==1
