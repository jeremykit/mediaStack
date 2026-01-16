"""View code management API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone

from app.database import get_db
from app.api.deps import get_current_user
from app.models import Admin, ViewCode, Category
from app.schemas.view_code import (
    ViewCodeCreate, ViewCodeUpdate, ViewCodeResponse,
    ViewCodeVerifyRequest, ViewCodeVerifyResponse
)

router = APIRouter(prefix="/api/view-codes", tags=["view-codes"])


@router.get("", response_model=List[ViewCodeResponse])
async def get_view_codes(
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Get all view codes."""
    result = await db.execute(
        select(ViewCode)
        .options(selectinload(ViewCode.categories))
        .order_by(ViewCode.created_at.desc())
    )
    view_codes = result.scalars().all()

    return [
        ViewCodeResponse(
            id=vc.id,
            code=vc.code,
            is_active=vc.is_active,
            created_at=vc.created_at,
            expires_at=vc.expires_at,
            category_ids=[c.id for c in vc.categories],
            category_names=[c.name for c in vc.categories]
        )
        for vc in view_codes
    ]


@router.post("", response_model=ViewCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_view_code(
    data: ViewCodeCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Create a new view code."""
    # Check if code already exists
    result = await db.execute(select(ViewCode).where(ViewCode.code == data.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="View code already exists"
        )

    # Get categories
    categories = []
    if data.category_ids:
        result = await db.execute(
            select(Category).where(Category.id.in_(data.category_ids))
        )
        categories = list(result.scalars().all())
        if len(categories) != len(data.category_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some categories not found"
            )

    view_code = ViewCode(
        code=data.code,
        is_active=data.is_active,
        expires_at=data.expires_at
    )
    view_code.categories = categories
    db.add(view_code)
    await db.commit()
    await db.refresh(view_code)

    return ViewCodeResponse(
        id=view_code.id,
        code=view_code.code,
        is_active=view_code.is_active,
        created_at=view_code.created_at,
        expires_at=view_code.expires_at,
        category_ids=[c.id for c in categories],
        category_names=[c.name for c in categories]
    )


@router.put("/{view_code_id}", response_model=ViewCodeResponse)
async def update_view_code(
    view_code_id: int,
    data: ViewCodeUpdate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Update a view code."""
    result = await db.execute(
        select(ViewCode)
        .options(selectinload(ViewCode.categories))
        .where(ViewCode.id == view_code_id)
    )
    view_code = result.scalar_one_or_none()
    if not view_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="View code not found"
        )

    if data.is_active is not None:
        view_code.is_active = data.is_active

    if data.expires_at is not None:
        view_code.expires_at = data.expires_at

    if data.category_ids is not None:
        categories = []
        if data.category_ids:
            result = await db.execute(
                select(Category).where(Category.id.in_(data.category_ids))
            )
            categories = list(result.scalars().all())
            if len(categories) != len(data.category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some categories not found"
                )
        view_code.categories = categories

    await db.commit()
    await db.refresh(view_code)

    return ViewCodeResponse(
        id=view_code.id,
        code=view_code.code,
        is_active=view_code.is_active,
        created_at=view_code.created_at,
        expires_at=view_code.expires_at,
        category_ids=[c.id for c in view_code.categories],
        category_names=[c.name for c in view_code.categories]
    )


@router.delete("/{view_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_view_code(
    view_code_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_user)
):
    """Delete a view code."""
    result = await db.execute(select(ViewCode).where(ViewCode.id == view_code_id))
    view_code = result.scalar_one_or_none()
    if not view_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="View code not found"
        )

    await db.delete(view_code)
    await db.commit()


@router.post("/verify", response_model=ViewCodeVerifyResponse)
async def verify_view_code(
    data: ViewCodeVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify a view code and return accessible categories."""
    result = await db.execute(
        select(ViewCode)
        .options(selectinload(ViewCode.categories))
        .where(ViewCode.code == data.code)
    )
    view_code = result.scalar_one_or_none()

    if not view_code:
        return ViewCodeVerifyResponse(valid=False)

    if not view_code.is_active:
        return ViewCodeVerifyResponse(valid=False)

    if view_code.expires_at:
        now = datetime.now(timezone.utc)
        expires_at = view_code.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now > expires_at:
            return ViewCodeVerifyResponse(valid=False)

    return ViewCodeVerifyResponse(
        valid=True,
        category_ids=[c.id for c in view_code.categories],
        expires_at=view_code.expires_at
    )
