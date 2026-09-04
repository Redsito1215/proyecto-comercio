import pytest
from pydantic import ValidationError

from backend.modules.core.schemas import SaleCreate


def test_sale_rejects_duplicate_product_lines():
    product_id = "507f1f77bcf86cd799439011"
    with pytest.raises(ValidationError, match="Cada producto"):
        SaleCreate(items=[{"product_id": product_id, "quantity": 1}, {"product_id": product_id, "quantity": 2}])
