from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
import os

from app.database import get_db
from app.models import Admin, VideoFile
from app.schemas.video import VideoUpdate, VideoResponse, VideoPlayResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.get("", response_model=List[VideoResponse])
async def list_videos(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(VideoFile).order_by(VideoFile.id.desc())
    if search:
        query = query.where(VideoFile.title.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    for key, value in video_update.model_dump(exclude_unset=True).items():
        setattr(video, key, value)

    await db.commit()
    await db.refresh(video)
    return video

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
