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
