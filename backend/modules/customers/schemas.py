from datetime import date
from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2,max_length=160)
    email: EmailStr | None = None
    document: str | None = Field(default=None,max_length=40)
    phone: str | None = Field(default=None,max_length=40)
    birthday: date | None = None


class ConsentCreate(BaseModel):
    purpose: str = Field(default='marketing',max_length=60)
    channel: str = Field(pattern='^(email|sms|push)$')
    granted: bool
    source: str = Field(default='user',max_length=80)
