from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
from sqlalchemy import select

from app.config import settings

scheduler: AsyncIOScheduler = None


def get_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.database_url.replace('+aiosqlite', ''))
        }
        scheduler = AsyncIOScheduler(jobstores=jobstores)
    return scheduler


async def scheduled_recording_job(schedule_id: int):
    from app.database import async_session
    from app.models import Schedule, RecordTask, TaskStatus
    from app.services.recorder import RecorderService

    async with async_session() as db:
        result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
        schedule = result.scalar_one_or_none()
        if not schedule or not schedule.is_active:
            return

        result = await db.execute(
            select(RecordTask).where(
                RecordTask.source_id == schedule.source_id,
                RecordTask.status == TaskStatus.recording
            )
        )
        if result.scalar_one_or_none():
            return

        try:
            await RecorderService.start_recording(schedule.source_id, db)
            schedule.last_run_at = datetime.utcnow()
            await db.commit()
        except Exception:
            pass


def add_schedule_job(schedule_id: int, cron_expr: str):
    sched = get_scheduler()
    try:
        trigger = CronTrigger.from_crontab(cron_expr)
        sched.add_job(
            scheduled_recording_job,
            trigger=trigger,
            args=[schedule_id],
            id=f"schedule_{schedule_id}",
            replace_existing=True
        )
    except ValueError:
        raise ValueError(f"Invalid cron expression: {cron_expr}")


def remove_schedule_job(schedule_id: int):
    sched = get_scheduler()
    job_id = f"schedule_{schedule_id}"
    if sched.get_job(job_id):
        sched.remove_job(job_id)


def get_next_run_time(schedule_id: int) -> datetime | None:
    sched = get_scheduler()
    job = sched.get_job(f"schedule_{schedule_id}")
    return job.next_run_time if job else None


async def init_scheduler():
    from app.database import async_session
    from app.models import Schedule

    sched = get_scheduler()

    async with async_session() as db:
        result = await db.execute(select(Schedule).where(Schedule.is_active == True))
        schedules = result.scalars().all()

        for schedule in schedules:
            try:
                add_schedule_job(schedule.id, schedule.cron_expr)
            except ValueError:
                pass

    sched.start()


def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
