from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator


class PromotionCreate(BaseModel):
    name: str = Field(min_length=3,max_length=160)
    discount_percent: Decimal = Field(gt=0,le=70,decimal_places=2)
    product_ids: list[str] = Field(min_length=1,max_length=200)
    segment: str = Field(default="all",pattern="^(all|at_risk|frequent|loyal_profitable)$")
    channel: str = Field(default="email",pattern="^(email|sms)$")
    valid_from: datetime
    valid_until: datetime
    control_percent: int = Field(default=10,ge=5,le=50)
    usage_limit: int = Field(default=1,ge=1,le=100)

    @model_validator(mode="after")
    def valid_dates(self):
        if self.valid_until<=self.valid_from: raise ValueError("La fecha final debe ser posterior")
        return self


class RedemptionCreate(BaseModel):
    code: str = Field(min_length=6,max_length=80)
    sale_id: str = Field(min_length=24,max_length=24)
