"""Audio extraction API endpoints."""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import re

from app.database import get_db
from app.models import Admin, VideoFile, AudioExtractTask, AudioExtractStatus, FileType
from app.schemas.audio import (
    AudioExtractRequest,
    AudioExtractTaskResponse,
    AudioInfoResponse
)
from app.api.deps import get_current_user
from app.services.audio_extractor import AudioExtractorService
from app.config import settings

router = APIRouter(prefix="/api/videos", tags=["audio"])


@router.post("/{video_id}/extract-audio", response_model=AudioExtractTaskResponse)
async def extract_audio(
    video_id: int,
    request: AudioExtractRequest = AudioExtractRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    Start audio extraction from a video file.

    Requires admin authentication.
    Returns immediately with task info - extraction runs in background.
    """
    try:
        task = await AudioExtractorService.start_extraction(
            video_id=video_id,
            db=db,
            format=request.format,
            bitrate=request.bitrate
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{video_id}/audio", response_model=AudioInfoResponse)
async def get_audio_info(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    Get audio extraction information for a video.

    Requires admin authentication.
    Returns task status and download URL if audio is available.
    """
    # Check if video exists
    result = await db.execute(
        select(VideoFile).where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # If this is an audio file (uploaded audio), return the file itself
    if video.file_type == FileType.audio:
        video_path = Path(video.file_path)
        if not video_path.is_absolute():
            video_path = settings.storage_path / video.file_path

        if video_path.exists():
            filename = os.path.basename(video.file_path)
            return AudioInfoResponse(
                video_id=video_id,
                has_audio=True,
                task=None,
                download_url=f"/audio/{filename}",
                file_size=video_path.stat().st_size
            )

    # Get latest task for extracted audio
    task = await AudioExtractorService.get_task(video_id, db)

    if not task:
        return AudioInfoResponse(
            video_id=video_id,
            has_audio=False,
            task=None,
            download_url=None,
            file_size=None
        )

    # Check if audio file exists
    has_audio = False
    download_url = None
    file_size = None

    if task.status == AudioExtractStatus.completed and task.output_path:
        audio_path = Path(task.output_path)
        if audio_path.exists():
            has_audio = True
            download_url = f"/api/videos/{video_id}/audio/download"
            file_size = audio_path.stat().st_size

    return AudioInfoResponse(
        video_id=video_id,
        has_audio=has_audio,
        task=AudioExtractTaskResponse(
            id=task.id,
            video_id=task.video_id,
            status=task.status,
            output_path=task.output_path,
            format=task.format,
            bitrate=task.bitrate,
            created_at=task.created_at,
            completed_at=task.completed_at
        ),
        download_url=download_url,
        file_size=file_size
    )


@router.get("/{video_id}/audio/download")
async def download_audio(
    video_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Download extracted audio file.

    This endpoint is public (no authentication required).
    Returns the audio file for download.
    """
    # Check if video exists
    result = await db.execute(
        select(VideoFile).where(VideoFile.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Get completed task
    task = await AudioExtractorService.get_completed_task(video_id, db)
    if not task or not task.output_path:
        raise HTTPException(status_code=404, detail="Audio not available")

    # Validate path is within audio directory (prevent path traversal)
    audio_dir = Path(settings.storage_path) / "audio"
    audio_path = Path(task.output_path)

    try:
        # Verify file path is within the audio directory
        audio_path.resolve().relative_to(audio_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Generate safe download filename
    safe_title = re.sub(r'[^\w\s\-\.]', '', video.title)
    safe_title = safe_title.strip() or 'audio'
    filename = f"{safe_title}.{task.format}"

    return FileResponse(
        path=str(audio_path),
        filename=filename,
        media_type=f"audio/{task.format}"
    )
