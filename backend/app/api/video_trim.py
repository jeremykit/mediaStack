"""API endpoints for video trimming."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db, get_current_user
from app.models import Admin
from app.schemas.video_trim import TrimVideoRequest, TrimTaskResponse
from app.services.video_trimmer import VideoTrimmerService

router = APIRouter(prefix="/api", tags=["video-trim"])


@router.post("/videos/{video_id}/trim", response_model=TrimTaskResponse)
async def trim_video(
    video_id: int,
    request: TrimVideoRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_user),
):
    """
    Start trimming a video.

    Only recorded videos (source_type='recorded') can be trimmed.
    After trimming, the video status is reset to 'pending' for re-approval.
    """
    try:
        task = await VideoTrimmerService.start_trimming(
            video_id=video_id,
            start_time=request.start_time,
            end_time=request.end_time,
            extract_audio=request.extract_audio,
            keep_original=request.keep_original,
            db=db,
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start trimming: {str(e)}"
        )


@router.get("/videos/{video_id}/trim/tasks", response_model=List[TrimTaskResponse])
async def get_video_trim_tasks(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_user),
):
    """Get all trim tasks for a video."""
    from sqlalchemy import select
    from app.models import VideoTrimTask

    result = await db.execute(
        select(VideoTrimTask)
        .where(VideoTrimTask.video_id == video_id)
        .order_by(VideoTrimTask.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks


@router.get("/videos/trim/tasks/{task_id}", response_model=TrimTaskResponse)
async def get_trim_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_user),
):
    """Get a specific trim task by ID (for polling status)."""
    task = await VideoTrimmerService.get_task_by_id(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Trim task not found")
    return task


@router.delete("/videos/trim/tasks/{task_id}")
async def cancel_trim_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_user),
):
    """Cancel an ongoing trim task."""
    success = await VideoTrimmerService.cancel_task(task_id, db)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be cancelled (not found or not processing)",
        )
    return {"message": "Trim task cancelled successfully"}
