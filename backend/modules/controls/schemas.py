from decimal import Decimal
from pydantic import BaseModel,Field,model_validator


class CashSessionOpen(BaseModel):
    register_id:str=Field(min_length=1,max_length=60)
    location_id:str=Field(default="main",min_length=1,max_length=60)
    opening_amount:Decimal=Field(ge=0,decimal_places=2)


class CashMovementCreate(BaseModel):
    type:str=Field(pattern="^(sale|deposit|withdrawal|refund|correction)$")
    amount:Decimal=Field(gt=0,decimal_places=2)
    source_type:str|None=Field(default=None,max_length=40)
    source_id:str|None=Field(default=None,max_length=80)
    reason:str=Field(min_length=3,max_length=300)


class CashCountCreate(BaseModel):
    counted_amount:Decimal=Field(ge=0,decimal_places=2)
    reason:str=Field(default="Arqueo de control",min_length=3,max_length=300)


class CashClose(CashCountCreate):pass


class LossCreate(BaseModel):
    product_id:str=Field(min_length=24,max_length=24)
    location_id:str=Field(default="main",min_length=1,max_length=60)
    lot_id:str|None=Field(default=None,min_length=24,max_length=24)
    type:str=Field(pattern="^(expiry|damage|theft_suspected|spoilage|other)$")
    quantity:int=Field(gt=0,le=1000000)
    reason:str=Field(min_length=3,max_length=300)
    evidence:str|None=Field(default=None,max_length=500)


class AlertResolve(BaseModel):
    resolution:str=Field(min_length=5,max_length=500)
