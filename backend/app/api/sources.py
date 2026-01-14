from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import LiveSource, Admin, RecordTask, TaskStatus
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse, SourceStatusResponse
from app.api.deps import get_current_user
from app.services.stream_checker import check_stream_status

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(LiveSource).order_by(LiveSource.id.desc()))
    return result.scalars().all()


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source: SourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    db_source = LiveSource(**source.model_dump())
    db.add(db_source)
    await db.commit()
    await db.refresh(db_source)
    return db_source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_update: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    for key, value in source_update.model_dump(exclude_unset=True).items():
        setattr(source, key, value)

    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    active_task = await db.execute(
        select(RecordTask).where(
            RecordTask.source_id == source_id,
            RecordTask.status == TaskStatus.recording
        )
    )
    if active_task.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Cannot delete source with active recording")

    await db.delete(source)
    await db.commit()


@router.get("/{source_id}/status", response_model=SourceStatusResponse)
async def check_source_status(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    online, message = await check_stream_status(source.url, source.protocol.value)
    return SourceStatusResponse(online=online, message=message)
