# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator
from typing import Optional, Literal, Annotated
from enum import Enum
import re

PHONE_E164 = re.compile(r'^\+[1-9]\d{7,14}$')  # + and 8–15 digits
PHONE_US = re.compile(r'^(\+?1\s?)?(\(?\d{3}\)?[\s\.-]?)\d{3}[\s\.-]?\d{4}$')

class ContactStatus(str, Enum):
    new = "new"
    read = "read"
    archived = "archived"

NameStr = Annotated[str, Field(strip_whitespace=True, min_length=2, max_length=160)]
PhoneStr = Annotated[str, Field(min_length=7, max_length=20)]

class ContactCreate(BaseModel):
    name: NameStr
    email: EmailStr
    phone: PhoneStr
    service: Optional[str] = Field(default=None, max_length=120)
    preferred_time: Optional[Literal["morning", "afternoon", "evening"]] = None
    message: Optional[str] = Field(default=None, max_length=8000)
    website: Optional[str] = None  # honeypot

    @field_validator("phone")
    @classmethod
    def validate_phone_hybrid(cls, v: str) -> str:
        v_norm = re.sub(r'[\s\-\.\(\)]', '', v)  # drop spaces/dashes/dots/parentheses
        # If starts with '+', enforce E.164
        if v_norm.startswith('+'):
            if not PHONE_E164.fullmatch(v_norm):
                raise ValueError("Invalid international phone format (use +<country><number>)")
            return v_norm
        # Otherwise allow common US formats
        if PHONE_US.fullmatch(v) or re.fullmatch(r'^\d{10}$', v_norm):
            return v  # keep original or return v_norm as you prefer
        raise ValueError("Invalid phone. Use +<country><number> or a valid US format, e.g., (419) 555-1234")

class ContactRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    service: Optional[str]
    preferred_time: Optional[str]
    message: Optional[str]
    status: ContactStatus
    created_at: datetime

    class Config:
        from_attributes = True

class ContactList(BaseModel):
    total: int
    items: list[ContactRead]
