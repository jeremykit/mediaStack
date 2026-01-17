"""Thumbnail management API endpoints."""
import asyncio
import uuid
from pathlib import Path

import aiofiles
import aiofiles.os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Admin, VideoFile
from app.schemas.thumbnail import ThumbnailCaptureRequest, ThumbnailResponse
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/videos", tags=["thumbnail"])

# Allowed image extensions and max size for upload
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_THUMBNAIL_SIZE = 5 * 1024 * 1024  # 5MB


async def get_video_or_404(video_id: int, db: AsyncSession) -> VideoFile:
    """Get video by ID or raise 404."""
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


async def get_video_duration(video_path: str) -> float:
    """Get video duration using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()

        if process.returncode == 0 and stdout:
            return float(stdout.decode().strip())
    except (ValueError, Exception):
        pass

    return 0.0


async def capture_thumbnail(video_path: str, output_path: Path, timestamp: float) -> bool:
    """Capture a thumbnail from video at specified timestamp using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        str(output_path)
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        return process.returncode == 0 and output_path.exists()
    except Exception:
        return False


def ensure_thumbnails_dir() -> Path:
    """Ensure thumbnails directory exists and return its path."""
    thumbnails_dir = settings.storage_path / "thumbnails"
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    return thumbnails_dir


async def delete_old_thumbnail(thumbnail_path: str | None) -> None:
    """Delete old thumbnail file if it exists within the thumbnails directory."""
    if not thumbnail_path:
        return

    thumbnails_dir = settings.storage_path / "thumbnails"
    old_path = Path(thumbnail_path)

    try:
        # Verify file path is within the thumbnails directory (path traversal protection)
        old_path.resolve().relative_to(thumbnails_dir.resolve())
        if old_path.exists():
            await aiofiles.os.remove(str(old_path))
    except (ValueError, OSError):
        # Path not in thumbnails directory or deletion failed, ignore
        pass


@router.post("/{video_id}/thumbnail/auto", response_model=ThumbnailResponse)
async def auto_capture_thumbnail(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """
    Automatically capture thumbnail from the middle of the video.

    Requires admin authentication.
    Captures a frame from the middle of the video duration.
    """
    video = await get_video_or_404(video_id, db)

    # Verify video file exists
    video_path = Path(video.file_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    # Get video duration
    duration = await get_video_duration(str(video_path))
    if duration <= 0:
        # If we can't get duration, try to use stored duration or default to 0
        duration = float(video.duration) if video.duration else 0.0

    # Calculate middle timestamp
    timestamp = duration / 2 if duration > 0 else 0.0

    # Create thumbnails directory
    thumbnails_dir = ensure_thumbnails_dir()

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.jpg"
    output_path = thumbnails_dir / unique_filename

    # Capture thumbnail
    success = await capture_thumbnail(str(video_path), output_path, timestamp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to capture thumbnail from video")

    # Delete old thumbnail if exists
    await delete_old_thumbnail(video.thumbnail)

    # Update video record
    video.thumbnail = str(output_path)
    await db.commit()
    await db.refresh(video)

    # Return thumbnail URL
    thumbnail_url = f"/thumbnails/{unique_filename}"
    return ThumbnailResponse(video_id=video_id, thumbnail_url=thumbnail_url)


@router.post("/{video_id}/thumbnail/upload", response_model=ThumbnailResponse)
async def upload_thumbnail(
    video_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """
    Upload a custom thumbnail image for a video.

    Requires admin authentication.
    Accepts jpg, png, webp images up to 5MB.
    """
    video = await get_video_or_404(video_id, db)

    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_THUMBNAIL_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_THUMBNAIL_SIZE // (1024 * 1024)}MB"
        )

    # Create thumbnails directory
    thumbnails_dir = ensure_thumbnails_dir()

    # Generate unique filename (always save as original extension)
    unique_filename = f"{uuid.uuid4()}{ext}"
    output_path = thumbnails_dir / unique_filename

    # Save file
    async with aiofiles.open(output_path, "wb") as f:
        await f.write(content)

    # Delete old thumbnail if exists
    await delete_old_thumbnail(video.thumbnail)

    # Update video record
    video.thumbnail = str(output_path)
    await db.commit()
    await db.refresh(video)

    # Return thumbnail URL
    thumbnail_url = f"/thumbnails/{unique_filename}"
    return ThumbnailResponse(video_id=video_id, thumbnail_url=thumbnail_url)


@router.post("/{video_id}/thumbnail/capture", response_model=ThumbnailResponse)
async def capture_thumbnail_at_time(
    video_id: int,
    request: ThumbnailCaptureRequest,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """
    Capture thumbnail at a specific timestamp in the video.

    Requires admin authentication.
    Timestamp is specified in seconds.
    """
    video = await get_video_or_404(video_id, db)

    # Verify video file exists
    video_path = Path(video.file_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    # Validate timestamp against video duration
    duration = await get_video_duration(str(video_path))
    if duration > 0 and request.timestamp > duration:
        raise HTTPException(
            status_code=400,
            detail=f"Timestamp {request.timestamp}s exceeds video duration {duration:.2f}s"
        )

    # Create thumbnails directory
    thumbnails_dir = ensure_thumbnails_dir()

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.jpg"
    output_path = thumbnails_dir / unique_filename

    # Capture thumbnail
    success = await capture_thumbnail(str(video_path), output_path, request.timestamp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to capture thumbnail from video")

    # Delete old thumbnail if exists
    await delete_old_thumbnail(video.thumbnail)

    # Update video record
    video.thumbnail = str(output_path)
    await db.commit()
    await db.refresh(video)

    # Return thumbnail URL
    thumbnail_url = f"/thumbnails/{unique_filename}"
    return ThumbnailResponse(video_id=video_id, thumbnail_url=thumbnail_url)
