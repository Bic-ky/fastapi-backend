from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

# Shared properties
class BlogBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    image: Optional[HttpUrl] = None  # Use URL type for image links

# Properties for creating a new blog
class BlogCreate(BlogBase):
    pass

# Properties for updating an existing blog
class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    image: Optional[HttpUrl] = None

# Response schema
class BlogResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    image: Optional[str] = None
    owner_id: int
    author: Optional[str] = None  # <-- add this

    class Config:
        from_attributes = True
