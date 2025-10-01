# app/schemas/auth.py
from pydantic import BaseModel, Field

class ChangePasswordIn(BaseModel):
    current_password: str = Field(..., min_length=5, alias="currentPassword")
    new_password: str = Field(..., min_length=5, alias="newPassword")

    class Config:
        populate_by_name = True  
