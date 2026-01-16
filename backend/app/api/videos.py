from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
import os

from app.database import get_db
from app.models import Admin, VideoFile, Tag, Category
from app.schemas.video import (
    VideoUpdate, VideoResponse, VideoPlayResponse,
    SetCategoryRequest, SetTagsRequest
)
from app.schemas.category import CategoryListResponse
from app.schemas.tag import TagListResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/videos", tags=["videos"])


def video_to_response(video: VideoFile) -> VideoResponse:
    """Convert VideoFile model to VideoResponse."""
    return VideoResponse(
        id=video.id,
        task_id=video.task_id,
        category_id=video.category_id,
        title=video.title,
        file_path=video.file_path,
        file_size=video.file_size,
        duration=video.duration,
        thumbnail=video.thumbnail,
        view_count=video.view_count,
        source_type=video.source_type,
        file_type=video.file_type,
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

    file_path = video.file_path
    thumbnail_path = video.thumbnail

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
    return VideoPlayResponse(hls_url=f"/vod/{filename}/index.m3u8")


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
