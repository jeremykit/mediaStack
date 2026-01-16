"""Upload API routes for chunked file uploads."""
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.database import get_db
from app.api.deps import get_current_user
from app.models import Admin, UploadTask, UploadStatus, VideoFile, SourceType, FileType, Tag
from app.schemas.upload import (
    UploadInitRequest, UploadInitResponse,
    UploadStatusResponse, UploadCompleteRequest, UploadChunkResponse
)
from app.services.uploader import (
    validate_file, create_upload_task, save_chunk,
    get_uploaded_chunks, merge_chunks, cleanup_temp,
    generate_thumbnail, get_media_duration
)
from app.config import settings

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/init", response_model=UploadInitResponse)
async def init_upload(
    data: UploadInitRequest,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Initialize a chunked upload task."""
    # Validate file
    is_valid, file_type, error = validate_file(data.filename, data.file_size)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Create upload task
    task_id, total_chunks = create_upload_task(
        data.filename, data.file_size, data.chunk_size
    )

    # Save to database
    upload_task = UploadTask(
        id=task_id,
        filename=data.filename,
        file_size=data.file_size,
        chunk_size=data.chunk_size,
        total_chunks=total_chunks,
        uploaded_chunks=0,
        status=UploadStatus.uploading
    )
    db.add(upload_task)
    await db.commit()

    return UploadInitResponse(
        task_id=task_id,
        chunk_size=data.chunk_size,
        total_chunks=total_chunks
    )


@router.post("/{task_id}/chunk", response_model=UploadChunkResponse)
async def upload_chunk(
    task_id: str,
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Upload a single chunk."""
    # Get upload task
    result = await db.execute(select(UploadTask).where(UploadTask.id == task_id))
    upload_task = result.scalar_one_or_none()
    if not upload_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload task not found"
        )

    if upload_task.status != UploadStatus.uploading:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload task is {upload_task.status}"
        )

    if chunk_index < 0 or chunk_index >= upload_task.total_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid chunk index. Must be 0-{upload_task.total_chunks - 1}"
        )

    # Read and save chunk
    chunk_data = await chunk.read()
    if not save_chunk(task_id, chunk_index, chunk_data):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save chunk"
        )

    # Update uploaded chunks count
    uploaded_chunks = len(get_uploaded_chunks(task_id))
    upload_task.uploaded_chunks = uploaded_chunks
    await db.commit()

    return UploadChunkResponse(
        chunk_index=chunk_index,
        uploaded_chunks=uploaded_chunks,
        total_chunks=upload_task.total_chunks
    )


@router.get("/{task_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Get upload task status."""
    result = await db.execute(select(UploadTask).where(UploadTask.id == task_id))
    upload_task = result.scalar_one_or_none()
    if not upload_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload task not found"
        )

    uploaded_chunk_indices = get_uploaded_chunks(task_id)

    return UploadStatusResponse(
        task_id=upload_task.id,
        filename=upload_task.filename,
        file_size=upload_task.file_size,
        chunk_size=upload_task.chunk_size,
        total_chunks=upload_task.total_chunks,
        uploaded_chunks=len(uploaded_chunk_indices),
        status=upload_task.status,
        uploaded_chunk_indices=uploaded_chunk_indices,
        created_at=upload_task.created_at
    )


@router.post("/{task_id}/complete")
async def complete_upload(
    task_id: str,
    data: Optional[UploadCompleteRequest] = None,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Complete upload and create video file."""
    result = await db.execute(select(UploadTask).where(UploadTask.id == task_id))
    upload_task = result.scalar_one_or_none()
    if not upload_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload task not found"
        )

    if upload_task.status != UploadStatus.uploading:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload task is {upload_task.status}"
        )

    # Check all chunks uploaded
    uploaded_chunks = get_uploaded_chunks(task_id)
    if len(uploaded_chunks) != upload_task.total_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing chunks. Uploaded: {len(uploaded_chunks)}, Expected: {upload_task.total_chunks}"
        )

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(upload_task.filename)[1].lower()
    output_filename = f"upload_{timestamp}_{task_id[:8]}{ext}"

    # Merge chunks
    output_path = merge_chunks(task_id, upload_task.total_chunks, output_filename)
    if not output_path:
        upload_task.status = UploadStatus.failed
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to merge chunks"
        )

    # Determine file type
    is_video = ext in {'.mp4'}
    file_type = FileType.video if is_video else FileType.audio

    # Generate thumbnail for video
    thumbnail_path = None
    if is_video:
        thumbnail_path = await generate_thumbnail(output_path)

    # Get duration
    duration = await get_media_duration(output_path)

    # Get file size
    file_size = output_path.stat().st_size

    # Create video file record
    title = data.title if data and data.title else os.path.splitext(upload_task.filename)[0]

    video_file = VideoFile(
        title=title,
        file_path=str(output_path.relative_to(settings.storage_path)),
        file_size=file_size,
        duration=duration,
        thumbnail=str(thumbnail_path.relative_to(settings.storage_path)) if thumbnail_path else None,
        source_type=SourceType.uploaded,
        file_type=file_type,
        category_id=data.category_id if data else None
    )

    # Add tags
    if data and data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        tags = list(result.scalars().all())
        video_file.tags = tags

    db.add(video_file)

    # Update upload task status
    upload_task.status = UploadStatus.completed
    await db.commit()

    # Cleanup temp files
    cleanup_temp(task_id)

    await db.refresh(video_file)

    return {
        "message": "Upload completed",
        "video_id": video_file.id,
        "title": video_file.title,
        "file_path": video_file.file_path
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_upload(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Cancel and delete an upload task."""
    result = await db.execute(select(UploadTask).where(UploadTask.id == task_id))
    upload_task = result.scalar_one_or_none()
    if not upload_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload task not found"
        )

    # Cleanup temp files
    cleanup_temp(task_id)

    # Delete from database
    await db.delete(upload_task)
    await db.commit()
