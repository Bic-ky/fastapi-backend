from sqlalchemy import Column, Integer, Boolean, String, DateTime, Index, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    blogs = relationship("Blog", back_populates="owner")

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True)
    jti = Column(String(64), nullable=False, unique=True, index=True)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_type = Column(String(20), nullable=False, default="access")  # e.g., 'access'/'refresh'
    revoked_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User")

Index("ix_revoked_tokens_user_jti", RevokedToken.user_id, RevokedToken.jti, unique=True)