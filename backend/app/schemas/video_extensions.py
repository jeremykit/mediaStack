"""Schemas for video extension resources (images, texts, links)."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ============ Video Image Schemas ============

class VideoImageResponse(BaseModel):
    """Response schema for video image."""
    id: int
    video_id: int
    image_path: str  # 保留用于内部使用
    image_url: str   # 返回给前端的 URL
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Video Text Schemas ============

class VideoTextCreate(BaseModel):
    """Request schema for creating video text."""
    title: str = Field(..., min_length=1, max_length=64)
    content: Optional[str] = None
    sort_order: int = Field(default=0, ge=0)


class VideoTextUpdate(BaseModel):
    """Request schema for updating video text."""
    title: Optional[str] = Field(None, min_length=1, max_length=64)
    content: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)


class VideoTextResponse(BaseModel):
    """Response schema for video text."""
    id: int
    video_id: int
    title: str
    content: Optional[str] = None
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Video Link Schemas ============

class VideoLinkCreate(BaseModel):
    """Request schema for creating video link."""
    title: str = Field(..., min_length=1, max_length=64)
    url: str = Field(..., min_length=1, max_length=512)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format")
        return v


class VideoLinkResponse(BaseModel):
    """Response schema for video link."""
    id: int
    video_id: int
    title: str
    url: str
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True
