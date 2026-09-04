from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class PriceSimulation(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    proposed_price: Decimal = Field(gt=0, decimal_places=2)


class PriceChange(PriceSimulation):
    reason: str = Field(min_length=3, max_length=300)

    @field_validator("reason")
    @classmethod
    def clean_reason(cls, value): return value.strip()


class CompetitorPriceCreate(BaseModel):
    product_id: str = Field(min_length=24, max_length=24)
    competitor: str = Field(min_length=2, max_length=120)
    channel: str = Field(pattern="^(physical|digital)$")
    observed_price: Decimal = Field(gt=0, decimal_places=2)
    source: str = Field(min_length=2, max_length=300)
    observed_at: datetime
