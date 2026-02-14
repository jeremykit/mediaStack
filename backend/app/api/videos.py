from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import os

from app.database import get_db
from app.models import Admin, VideoFile, Tag, Category
from app.models.video import VideoStatus, FileType
from app.schemas.video import (
    VideoUpdate, VideoResponse, VideoPlayResponse,
    SetCategoryRequest, SetTagsRequest,
    BatchPublishRequest, BatchOfflineRequest, BatchOperationResponse
)
from app.schemas.category import CategoryListResponse
from app.schemas.tag import TagListResponse
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/videos", tags=["videos"])


def video_to_response(video: VideoFile) -> VideoResponse:
    """Convert VideoFile model to VideoResponse."""
    # Convert thumbnail path to URL
    thumbnail_url = None
    if video.thumbnail:
        from pathlib import Path
        thumb_path = Path(video.thumbnail)
        if thumb_path.is_absolute():
            # Extract just the filename
            thumbnail_url = f"/thumbnails/{thumb_path.name}"
        else:
            # Relative path, extract filename
            thumbnail_url = f"/thumbnails/{Path(video.thumbnail).name}"

    return VideoResponse(
        id=video.id,
        task_id=video.task_id,
        category_id=video.category_id,
        title=video.title,
        description=video.description,
        file_path=video.file_path,
        file_size=video.file_size,
        duration=video.duration,
        thumbnail=thumbnail_url,
        view_count=video.view_count,
        source_type=video.source_type,
        file_type=video.file_type,
        status=video.status,
        reviewed_at=video.reviewed_at,
        reviewed_by=video.reviewed_by,
        created_at=video.created_at,
        category=CategoryListResponse(
            id=video.category.id,
            name=video.category.name,
            sort_order=video.category.sort_order
        ) if video.category else None,
        tags=[
            TagListResponse(id=t.id, name=t.name)
            for t in video.tags
        ] if video.tags else []
    )


@router.get("", response_model=List[VideoResponse])
async def list_videos(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    tag_ids: Optional[str] = Query(None, description="Comma-separated tag IDs"),
    status: Optional[VideoStatus] = Query(None, description="Filter by video status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    x_view_code: Optional[str] = Header(None, alias="X-View-Code"),
    db: AsyncSession = Depends(get_db)
):
    """List videos with optional filtering."""
    query = (
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .order_by(VideoFile.id.desc())
    )

    if search:
        query = query.where(VideoFile.title.ilike(f"%{search}%"))

    if category_id:
        query = query.where(VideoFile.category_id == category_id)

    if status:
        query = query.where(VideoFile.status == status)

    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(",") if tid.strip()]
            if tag_id_list:
                # Videos that have any of the specified tags
                from app.models.video_tag import video_tags
                query = query.join(video_tags).where(video_tags.c.tag_id.in_(tag_id_list)).distinct()
        except ValueError:
            pass

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    videos = result.scalars().all()

    return [video_to_response(v) for v in videos]


