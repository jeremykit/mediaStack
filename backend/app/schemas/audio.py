"""Audio extraction schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

from app.models.audio_extract_task import AudioExtractStatus


class AudioExtractRequest(BaseModel):
    """Request schema for audio extraction."""
    format: str = Field(default="mp3", description="Audio format (only mp3 supported)")
    bitrate: str = Field(default="128k", description="Audio bitrate (e.g., 128k, 192k, 320k)")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed_formats = ['mp3']  # 目前只支持 mp3
        if v.lower() not in allowed_formats:
            raise ValueError(f"Format must be one of: {', '.join(allowed_formats)}")
        return v.lower()

    @field_validator('bitrate')
    @classmethod
    def validate_bitrate(cls, v: str) -> str:
        # 只允许数字+k 格式，如 128k, 192k, 320k
        if not re.match(r'^\d{2,3}k$', v.lower()):
            raise ValueError("Bitrate must be in format like '128k', '192k', '320k'")
        return v.lower()


class AudioExtractTaskResponse(BaseModel):
    """Response schema for audio extraction task."""
    id: int
    video_id: int
    status: AudioExtractStatus
    output_path: Optional[str] = None
    format: str
    bitrate: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AudioInfoResponse(BaseModel):
    """Response schema for audio information."""
    video_id: int
    has_audio: bool
    task: Optional[AudioExtractTaskResponse] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
