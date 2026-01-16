"""Category schemas for request/response models."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(max_length=32)
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(default=None, max_length=32)
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    sort_order: int
    created_at: datetime
    video_count: int = 0

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for category list response."""
    id: int
    name: str
    sort_order: int

    class Config:
        from_attributes = True
