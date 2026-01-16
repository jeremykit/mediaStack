"""Category management API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.api.deps import get_current_user
from app.models import Admin, Category, VideoFile
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all categories sorted by sort_order."""
    # Get categories with video count
    result = await db.execute(
        select(
            Category,
            func.count(VideoFile.id).label("video_count")
        )
        .outerjoin(VideoFile, VideoFile.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.sort_order, Category.id)
    )
    rows = result.all()

    categories = []
    for row in rows:
        category = row[0]
        video_count = row[1]
        categories.append(CategoryResponse(
            id=category.id,
            name=category.name,
            sort_order=category.sort_order,
            created_at=category.created_at,
            video_count=video_count
        ))
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Create a new category."""
    # Check if name already exists
    result = await db.execute(select(Category).where(Category.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )

    category = Category(name=data.name, sort_order=data.sort_order)
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        sort_order=category.sort_order,
        created_at=category.created_at,
        video_count=0
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Update a category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check name uniqueness if updating name
    if data.name and data.name != category.name:
        result = await db.execute(select(Category).where(Category.name == data.name))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
        category.name = data.name

    if data.sort_order is not None:
        category.sort_order = data.sort_order

    await db.commit()
    await db.refresh(category)

    # Get video count
    count_result = await db.execute(
        select(func.count(VideoFile.id)).where(VideoFile.category_id == category_id)
    )
    video_count = count_result.scalar() or 0

    return CategoryResponse(
        id=category.id,
        name=category.name,
        sort_order=category.sort_order,
        created_at=category.created_at,
        video_count=video_count
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Delete a category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if category has videos
    count_result = await db.execute(
        select(func.count(VideoFile.id)).where(VideoFile.category_id == category_id)
    )
    video_count = count_result.scalar() or 0
    if video_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {video_count} videos"
        )

    await db.delete(category)
    await db.commit()
