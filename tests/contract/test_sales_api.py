from backend.app import create_app


def test_products_reject_invalid_payload():
    client = create_app(testing=True).test_client()
    response = client.post("/api/v1/products", json={"name": "Sin SKU"})
    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"


def test_sale_rejects_empty_lines():
    client = create_app(testing=True).test_client()
    response = client.post("/api/v1/sales", json={"location_id": "main", "items": []})
    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"


def test_confirm_requires_idempotency_key():
    client = create_app(testing=True).test_client()
    response = client.post("/api/v1/sales/000000000000000000000000/confirm")
    assert response.status_code == 400
    assert response.json["error"]["code"] == "idempotency_key_required"


def test_inventory_movements_reject_invalid_limit():
    response = create_app(testing=True).test_client().get("/api/v1/inventory/movements?limit=no-numero")
    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"


def test_inventory_movements_reject_invalid_limit():
    response = create_app(testing=True).test_client().get("/api/v1/inventory/movements?limit=no-numero")
    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"
