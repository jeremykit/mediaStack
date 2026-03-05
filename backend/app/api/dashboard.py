from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Admin, RecordTask, LiveSource, VideoFile, TaskStatus, VideoStatus
from app.api.deps import get_current_user
from app.config import settings
import psutil

router = APIRouter(prefix="/api/admin/dashboard", tags=["dashboard"])


class RecordingTaskItem(BaseModel):
    id: int
    source_name: str
    started_at: datetime
    duration: int | None = None


class SourcesStats(BaseModel):
    total: int
    online: int
    offline: int
    recording: int


class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float


class DashboardOverviewResponse(BaseModel):
    recording_tasks: List[RecordingTaskItem]
    recording_count: int
    pending_video_count: int
    sources: SourcesStats
    system: SystemStats


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    Get dashboard overview statistics including:
    - Active recording tasks
    - Pending video count
    - Source statistics
    - System resource usage
    """

    # Get recording tasks with source names
    result = await db.execute(
        select(RecordTask, LiveSource)
        .join(LiveSource, RecordTask.source_id == LiveSource.id)
        .where(RecordTask.status == TaskStatus.recording)
    )
    recording_tasks = result.all()

    # Calculate duration for each recording task
    recording_task_items = []
    for task, source in recording_tasks:
        duration = None
        if task.started_at:
            duration = int((datetime.now() - task.started_at).total_seconds())
        recording_task_items.append(
            RecordingTaskItem(
                id=task.id,
                source_name=source.name,
                started_at=task.started_at,
                duration=duration
            )
        )

    # Count pending videos
    pending_result = await db.execute(
        select(func.count(VideoFile.id)).where(VideoFile.status == VideoStatus.pending)
    )
    pending_video_count = pending_result.scalar() or 0

    # Source statistics
    total_result = await db.execute(select(func.count(LiveSource.id)))
    total = total_result.scalar() or 0

    online_result = await db.execute(
        select(func.count(LiveSource.id)).where(LiveSource.is_online == True)
    )
    online = online_result.scalar() or 0

    offline = total - online

    # Count recording sources (sources with active recording tasks)
    recording_count = len(recording_tasks)

    sources_stats = SourcesStats(
        total=total,
        online=online,
        offline=offline,
        recording=recording_count
    )

    # System statistics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(str(settings.storage_path))

    system_stats = SystemStats(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_percent=disk.percent
    )

    return DashboardOverviewResponse(
        recording_tasks=recording_task_items,
        recording_count=recording_count,
        pending_video_count=pending_video_count,
        sources=sources_stats,
        system=system_stats
    )
