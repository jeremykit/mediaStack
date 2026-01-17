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
    # Validate protocol matches URL
    url_lower = source.url.lower()
    if source.protocol.value == "rtmp" and not url_lower.startswith("rtmp://"):
        raise HTTPException(status_code=400, detail="RTMP protocol requires rtmp:// URL")
    elif source.protocol.value == "hls" and not (url_lower.startswith("http://") or url_lower.startswith("https://")):
        raise HTTPException(status_code=400, detail="HLS protocol requires http:// or https:// URL")

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

    # Get the updated values
    update_data = source_update.model_dump(exclude_unset=True)

    # Validate protocol matches URL if either is being updated
    final_protocol = update_data.get('protocol', source.protocol).value
    final_url = update_data.get('url', source.url).lower()

    if final_protocol == "rtmp" and not final_url.startswith("rtmp://"):
        raise HTTPException(status_code=400, detail="RTMP 协议需要 rtmp:// 开头的 URL")
    elif final_protocol == "hls" and not (final_url.startswith("http://") or final_url.startswith("https://")):
        raise HTTPException(status_code=400, detail="HLS 协议需要 http:// 或 https:// 开头的 URL")

    for key, value in update_data.items():
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
        raise HTTPException(status_code=400, detail="无法删除正在录制的直播源")

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
