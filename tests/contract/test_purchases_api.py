from backend.app import create_app


def test_purchase_order_requires_items():
    response = create_app(testing=True).test_client().post("/api/v1/purchase-orders", json={"supplier_name": "Proveedor", "items": []})
    assert response.status_code == 422


def test_purchase_receipt_requires_idempotency_key():
    response = create_app(testing=True).test_client().post("/api/v1/purchase-orders/000000000000000000000000/receipts", json={})
    assert response.status_code == 400
