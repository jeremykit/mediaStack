from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.video import SourceType

class VideoUpdate(BaseModel):
    title: Optional[str] = None

class VideoResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    title: str
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    view_count: int
    source_type: SourceType
    created_at: datetime

    class Config:
        from_attributes = True

class VideoPlayResponse(BaseModel):
    hls_url: str
