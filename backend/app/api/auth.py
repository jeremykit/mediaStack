from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.database import get_db
from app.models import Admin
from app.schemas.auth import TokenResponse, AdminResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Admin).where(Admin.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login_at = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token)

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=AdminResponse)
async def get_me(current_user: Admin = Depends(get_current_user)):
    return current_user
