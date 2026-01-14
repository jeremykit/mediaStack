from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Admin, Schedule, LiveSource
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleWithSourceResponse
from app.api.deps import get_current_user
from app.services.scheduler import add_schedule_job, remove_schedule_job, get_next_run_time

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("", response_model=List[ScheduleWithSourceResponse])
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(
        select(Schedule, LiveSource.name)
        .join(LiveSource)
        .order_by(Schedule.id.desc())
    )
    schedules = []
    for schedule, source_name in result.all():
        schedules.append(ScheduleWithSourceResponse(
            id=schedule.id,
            source_id=schedule.source_id,
            cron_expr=schedule.cron_expr,
            is_active=schedule.is_active,
            last_run_at=schedule.last_run_at,
            next_run_at=get_next_run_time(schedule.id),
            created_at=schedule.created_at,
            source_name=source_name
        ))
    return schedules


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    schedule: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(LiveSource).where(LiveSource.id == schedule.source_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Source not found")

    try:
        from apscheduler.triggers.cron import CronTrigger
        CronTrigger.from_crontab(schedule.cron_expr)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cron expression")

    db_schedule = Schedule(**schedule.model_dump())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)

    if db_schedule.is_active:
        add_schedule_job(db_schedule.id, db_schedule.cron_expr)

    return db_schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    update_data = schedule_update.model_dump(exclude_unset=True)

    if "cron_expr" in update_data:
        try:
            from apscheduler.triggers.cron import CronTrigger
            CronTrigger.from_crontab(update_data["cron_expr"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid cron expression")

    for key, value in update_data.items():
        setattr(schedule, key, value)

    await db.commit()
    await db.refresh(schedule)

    if schedule.is_active:
        add_schedule_job(schedule.id, schedule.cron_expr)
    else:
        remove_schedule_job(schedule.id)

    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    remove_schedule_job(schedule_id)
    await db.delete(schedule)
    await db.commit()
