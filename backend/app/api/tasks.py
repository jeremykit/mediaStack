from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Admin, RecordTask, LiveSource, TaskStatus
from app.schemas.task import TaskResponse, TaskWithSourceResponse
from app.api.deps import get_current_user
from app.services.recorder import RecorderService

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/sources/{source_id}/record/start", response_model=TaskResponse)
async def start_recording(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    try:
        task = await RecorderService.start_recording(source_id, db)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sources/{source_id}/record/stop", response_model=TaskResponse)
async def stop_recording(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(
        select(RecordTask).where(
            RecordTask.source_id == source_id,
            RecordTask.status == TaskStatus.recording
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=400, detail="No active recording for this source")

    try:
        task = await RecorderService.stop_recording(task.id, db)
        await db.refresh(task)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=List[TaskWithSourceResponse])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(
        select(RecordTask, LiveSource.name)
        .join(LiveSource)
        .order_by(RecordTask.id.desc())
        .limit(100)
    )
    return [
        TaskWithSourceResponse(
            id=task.id, source_id=task.source_id, status=task.status,
            started_at=task.started_at, ended_at=task.ended_at,
            file_path=task.file_path, file_size=task.file_size,
            duration=task.duration, error_message=task.error_message,
            created_at=task.created_at, source_name=source_name
        )
        for task, source_name in result.all()
    ]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(RecordTask).where(RecordTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
