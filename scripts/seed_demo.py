from datetime import UTC,datetime,timedelta
from decimal import Decimal
from bson import Decimal128

from backend.db import get_db
from backend.modules.core.repositories import insert_product


def seed():
    db=get_db()
    products=[("CAF-001","Café molido premium","8.50","4.20",False,"780000001"), ("LEC-001","Leche entera 1L","1.60","1.05",True,"780000002"), ("PAT-001","Patatas artesanas","2.40","1.10",True,"780000003"), ("CER-000","Cerveza sin alcohol","1.90","0.85",False,"780000004"), ("BOL-001","Bollos de mantequilla","2.10","0.95",True,"780000005")]
    now=datetime.now(UTC)
    created=0
    for sku,name,price,cost,perishable,barcode in products:
        if db.products.find_one({"sku":sku}):continue
        pid=insert_product(db,{"sku":sku,"name":name,"unit":"unidad","barcode":barcode,"current_price":Decimal128(Decimal(price)),"average_cost":Decimal128(Decimal(cost)),"perishable":perishable,"minimum_margin_percent":Decimal128("20")});created+=1
        db.inventory.insert_one({"product_id":pid,"location_id":"main","on_hand":30,"available":30,"reserved":0,"average_cost":Decimal128(Decimal(cost)),"created_at":now,"updated_at":now})
        if perishable:db.lots.insert_one({"product_id":pid,"location_id":"main","lot_number":f"INI-{sku}","quantity":30,"available_quantity":30,"unit_cost":Decimal128(Decimal(cost)),"expires_at":now+timedelta(days=45),"status":"available","created_at":now,"updated_at":now})
    print(f"Datos iniciales completados: {created} productos nuevos; catálogo esperado: {len(products)}.")


if __name__=="__main__":seed()
