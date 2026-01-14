from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScheduleCreate(BaseModel):
    source_id: int
    cron_expr: str
    is_active: bool = True


class ScheduleUpdate(BaseModel):
    cron_expr: Optional[str] = None
    is_active: Optional[bool] = None


class ScheduleResponse(BaseModel):
    id: int
    source_id: int
    cron_expr: str
    is_active: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduleWithSourceResponse(ScheduleResponse):
    source_name: str
