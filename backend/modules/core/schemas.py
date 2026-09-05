from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class UniqueProductLines(BaseModel):
    @model_validator(mode="after")
    def unique_products(self):
        items = getattr(self, "items", [])
        product_ids = [line.product_id for line in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Cada producto debe aparecer una sola vez")
        return self


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=160)
    unit: str = Field(default="unidad", min_length=1, max_length=30)
    barcode: str | None = Field(default=None, max_length=60)
    current_price: Decimal = Field(gt=0, decimal_places=2)
    average_cost: Decimal = Field(ge=0, decimal_places=2)
    minimum_margin_percent: Decimal = Field(default=20, ge=0, le=100, decimal_places=2)
    category_id: str | None = Field(default=None, min_length=24, max_length=24)
    supplier_id: str | None = Field(default=None, min_length=24, max_length=24)
    perishable: bool = False

    @field_validator("sku", "name", "unit")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class CatalogCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=160)
    active: bool = True

    @field_validator("code", "name")
    @classmethod
    def normalize_catalog(cls, value: str) -> str:
        return value.strip()


class SupplierCreate(CatalogCreate):
    email: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=40)


class LocationCreate(CatalogCreate):
    address: str | None = Field(default=None, max_length=240)


class SaleLineCreate(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    quantity: int = Field(gt=0, le=10000)


class SaleCreate(UniqueProductLines):
    location_id: str = Field(default="main", min_length=1, max_length=60)
    customer_id: str | None = None
    items: list[SaleLineCreate] = Field(min_length=1, max_length=200)


class ReceiptLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    lot_number: str = Field(min_length=1, max_length=80)
    quantity: int = Field(gt=0, le=1000000)
    unit_cost: Decimal = Field(ge=0, decimal_places=2)
    expires_at: str | None = None


class InventoryReceiptCreate(UniqueProductLines):
    location_id: str = Field(default="main", min_length=1, max_length=60)
    items: list[ReceiptLine] = Field(min_length=1, max_length=500)


class PurchaseOrderLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    quantity: int = Field(gt=0, le=1000000)
    unit_cost: Decimal = Field(ge=0, decimal_places=2)


class PurchaseOrderCreate(UniqueProductLines):
    supplier_name: str = Field(min_length=2, max_length=160)
    location_id: str = Field(default="main", min_length=1, max_length=60)
    items: list[PurchaseOrderLine] = Field(min_length=1, max_length=500)


class PurchaseReceiptCreate(UniqueProductLines):
    items: list[ReceiptLine] = Field(min_length=1, max_length=500)


class StockCountLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    physical_quantity: int = Field(ge=0)
    reason: str = Field(min_length=3, max_length=300)


class StockCountCreate(UniqueProductLines):
    location_id: str = Field(default="main", min_length=1, max_length=60)
    items: list[StockCountLine] = Field(min_length=1, max_length=1000)


class LostSaleCreate(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    requested_quantity: int = Field(gt=0)
    reason: str = Field(default="out_of_stock", max_length=80)


class ReturnLine(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    fit_quantity: int = Field(ge=0)
    damaged_quantity: int = Field(ge=0)
    reason: str = Field(min_length=3, max_length=300)


class ReturnCreate(UniqueProductLines):
    sale_id: str = Field(min_length=24, max_length=24)
    items: list[ReturnLine] = Field(min_length=1, max_length=200)
