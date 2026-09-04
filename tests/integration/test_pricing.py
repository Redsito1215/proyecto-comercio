from datetime import UTC, datetime
from decimal import Decimal
from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def seed_product(database):
    return database.products.insert_one({"sku":"PRICE-1", "name":"Producto precio", "name_normalized":"producto precio", "active":True, "current_price":Decimal128("10.00"), "average_cost":Decimal128("5.00"), "minimum_margin_percent":Decimal128("20"), "created_at":datetime.now(UTC)}).inserted_id


def test_price_change_is_audited():
    database=get_db(); assert database.name.endswith("_test"); database.products.delete_many({}); database.price_changes.delete_many({})
    seeded_product=seed_product(database); product_id = str(seeded_product); client=create_app(testing=True).test_client()
    response = client.put(f"/api/v1/pricing/products/{product_id}/price", json={"product_id": product_id, "proposed_price": "15.00", "reason": "Ajuste controlado"})
    assert response.status_code == 200
    assert database.products.find_one({"_id": seeded_product})["current_price"] == Decimal128(Decimal("15.00"))
    audit = database.price_changes.find_one({"product_id": seeded_product})
    assert audit["reason"] == "Ajuste controlado"


def test_price_below_minimum_is_rejected():
    database=get_db(); assert database.name.endswith("_test"); database.products.delete_many({}); seeded_product=seed_product(database); client=create_app(testing=True).test_client()
    response = client.put(f"/api/v1/pricing/products/{seeded_product}/price", json={"product_id": str(seeded_product), "proposed_price": "5.01", "reason": "Demasiado bajo"})
    assert response.status_code == 409
