from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.source import ProtocolType
from app.schemas.category import CategoryListResponse


class SourceCreate(BaseModel):
    name: str
    protocol: ProtocolType
    url: str
    retention_days: int = 365
    is_active: bool = True
    category_id: Optional[int] = None


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    protocol: Optional[ProtocolType] = None
    url: Optional[str] = None
    retention_days: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    protocol: ProtocolType
    url: str
    retention_days: int
    is_active: bool
    is_online: bool
    last_check_time: Optional[datetime]
    is_recording: bool = False
    category: Optional[CategoryListResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceStatusResponse(BaseModel):
    online: bool
    message: str
