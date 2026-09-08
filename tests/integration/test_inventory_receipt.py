from backend.app import create_app
from backend.db import get_db


def test_receipt_creates_lot_stock_and_movement():
    db = get_db()
    assert db.name.endswith("_test")
    for name in ("products", "inventory", "lots", "inventory_movements"):
        db[name].delete_many({})
    product_id = db.products.insert_one({"sku": "LOT-1", "name": "Leche", "name_normalized": "leche", "active": True, "perishable": True, "barcodes": []}).inserted_id
    client = create_app(testing=True).test_client()
    response = client.post("/api/v1/inventory/receipts", headers={"Idempotency-Key": "receipt-1"}, json={
        "location_id": "main", "items": [{"product_id": str(product_id), "lot_number": "L-001", "quantity": 8, "unit_cost": "1.25", "expires_at": "2026-12-31"}],
    })
    assert response.status_code == 201
    assert db.inventory.find_one({"product_id": product_id})["available"] == 8
    assert db.lots.find_one({"product_id": product_id})["available_quantity"] == 8
    assert db.inventory_movements.count_documents({"type": "receipt"}) == 1
    movements = client.get("/api/v1/inventory/movements?type=receipt").json["data"]
    assert len(movements) == 1
    assert movements[0]["product_name"] == "Leche"
    assert movements[0]["sku"] == "LOT-1"
    assert movements[0]["quantity"] == 8
    movements = client.get("/api/v1/inventory/movements?type=receipt").json["data"]
    assert len(movements) == 1
    assert movements[0]["product_name"] == "Leche"
    assert movements[0]["sku"] == "LOT-1"
    assert movements[0]["quantity"] == 8
