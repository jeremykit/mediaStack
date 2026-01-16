"""Tag management API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.api.deps import get_current_user
from app.models import Admin, Tag
from app.models.video_tag import video_tags
from app.schemas.tag import TagCreate, TagResponse

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=List[TagResponse])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """Get all tags with video count."""
    result = await db.execute(
        select(
            Tag,
            func.count(video_tags.c.video_id).label("video_count")
        )
        .outerjoin(video_tags, video_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    rows = result.all()

    tags = []
    for row in rows:
        tag = row[0]
        video_count = row[1]
        tags.append(TagResponse(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at,
            video_count=video_count
        ))
    return tags


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Create a new tag."""
    # Check if name already exists
    result = await db.execute(select(Tag).where(Tag.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists"
        )

    tag = Tag(name=data.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        created_at=tag.created_at,
        video_count=0
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Delete a tag."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    await db.delete(tag)
    await db.commit()
