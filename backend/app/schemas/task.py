from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus


class TaskResponse(BaseModel):
    id: int
    source_id: int
    status: TaskStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskWithSourceResponse(TaskResponse):
    source_name: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
