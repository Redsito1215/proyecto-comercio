from decimal import Decimal
from pydantic import BaseModel,ConfigDict,Field,model_validator


class PaymentCreate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    sale_id:str=Field(min_length=24,max_length=24)
    method:str=Field(pattern="^(cash|card|wallet|transfer)$")
    amount:Decimal=Field(gt=0,decimal_places=2)
    payment_method_token:str|None=Field(default=None,min_length=8,max_length=200)
    brand:str|None=Field(default=None,max_length=30)
    last4:str|None=Field(default=None,pattern="^[0-9]{4}$")

    @model_validator(mode="after")
    def token_for_electronic(self):
        if self.method!="cash" and not self.payment_method_token:raise ValueError("Se requiere token del proveedor")
        return self


class RefundCreate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    amount:Decimal=Field(gt=0,decimal_places=2)
    reason:str=Field(min_length=3,max_length=300)
