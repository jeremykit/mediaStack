from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.database import get_db
from app.models import Admin, RecordTask, LiveSource, VideoFile, TaskStatus, VideoStatus, Schedule, Download, Category, FileType
from app.api.deps import get_current_user
from app.config import settings
from app.schemas.dashboard import (
    DashboardOverview,
    RecordingTaskInfo,
    SourceStats,
    SystemStats,
    DashboardStatistics,
    StorageStats,
    CategoryStorageInfo,
    TrafficStats,
    DashboardActivity,
    RecentTaskInfo,
    UpcomingScheduleInfo
)
from app.services.scheduler import get_scheduler
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


@router.get("/statistics", response_model=DashboardStatistics)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    Get dashboard statistics including:
    - Storage statistics (total files, total size, by category)
    - Traffic statistics by period (today, week, month)
    """
    # Get current time in UTC for consistent calculations
    now = datetime.now(ZoneInfo("UTC"))

    # Calculate time boundaries
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday
    month_start = today_start.replace(day=1)

    # Storage statistics
    # Total files and size
    total_result = await db.execute(
        select(
            func.count(VideoFile.id).label("total_files"),
            func.sum(VideoFile.file_size).label("total_size")
        )
    )
    total_row = total_result.one()
    total_files = total_row.total_files or 0
    total_size = total_row.total_size or 0

    # Storage by category
    category_result = await db.execute(
        select(
            Category.name,
            func.count(VideoFile.id).label("count"),
            func.sum(VideoFile.file_size).label("size")
        )
        .join(VideoFile, VideoFile.category_id == Category.id)
        .group_by(Category.id, Category.name)
    )
    by_category = [
        CategoryStorageInfo(
            name=row.name,
            count=row.count or 0,
            size=row.size or 0
        )
        for row in category_result.all()
    ]

    storage_stats = StorageStats(
        total_files=total_files,
        total_size=total_size,
        by_category=by_category
    )

    # Traffic statistics by period
    traffic_by_period = []

    # Helper function to get traffic for a period
    async def get_traffic_for_period(start_date: datetime, period_label: str) -> TrafficStats:
        # NOTE: Traffic Statistics Implementation Design
        # ---------------------------------------------
        # This implementation counts cumulative views of videos/audio created
        # within the time period. It does NOT track actual access events during the period.
        #
        # Example: If a video was created today and viewed 100 times tomorrow,
        # those 100 views are still counted toward "today" stats because the video
        # was created today. This is a simplified approach that avoids creating
        # a separate access/visit log table.
        #
        # To track actual traffic within a time period (when views/downloads occur),
        # a new access_records table would be needed to log each view/download event
        # with a timestamp. This is beyond the current scope.

        # Count video views (videos created in period, sum view_count)
        video_views_result = await db.execute(
            select(func.sum(VideoFile.view_count)).where(
                VideoFile.file_type == FileType.video,
                VideoFile.created_at >= start_date
            )
        )
        video_views = video_views_result.scalar() or 0

        # Count audio views
        audio_views_result = await db.execute(
            select(func.sum(VideoFile.view_count)).where(
                VideoFile.file_type == FileType.audio,
                VideoFile.created_at >= start_date
            )
        )
        audio_views = audio_views_result.scalar() or 0

        # Count video downloads
        video_downloads_result = await db.execute(
            select(func.count(Download.id))
            .join(VideoFile, Download.video_id == VideoFile.id)
            .where(
                VideoFile.file_type == FileType.video,
                Download.downloaded_at >= start_date
            )
        )
        video_downloads = video_downloads_result.scalar() or 0

        # Count audio downloads
        audio_downloads_result = await db.execute(
            select(func.count(Download.id))
            .join(VideoFile, Download.video_id == VideoFile.id)
            .where(
                VideoFile.file_type == FileType.audio,
                Download.downloaded_at >= start_date
            )
        )
        audio_downloads = audio_downloads_result.scalar() or 0

        return TrafficStats(
            period=period_label,
            video_views=video_views,
            audio_views=audio_views,
            video_downloads=video_downloads,
            audio_downloads=audio_downloads
        )

    # Get traffic for each period
    traffic_by_period.append(await get_traffic_for_period(today_start, "today"))
    traffic_by_period.append(await get_traffic_for_period(week_start, "week"))
    traffic_by_period.append(await get_traffic_for_period(month_start, "month"))

    return DashboardStatistics(
        storage=storage_stats,
        traffic_by_period=traffic_by_period
    )


@router.get("/activity", response_model=DashboardActivity)
async def get_activity(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    Get dashboard activity including:
    - Recent completed tasks (last 10)
    - Upcoming schedules with next run time
    """
    # Get recent completed tasks
    recent_tasks_result = await db.execute(
        select(RecordTask, LiveSource)
        .join(LiveSource, RecordTask.source_id == LiveSource.id)
        .where(RecordTask.status == TaskStatus.completed)
        .order_by(RecordTask.ended_at.desc())
        .limit(10)
    )
    recent_tasks = recent_tasks_result.all()

    recent_task_items = [
        RecentTaskInfo(
            id=task.id,
            source_name=source.name,
            status=task.status.value,
            completed_at=task.ended_at or datetime.now(ZoneInfo("UTC")),
            duration=task.duration or 0,
            file_size=task.file_size or 0
        )
        for task, source in recent_tasks
    ]

    # Get upcoming schedules
    schedules_result = await db.execute(
        select(Schedule, LiveSource)
        .join(LiveSource, Schedule.source_id == LiveSource.id)
        .where(Schedule.is_active == True)
    )
    schedules = schedules_result.all()

    sched = get_scheduler()
    upcoming_schedule_items = []

    # If scheduler is not available, return empty upcoming schedules
    if sched is None:
        return DashboardActivity(
            recent_tasks=recent_task_items,
            upcoming_schedules=[]
        )

    for schedule, source in schedules:
        # Get next run time from scheduler
        job_id = f"schedule_{schedule.id}"
        job = sched.get_job(job_id)
        next_run = job.next_run_time if job else None

        if next_run:
            upcoming_schedule_items.append(
                UpcomingScheduleInfo(
                    id=schedule.id,
                    source_name=source.name,
                    next_run=next_run,
                    cron_expression=schedule.cron_expr
                )
            )

    # Sort by next run time
    upcoming_schedule_items.sort(key=lambda x: x.next_run)

    return DashboardActivity(
        recent_tasks=recent_task_items,
        upcoming_schedules=upcoming_schedule_items
    )
