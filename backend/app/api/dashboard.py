from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.database import get_db
from app.models import Admin, RecordTask, LiveSource, VideoFile, TaskStatus, VideoStatus
from app.api.deps import get_current_user
from app.config import settings
from app.schemas.dashboard import (
    DashboardOverview,
    RecordingTaskInfo,
    SourceStats,
    SystemStats
)
import psutil

router = APIRouter(prefix="/api/admin/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
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
        duration = 0
        if task.started_at:
            duration = int((datetime.now() - task.started_at).total_seconds())
        recording_task_items.append(
            RecordingTaskInfo(
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

    sources_stats = SourceStats(
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

    return DashboardOverview(
        recording_tasks=recording_task_items,
        recording_count=recording_count,
        pending_video_count=pending_video_count,
        sources=sources_stats,
        system=system_stats
    )
