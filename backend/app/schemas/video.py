from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.video import SourceType, FileType, VideoStatus
from app.schemas.tag import TagListResponse
from app.schemas.category import CategoryListResponse


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class SetCategoryRequest(BaseModel):
    category_id: Optional[int] = None


class SetTagsRequest(BaseModel):
    tag_ids: List[int]


class VideoResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    view_count: int
    source_type: SourceType
    file_type: FileType
    status: VideoStatus
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    created_at: datetime
    category: Optional[CategoryListResponse] = None
    tags: List[TagListResponse] = []

    class Config:
        from_attributes = True


class VideoPlayResponse(BaseModel):
    hls_url: str


class BatchPublishRequest(BaseModel):
    video_ids: List[int] = Field(..., max_length=100)


class BatchOfflineRequest(BaseModel):
    video_ids: List[int] = Field(..., max_length=100)


class BatchOperationResponse(BaseModel):
    success_count: int
    failed_ids: List[int]
