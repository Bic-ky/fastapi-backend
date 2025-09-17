from pydantic import BaseModel, Field
from typing import Optional

class FAQBase(BaseModel):
    question: str = Field(..., min_length=5, max_length=255)
    answer: str = Field(..., min_length=10)

class FAQCreate(FAQBase):
    pass

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

class FAQResponse(FAQBase):
    id: int

    class Config:
        from_attributes = True