@router.get("/pending", response_model=List[VideoResponse])
async def list_pending_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """List pending videos for review (admin only)."""
    query = (
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.status == VideoStatus.pending)
        .order_by(VideoFile.id.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    videos = result.scalars().all()
    return [video_to_response(v) for v in videos]


@router.post("/batch-publish", response_model=BatchOperationResponse)
async def batch_publish_videos(
    data: BatchPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """Batch publish videos (admin only)."""
    success_count = 0
    failed_ids = []

    # Query all videos at once to avoid N+1 problem
    result = await db.execute(
        select(VideoFile).where(VideoFile.id.in_(data.video_ids))
    )
    videos = {v.id: v for v in result.scalars().all()}

    for video_id in data.video_ids:
        video = videos.get(video_id)
        if video:
            video.status = VideoStatus.published
            video.reviewed_at = datetime.now()
            video.reviewed_by = current_user.id
            success_count += 1
        else:
            failed_ids.append(video_id)

    await db.commit()
    return BatchOperationResponse(success_count=success_count, failed_ids=failed_ids)


@router.post("/batch-offline", response_model=BatchOperationResponse)
async def batch_offline_videos(
    data: BatchOfflineRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """Batch offline videos (admin only)."""
    success_count = 0
    failed_ids = []

    # Query all videos at once to avoid N+1 problem
    result = await db.execute(
        select(VideoFile).where(VideoFile.id.in_(data.video_ids))
    )
    videos = {v.id: v for v in result.scalars().all()}

    for video_id in data.video_ids:
        video = videos.get(video_id)
        if video:
            video.status = VideoStatus.offline
            video.reviewed_at = datetime.now()
            video.reviewed_by = current_user.id
            success_count += 1
        else:
            failed_ids.append(video_id)

    await db.commit()
    return BatchOperationResponse(success_count=success_count, failed_ids=failed_ids)


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video_to_response(video)


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    for key, value in video_update.model_dump(exclude_unset=True).items():
        setattr(video, key, value)

    await db.commit()
    await db.refresh(video)
    return video_to_response(video)


@router.put("/{video_id}/category", response_model=VideoResponse)
async def set_video_category(
    video_id: int,
    data: SetCategoryRequest,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Set video category."""
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if data.category_id:
        # Verify category exists
        cat_result = await db.execute(select(Category).where(Category.id == data.category_id))
        if not cat_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Category not found")

    video.category_id = data.category_id
    await db.commit()
    await db.refresh(video)

    # Reload with relationships
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    return video_to_response(video)


@router.put("/{video_id}/tags", response_model=VideoResponse)
async def set_video_tags(
    video_id: int,
    data: SetTagsRequest,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Set video tags."""
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Get tags
    tags = []
    if data.tag_ids:
        tag_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        tags = list(tag_result.scalars().all())
        if len(tags) != len(data.tag_ids):
            raise HTTPException(status_code=400, detail="Some tags not found")

    video.tags = tags
    await db.commit()
    await db.refresh(video)

    # Reload with relationships
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    return video_to_response(video)


@router.post("/{video_id}/publish", response_model=VideoResponse)
async def publish_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """Publish a video (admin only)."""
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = VideoStatus.published
    video.reviewed_at = datetime.now()
    video.reviewed_by = current_user.id

    await db.commit()
    return video_to_response(video)


@router.post("/{video_id}/offline", response_model=VideoResponse)
async def offline_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """Take a video offline (admin only)."""
    result = await db.execute(
        select(VideoFile)
        .options(selectinload(VideoFile.category), selectinload(VideoFile.tags))
        .where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = VideoStatus.offline
    video.reviewed_at = datetime.now()
    video.reviewed_by = current_user.id

    await db.commit()
    return video_to_response(video)


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """Delete video and file (admin only)."""
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Build full paths from storage_path and relative paths
    file_path = settings.storage_path / video.file_path if video.file_path else None
    thumbnail_path = settings.storage_path / video.thumbnail if video.thumbnail else None

    await db.delete(video)
    await db.commit()

    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass

    try:
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
    except OSError:
        pass


@router.get("/{video_id}/play", response_model=VideoPlayResponse)
async def get_play_url(video_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    filename = os.path.basename(video.file_path)

    # Check file type
    if video.file_type == FileType.audio:
        # For audio files, return direct URL
        return VideoPlayResponse(
            audio_url=f"/audio/{filename}",
            file_type="audio"
        )
    else:
        # For video files, return HLS URL
        return VideoPlayResponse(
            hls_url=f"/vod/{filename}/index.m3u8",
            file_type="video"
        )


@router.post("/{video_id}/view")
async def increment_view(video_id: int, db: AsyncSession = Depends(get_db)):
    """Increment view count (public endpoint)."""
    result = await db.execute(
        update(VideoFile)
        .where(VideoFile.id == video_id)
        .values(view_count=VideoFile.view_count + 1)
        .returning(VideoFile.view_count)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Video not found")

    await db.commit()
    return {"view_count": row[0]}


@router.get("/{video_id}/stream")
async def stream_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """
    Stream video file directly (supports range requests).

    This endpoint is used by the video trim dialog to preview videos
    using the HTML5 video element.
    """
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Build full path from storage_path and relative file_path
    full_path = settings.storage_path / video.file_path if video.file_path else None
    if not full_path or not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    # Determine media type
    media_type = "video/mp4"
    filename = os.path.basename(full_path)

    return FileResponse(
        path=str(full_path),
        media_type=media_type,
        filename=filename,
    )
