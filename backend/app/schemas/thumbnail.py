"""Thumbnail management schemas."""
from pydantic import BaseModel, Field


class ThumbnailCaptureRequest(BaseModel):
    """Request schema for capturing thumbnail at specific timestamp."""
    timestamp: float = Field(..., ge=0, description="Timestamp in seconds to capture thumbnail from")


class ThumbnailResponse(BaseModel):
    """Response schema for thumbnail operations."""
    video_id: int
    thumbnail_url: str = Field(..., description="URL path to the thumbnail image")
