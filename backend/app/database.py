from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def ensure_default_category():
    """Ensure the default '未分类' category exists."""
    from app.models.category import Category
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(select(Category).where(Category.name == "未分类"))
        if not result.scalar_one_or_none():
            default_category = Category(name="未分类", sort_order=0)
            db.add(default_category)
            await db.commit()
