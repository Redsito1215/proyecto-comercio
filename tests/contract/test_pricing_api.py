from backend.app import create_app


def test_pricing_contract():
    response = create_app(testing=True).test_client().get("/api/v1/pricing/margins")
    assert response.status_code == 200
    assert "data" in response.get_json()


def test_simulation_validates_product_id():
    response = create_app(testing=True).test_client().post("/api/v1/pricing/simulations", json={"product_id": "bad", "proposed_price": "9.99"})
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "validation_error"
