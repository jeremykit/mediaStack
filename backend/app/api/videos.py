from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.file_path and os.path.exists(video.file_path):
        os.remove(video.file_path)
    if video.thumbnail and os.path.exists(video.thumbnail):
        os.remove(video.thumbnail)

    await db.delete(video)
    await db.commit()

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
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.view_count += 1
    await db.commit()
    return {"view_count": video.view_count}
