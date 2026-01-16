"""Tag schemas for request/response models."""
from pydantic import BaseModel, Field
from datetime import datetime


class TagCreate(BaseModel):
    """Schema for creating a tag."""
    name: str = Field(max_length=16)


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: int
    name: str
    created_at: datetime
    video_count: int = 0

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Schema for tag list response."""
    id: int
    name: str

    class Config:
        from_attributes = True
