"""Upload schemas for request/response models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.upload_task import UploadStatus


class UploadInitRequest(BaseModel):
    """Schema for initializing an upload task."""
    filename: str = Field(max_length=256)
    file_size: int = Field(gt=0)
    chunk_size: int = Field(default=5 * 1024 * 1024, gt=0)  # Default 5MB


class UploadInitResponse(BaseModel):
    """Schema for upload initialization response."""
    task_id: str
    chunk_size: int
    total_chunks: int


class UploadStatusResponse(BaseModel):
    """Schema for upload status response."""
    task_id: str
    filename: str
    file_size: int
    chunk_size: int
    total_chunks: int
    uploaded_chunks: int
    status: UploadStatus
    uploaded_chunk_indices: List[int] = []
    created_at: datetime

    class Config:
        from_attributes = True


class UploadCompleteRequest(BaseModel):
    """Schema for completing an upload."""
    title: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: List[int] = []


class UploadChunkResponse(BaseModel):
    """Schema for chunk upload response."""
    chunk_index: int
    uploaded_chunks: int
    total_chunks: int
