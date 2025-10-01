# app/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import declarative_base
import enum
from app.models.base import Base

class ContactStatus(str, enum.Enum):
    new = "new"
    read = "read"
    archived = "archived"

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    # form fields
    name = Column(String(160), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(32), nullable=False, index=True)
    service = Column(String(120), nullable=True)     
    preferred_time = Column(String(40), nullable=True)     
    message = Column(Text, nullable=True)

    # triage + audit
    status = Column(Enum(ContactStatus), nullable=False, default=ContactStatus.new)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
