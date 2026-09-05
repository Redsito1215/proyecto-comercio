from pydantic import BaseModel,ConfigDict,EmailStr,Field


class BootstrapCreate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name:str=Field(min_length=2,max_length=120)
    email:EmailStr
    password:str=Field(min_length=12,max_length=200)


class LoginCreate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    email:EmailStr
    password:str=Field(min_length=1,max_length=200)


class UserCreate(BootstrapCreate):
    roles:list[str]=Field(default_factory=lambda:["cashier"],min_length=1,max_length=5)


class BusinessSettingsUpdate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    business_name:str=Field(min_length=2,max_length=160)
    tax_id:str=Field(default="",max_length=40)
    currency:str=Field(default="USD",min_length=3,max_length=3)
    timezone:str=Field(default="America/Guayaquil",min_length=3,max_length=80)
    low_stock_threshold:int=Field(default=5,ge=0,le=100000)
    expiry_warning_days:int=Field(default=30,ge=1,le=365)
