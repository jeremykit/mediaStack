"""Schemas for video trimming API."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TrimVideoRequest(BaseModel):
    """Request schema for trimming a video."""
    start_time: int = Field(..., ge=0, description="Start time in seconds")
    end_time: int = Field(..., gt=0, description="End time in seconds")
    extract_audio: bool = Field(default=False, description="Extract audio from trimmed video")
    keep_original: bool = Field(default=False, description="Keep original video file")


class TrimTaskResponse(BaseModel):
    """Response schema for trim task."""
    id: int
    video_id: int
    status: str
    start_time: int
    end_time: int
    extract_audio: bool
    keep_original: bool
    audio_bitrate: str
    trimmed_video_path: Optional[str]
    extracted_audio_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True
