from decimal import Decimal

from bson import Decimal128, ObjectId

from backend.app import create_app
from backend.db import get_db


def test_confirm_sale_is_atomic_and_idempotent():
    db = get_db()
    assert db.name.endswith("_test"), "Las pruebas destructivas solo pueden usar una base *_test"
    for name in ("products", "inventory", "sales", "sale_items", "inventory_movements", "counters"):
        db[name].delete_many({})

    product_id = db.products.insert_one({
        "sku": "TEST-001", "name": "Producto de prueba", "name_normalized": "producto de prueba",
        "unit": "unidad", "barcodes": ["9990001"], "active": True,
        "current_price": Decimal128(Decimal("5.00")), "average_cost": Decimal128(Decimal("3.00")),
        "created_at": __import__("datetime").datetime.now(__import__("datetime").UTC),
    }).inserted_id
    db.inventory.insert_one({
        "product_id": product_id, "location_id": "main", "on_hand": 10, "reserved": 0,
        "available": 10, "average_cost": Decimal128(Decimal("3.00")),
    })

    client = create_app(testing=True).test_client()
    draft = client.post("/api/v1/sales", json={
        "location_id": "main", "items": [{"product_id": str(product_id), "quantity": 2}],
    })
    assert draft.status_code == 201
    sale_id = draft.json["data"]["id"]

    headers = {"Idempotency-Key": "sale-test-key"}
    first = client.post(f"/api/v1/sales/{sale_id}/confirm", headers=headers)
    second = client.post(f"/api/v1/sales/{sale_id}/confirm", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json["data"]["number"] == second.json["data"]["number"]
    assert db.inventory.find_one({"product_id": ObjectId(product_id)})["available"] == 8
    assert db.inventory_movements.count_documents({"source_id": ObjectId(sale_id)}) == 1
