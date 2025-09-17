from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, unique=True, nullable=False)
    content = Column(Text, nullable=True)                         # Full content
    image = Column(String(255), nullable=True)                    # Optional image URL
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Author ID

    # Relationship with User
    owner = relationship("User", back_populates="blogs")
