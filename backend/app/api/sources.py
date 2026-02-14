from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import asyncio
import logging

from app.database import get_db
from app.models import LiveSource, Admin, RecordTask, TaskStatus
from app.schemas.source import (
    SourceCreate, SourceUpdate, SourceResponse, SourceStatusResponse,
    BulkUpdateCategoryRequest, BulkUpdateCategoryResponse,
    CloudProviderCallback, CallbackResponse
)
from app.api.deps import get_current_user
from app.services.stream_checker import check_stream_status

logger = logging.getLogger(__name__)
# Ensure logger outputs to stdout
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', '%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(
        select(LiveSource, RecordTask)
        .outerjoin(RecordTask, (RecordTask.source_id == LiveSource.id) & (RecordTask.status == TaskStatus.recording))
        .options(selectinload(LiveSource.category))
        .order_by(LiveSource.id.desc())
    )

    sources_with_tasks = result.all()
    response = []
    for source, task in sources_with_tasks:
        source_dict = {
            "id": source.id,
            "name": source.name,
            "protocol": source.protocol,
            "url": source.url,
            "retention_days": source.retention_days,
            "is_active": source.is_active,
            "is_online": source.is_online,
            "last_check_time": source.last_check_time,
            "category": source.category,
            "created_at": source.created_at,
            "updated_at": source.updated_at,
            "is_recording": task is not None
        }
        response.append(source_dict)

    return response


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
    result = await db.execute(
        select(LiveSource)
        .where(LiveSource.id == source_id)
        .options(selectinload(LiveSource.category))
    )
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
    result = await db.execute(
        select(LiveSource)
        .where(LiveSource.id == source_id)
        .options(selectinload(LiveSource.category))
    )
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


@router.post("/bulk-update-category", response_model=BulkUpdateCategoryResponse)
async def bulk_update_category(
    request: BulkUpdateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(
        select(LiveSource).where(LiveSource.id.in_(request.source_ids))
    )
    sources = result.scalars().all()

    for source in sources:
        source.category_id = request.category_id

    await db.commit()

    return BulkUpdateCategoryResponse(updated_count=len(sources))


@router.get("/{source_id}/status", status_code=status.HTTP_202_ACCEPTED)
async def check_source_status(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    启动直播源状态检测（异步后台任务）

    立即返回 202，然后在后台循环检测并通过 WebSocket 实时推送结果
    """
    result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # 在后台启动检测任务，不阻塞响应
    asyncio.create_task(
        _check_source_in_background(source_id, source.url, source.protocol.value)
    )

    return {"message": "检测任务已启动", "source_id": source_id}


async def _check_source_in_background(source_id: int, url: str, protocol: str):
    """后台检测任务，每次检测完成后立即推送结果"""
    max_attempts = 10
    interval = 5  # 秒

    for attempt in range(1, max_attempts + 1):
        online, message = await check_stream_status(url, protocol)

        # 立即推送本次检测结果（包含检测次数）
        await _broadcast_source_status(source_id, online, attempt, max_attempts)

        if online:
            # 检测到在线，停止后续检测
            logger.info(f"Source {source_id} is online at attempt {attempt}, stopping")
            return

        # 等待后继续下一次检测
        if attempt < max_attempts:
            await asyncio.sleep(interval)

    logger.info(f"Source {source_id} is offline after {max_attempts} attempts")


async def _broadcast_source_status(source_id: int, is_online: bool, attempt: int = 0, max_attempts: int = 10):
    """
    更新数据库并广播直播源状态变化到 WebSocket 客户端

    Args:
        source_id: 直播源ID
        is_online: 在线状态
        attempt: 当前检测次数（0表示非检测任务触发）
        max_attempts: 最大检测次数
    """
    # 更新数据库
    try:
        from app.database import async_session
        from sqlalchemy import select

        async with async_session() as db:
            result = await db.execute(select(LiveSource).where(LiveSource.id == source_id))
            source = result.scalar_one_or_none()
            if source:
                source.is_online = is_online
                source.last_check_time = datetime.now()
                await db.commit()
    except Exception as e:
        logger.error(f"Failed to update database for source {source_id}: {e}")

    # 推送 WebSocket 消息
    try:
        from app.api.websocket import broadcast_source_status
        await broadcast_source_status(source_id, is_online, attempt, max_attempts)
    except ImportError:
        # WebSocket 模块未就绪，忽略
        pass
    except Exception as e:
        logger.warning(f"Failed to broadcast status: {e}")


@router.post("/callback", response_model=CallbackResponse, status_code=status.HTTP_200_OK)
async def receive_provider_callback(
    callback: CloudProviderCallback,
    db: AsyncSession = Depends(get_db)
):
    """
    接收云厂商直播状态回调

    根据 appname/channel_id 匹配数据库中的直播源，更新在线状态并推送 WebSocket 消息。

    匹配规则：
    - HLS流：https://pull.hiwords.net/live_008/1667703691430.m3u8
      匹配 appname/channel_id = live_008/1667703691430
    - RTMP流：rtmp://srs.hiwords.net/live/livestream
      匹配 appname/channel_id = live/livestream
    """
    # 构建匹配字符串: appname/channel_id
    stream_path = f"{callback.appname}/{callback.channel_id}"

    # 确保 logger 启用（可能被某些库禁用）
    if logger.disabled:
        logger.disabled = False

    logger.info(f"Received callback for stream: {stream_path}, event_type: {callback.event_type}, errcode: {callback.errcode}")

    # 根据流路径查找匹配的直播源
    # 需要匹配 URL 中包含 stream_path 的源
    result = await db.execute(
        select(LiveSource).where(
            func.lower(LiveSource.url).contains(stream_path.lower())
        )
    )
    sources = result.scalars().all()

    if not sources:
        logger.warning(f"No matching source found for stream path: {stream_path}")
        return CallbackResponse(code=0)

    # 更新所有匹配的直播源状态
    # event_type = 1 表示推流（在线），event_type = 0 表示断流（离线）
    is_online = callback.event_type == 1
    updated_count = 0

    for source in sources:
        old_status = source.is_online
        source.is_online = is_online
        source.last_check_time = datetime.now()
        updated_count += 1

        logger.info(f"Updated source {source.id} ({source.name}): {old_status} -> {is_online}")

        # 推送状态变化到 WebSocket
        await _broadcast_source_status(source.id, is_online)

    await db.commit()

    logger.info(f"Callback processed: {updated_count} sources updated")
    return CallbackResponse(code=0)
