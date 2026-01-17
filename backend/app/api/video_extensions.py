"""API endpoints for video extension resources (images, texts, links)."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pathlib import Path
import uuid
import os
import aiofiles
import aiofiles.os

from app.database import get_db
from app.models import Admin, VideoFile, VideoImage, VideoText, VideoLink
from app.schemas.video_extensions import (
    VideoImageResponse,
    VideoTextCreate, VideoTextUpdate, VideoTextResponse,
    VideoLinkCreate, VideoLinkResponse
)
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/videos", tags=["video-extensions"])

# Allowed image extensions and max size
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


async def get_video_or_404(video_id: int, db: AsyncSession) -> VideoFile:
    """Get video by ID or raise 404."""
    result = await db.execute(select(VideoFile).where(VideoFile.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


def image_to_response(image: VideoImage) -> VideoImageResponse:
    """Convert VideoImage model to response schema with URL instead of absolute path."""
    filename = os.path.basename(image.image_path)
    return VideoImageResponse(
        id=image.id,
        video_id=image.video_id,
        image_path=image.image_path,
        image_url=f"/api/images/{filename}",
        sort_order=image.sort_order,
        created_at=image.created_at
    )


# ============ Video Image Endpoints ============

@router.get("/{video_id}/images", response_model=List[VideoImageResponse])
async def list_video_images(
    video_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all images associated with a video."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoImage)
        .where(VideoImage.video_id == video_id)
        .order_by(VideoImage.sort_order, VideoImage.id)
    )
    images = result.scalars().all()
    return [image_to_response(image) for image in images]


@router.post("/{video_id}/images", response_model=VideoImageResponse)
async def create_video_image(
    video_id: int,
    file: UploadFile = File(...),
    sort_order: int = 0,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Upload and add an image to a video (admin only)."""
    await get_video_or_404(video_id, db)

    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE // (1024 * 1024)}MB"
        )

    # Create images directory if not exists
    images_dir = settings.storage_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = images_dir / unique_filename

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Create database record
    image = VideoImage(
        video_id=video_id,
        image_path=str(file_path),
        sort_order=sort_order
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)

    return image_to_response(image)


@router.delete("/{video_id}/images/{image_id}", status_code=204)
async def delete_video_image(
    video_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Delete an image from a video (admin only)."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoImage)
        .where(VideoImage.id == image_id, VideoImage.video_id == video_id)
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = image.image_path

    await db.delete(image)
    await db.commit()

    # Delete file from disk with path traversal protection
    images_dir = Path(settings.storage_path) / "images"
    if file_path:
        file_path_obj = Path(file_path)
        try:
            # 验证文件路径在 images 目录内
            file_path_obj.resolve().relative_to(images_dir.resolve())
            if file_path_obj.exists():
                await aiofiles.os.remove(file_path)
        except (ValueError, OSError):
            # 路径不在 images 目录内或删除失败，忽略
            pass


# ============ Video Text Endpoints ============

@router.get("/{video_id}/texts", response_model=List[VideoTextResponse])
async def list_video_texts(
    video_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all texts associated with a video."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoText)
        .where(VideoText.video_id == video_id)
        .order_by(VideoText.sort_order, VideoText.id)
    )
    texts = result.scalars().all()
    return texts


@router.post("/{video_id}/texts", response_model=VideoTextResponse)
async def create_video_text(
    video_id: int,
    data: VideoTextCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Add a text to a video (admin only)."""
    await get_video_or_404(video_id, db)

    text = VideoText(
        video_id=video_id,
        title=data.title,
        content=data.content,
        sort_order=data.sort_order
    )
    db.add(text)
    await db.commit()
    await db.refresh(text)

    return text


@router.put("/{video_id}/texts/{text_id}", response_model=VideoTextResponse)
async def update_video_text(
    video_id: int,
    text_id: int,
    data: VideoTextUpdate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Update a text associated with a video (admin only)."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoText)
        .where(VideoText.id == text_id, VideoText.video_id == video_id)
    )
    text = result.scalar_one_or_none()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(text, key, value)

    await db.commit()
    await db.refresh(text)

    return text


@router.delete("/{video_id}/texts/{text_id}", status_code=204)
async def delete_video_text(
    video_id: int,
    text_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Delete a text from a video (admin only)."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoText)
        .where(VideoText.id == text_id, VideoText.video_id == video_id)
    )
    text = result.scalar_one_or_none()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")

    await db.delete(text)
    await db.commit()


# ============ Video Link Endpoints ============

@router.get("/{video_id}/links", response_model=List[VideoLinkResponse])
async def list_video_links(
    video_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all links associated with a video."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoLink)
        .where(VideoLink.video_id == video_id)
        .order_by(VideoLink.sort_order, VideoLink.id)
    )
    links = result.scalars().all()
    return links


@router.post("/{video_id}/links", response_model=VideoLinkResponse)
async def create_video_link(
    video_id: int,
    data: VideoLinkCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Add a link to a video (admin only)."""
    await get_video_or_404(video_id, db)

    link = VideoLink(
        video_id=video_id,
        title=data.title,
        url=data.url,
        sort_order=data.sort_order
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)

    return link


@router.delete("/{video_id}/links/{link_id}", status_code=204)
async def delete_video_link(
    video_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Delete a link from a video (admin only)."""
    await get_video_or_404(video_id, db)

    result = await db.execute(
        select(VideoLink)
        .where(VideoLink.id == link_id, VideoLink.video_id == video_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await db.delete(link)
    await db.commit()
