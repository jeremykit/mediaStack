from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.source import ProtocolType


class SourceCreate(BaseModel):
    name: str
    protocol: ProtocolType
    url: str
    retention_days: int = 365
    is_active: bool = True


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    protocol: Optional[ProtocolType] = None
    url: Optional[str] = None
    retention_days: Optional[int] = None
    is_active: Optional[bool] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    protocol: ProtocolType
    url: str
    retention_days: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceStatusResponse(BaseModel):
    online: bool
    message: str
