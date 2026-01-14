from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.models import Admin
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_initial_admin(db: AsyncSession):
    result = await db.execute(select(Admin).where(Admin.username == settings.admin_username))
    if result.scalar_one_or_none():
        return
    admin = Admin(
        username=settings.admin_username,
        password_hash=pwd_context.hash(settings.admin_password)
    )
    db.add(admin)
    await db.commit()
