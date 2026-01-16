from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.video import SourceType, FileType
from app.schemas.tag import TagListResponse
from app.schemas.category import CategoryListResponse


class VideoUpdate(BaseModel):
    title: Optional[str] = None


class SetCategoryRequest(BaseModel):
    category_id: Optional[int] = None


class SetTagsRequest(BaseModel):
    tag_ids: List[int]


class VideoResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    category_id: Optional[int] = None
    title: str
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    view_count: int
    source_type: SourceType
    file_type: FileType
    created_at: datetime
    category: Optional[CategoryListResponse] = None
    tags: List[TagListResponse] = []

    class Config:
        from_attributes = True


class VideoPlayResponse(BaseModel):
    hls_url: str
