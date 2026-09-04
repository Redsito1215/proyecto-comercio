from bson import Decimal128

from backend.app import create_app
from backend.db import get_db


def test_partial_receipt_keeps_pending_quantity():
    db = get_db(); assert db.name.endswith("_test")
    for name in ("products", "purchase_orders", "purchase_order_items", "inventory", "lots", "inventory_movements", "counters"):
        db[name].delete_many({})
    pid = db.products.insert_one({"sku":"PO-1","name":"Café","name_normalized":"cafe","active":True,"perishable":False,"barcodes":[],"current_price":Decimal128("5"),"average_cost":Decimal128("2")}).inserted_id
    client = create_app(testing=True).test_client()
    order = client.post("/api/v1/purchase-orders", json={"supplier_name":"Proveedor Uno","items":[{"product_id":str(pid),"quantity":10,"unit_cost":"2.00"}]})
    assert order.status_code == 201
    oid = order.json["data"]["id"]
    receipt = client.post(f"/api/v1/purchase-orders/{oid}/receipts", headers={"Idempotency-Key":"po-receipt-1"}, json={"items":[{"product_id":str(pid),"lot_number":"PO-L1","quantity":4,"unit_cost":"2.00"}]})
    assert receipt.status_code == 201
    saved = db.purchase_order_items.find_one({"purchase_order_id":db.purchase_orders.find_one({"_id":__import__('bson').ObjectId(oid)})["_id"]})
    assert saved["received_quantity"] == 4
    assert saved["pending_quantity"] == 6
    assert db.purchase_orders.find_one({"_id":__import__('bson').ObjectId(oid)})["status"] == "partially_received"
