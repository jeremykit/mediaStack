"""Dashboard schemas for API response models."""
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime


# ============= Dashboard Overview Schemas =============

class RecordingTaskInfo(BaseModel):
    """Recording task information for overview."""
    id: int
    source_name: str
    started_at: datetime
    duration: int  # seconds


class SourceStats(BaseModel):
    """Live source statistics."""
    total: int
    online: int
    offline: int
    recording: int


class SystemStats(BaseModel):
    """System resource statistics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float


class DashboardOverview(BaseModel):
    """Dashboard overview API response."""
    recording_tasks: List[RecordingTaskInfo]
    recording_count: int
    pending_video_count: int
    sources: SourceStats
    system: SystemStats


# ============= Dashboard Statistics Schemas =============

class CategoryStorageInfo(BaseModel):
    """Storage information by category."""
    name: str
    count: int
    size: int  # bytes


class StorageStats(BaseModel):
    """Storage statistics."""
    total_files: int
    total_size: int  # bytes
    by_category: List[CategoryStorageInfo]


class TrafficStats(BaseModel):
    """Traffic statistics for a specific period."""
    period: Literal["today", "week", "month"]
    video_views: int
    audio_views: int
    video_downloads: int
    audio_downloads: int


class DashboardStatistics(BaseModel):
    """Dashboard statistics API response."""
    storage: StorageStats
    traffic_by_period: List[TrafficStats]


# ============= Dashboard Activity Schemas =============

class RecentTaskInfo(BaseModel):
    """Recent completed task information."""
    id: int
    source_name: str
    status: str
    completed_at: datetime
    duration: int  # seconds
    file_size: int  # bytes


class UpcomingScheduleInfo(BaseModel):
    """Upcoming schedule information."""
    id: int
    source_name: str
    next_run: datetime
    cron_expression: str


class DashboardActivity(BaseModel):
    """Dashboard activity API response."""
    recent_tasks: List[RecentTaskInfo]
    upcoming_schedules: List[UpcomingScheduleInfo]
