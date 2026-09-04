from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=160)
    unit: str = Field(default="unidad", min_length=1, max_length=30)
    barcode: str | None = Field(default=None, max_length=60)
    current_price: Decimal = Field(gt=0, decimal_places=2)
    average_cost: Decimal = Field(ge=0, decimal_places=2)
    perishable: bool = False

    @field_validator("sku", "name", "unit")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class SaleLineCreate(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    quantity: int = Field(gt=0, le=10000)


class SaleCreate(BaseModel):
    location_id: str = Field(default="main", min_length=1, max_length=60)
    customer_id: str | None = None
    items: list[SaleLineCreate] = Field(min_length=1, max_length=200)


class ReceiptLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    lot_number: str = Field(min_length=1, max_length=80)
    quantity: int = Field(gt=0, le=1000000)
    unit_cost: Decimal = Field(ge=0, decimal_places=2)
    expires_at: str | None = None


class InventoryReceiptCreate(BaseModel):
    location_id: str = Field(default="main", min_length=1, max_length=60)
    items: list[ReceiptLine] = Field(min_length=1, max_length=500)


class PurchaseOrderLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    quantity: int = Field(gt=0, le=1000000)
    unit_cost: Decimal = Field(ge=0, decimal_places=2)


class PurchaseOrderCreate(BaseModel):
    supplier_name: str = Field(min_length=2, max_length=160)
    location_id: str = Field(default="main", min_length=1, max_length=60)
    items: list[PurchaseOrderLine] = Field(min_length=1, max_length=500)


class PurchaseReceiptCreate(BaseModel):
    items: list[ReceiptLine] = Field(min_length=1, max_length=500)


class StockCountLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    physical_quantity: int = Field(ge=0)
    reason: str = Field(min_length=3, max_length=300)


class StockCountCreate(BaseModel):
    location_id: str = Field(default="main", min_length=1, max_length=60)
    items: list[StockCountLine] = Field(min_length=1, max_length=1000)


class LostSaleCreate(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    requested_quantity: int = Field(gt=0)
    reason: str = Field(default="out_of_stock", max_length=80)
