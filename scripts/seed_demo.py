from datetime import UTC,datetime,timedelta
from decimal import Decimal
from bson import Decimal128

from backend.db import get_db
from backend.modules.core.repositories import insert_product


def seed():
    db=get_db()
    categories=[("BEB","Bebidas"),("LAC","Lácteos"),("PAN","Panadería"),("SNA","Snacks"),("DES","Despensa")]
    suppliers=[("SUP-AND","Distribuidora Andina","ventas@andina.example","0990001001"),("SUP-LAC","Lácteos del Valle","pedidos@lacteos.example","0990001002"),("SUP-PAN","Panadería Central","comercial@panaderia.example","0990001003")]
    locations=[("MAIN","Sucursal principal","Av. Comercio 100"),("NORTE","Sucursal norte","Calle Mercado 25"),("BOD-01","Bodega central","Parque industrial, nave 4")]
    products=[("CAF-001","Café molido premium","8.50","4.20",False,"780000001","DES"), ("LEC-001","Leche entera 1L","1.60","1.05",True,"780000002","LAC"), ("PAT-001","Patatas artesanas","2.40","1.10",True,"780000003","SNA"), ("CER-000","Cerveza sin alcohol","1.90","0.85",False,"780000004","BEB"), ("BOL-001","Bollos de mantequilla","2.10","0.95",True,"780000005","PAN"), ("ARR-001","Arroz premium 1kg","2.25","1.30",False,"780000006","DES"), ("YOG-001","Yogur natural","1.15","0.62",True,"780000007","LAC"), ("AGU-001","Agua mineral 1L","0.85","0.32",False,"780000008","BEB")]
    now=datetime.now(UTC)
    for code,name in categories:db.categories.update_one({"code":code},{"$set":{"name":name,"name_normalized":name.casefold(),"active":True}},upsert=True)
    for code,name,email,phone in suppliers:db.suppliers.update_one({"code":code},{"$set":{"name":name,"name_normalized":name.casefold(),"email":email,"phone":phone,"active":True}},upsert=True)
    for code,name,address in locations:db.locations.update_one({"code":code},{"$set":{"name":name,"name_normalized":name.casefold(),"address":address,"active":True}},upsert=True)
    category_ids={x["code"]:x["_id"] for x in db.categories.find({"code":{"$in":[x[0] for x in categories]}})}
    created=0
    for sku,name,price,cost,perishable,barcode,category in products:
        existing=db.products.find_one({"sku":sku})
        if existing:pid=existing["_id"]
        else:
            pid=insert_product(db,{"sku":sku,"name":name,"unit":"unidad","barcode":barcode,"current_price":Decimal128(Decimal(price)),"average_cost":Decimal128(Decimal(cost)),"perishable":perishable,"minimum_margin_percent":Decimal128("20")});created+=1
        db.products.update_one({"_id":pid},{"$set":{"category_id":category_ids[category],"active":True}})
        db.inventory.update_one({"product_id":pid,"location_id":"main"},{"$setOnInsert":{"on_hand":30,"available":30,"reserved":0,"average_cost":Decimal128(Decimal(cost)),"created_at":now},"$set":{"updated_at":now}},upsert=True)
        if perishable:db.lots.update_one({"product_id":pid,"location_id":"main","lot_number":f"INI-{sku}"},{"$setOnInsert":{"quantity":30,"available_quantity":30,"unit_cost":Decimal128(Decimal(cost)),"created_at":now},"$set":{"expires_at":now+timedelta(days=45),"status":"available","updated_at":now}},upsert=True)
        db.competitor_prices.update_one({"product_id":pid,"competitor":"Mercado Digital"},{"$set":{"price":Decimal128(Decimal(price)*Decimal("0.98")),"observed_at":now,"source":"demo"}},upsert=True)
    customers=[("CLI-001","Ana Torres","ana.torres@example.com",datetime(1992,9,10,tzinfo=UTC)),("CLI-002","Carlos Méndez","carlos.mendez@example.com",datetime(1987,2,18,tzinfo=UTC)),("CLI-003","Sofía Ruiz","sofia.ruiz@example.com",datetime(1998,12,3,tzinfo=UTC))]
    for code,name,email,birthday in customers:db.customers.update_one({"code":code},{"$set":{"name":name,"name_normalized":name.casefold(),"email":email,"birthday":birthday,"status":"active","marketing_consent":{"granted":True,"channel":"email","updated_at":now},"updated_at":now},"$setOnInsert":{"created_at":now}},upsert=True)
    db.settings.update_one({"key":"business"},{"$set":{"business_name":"Comercio Inteligente Demo","tax_id":"0999999999001","currency":"USD","timezone":"America/Guayaquil","low_stock_threshold":5,"expiry_warning_days":30,"updated_at":now}},upsert=True)
    print(f"Datos iniciales completados: {created} productos nuevos; {len(products)} productos, {len(categories)} categorías, {len(suppliers)} proveedores, {len(locations)} ubicaciones y {len(customers)} clientes disponibles.")


if __name__=="__main__":seed()
