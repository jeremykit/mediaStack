import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

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
    """Ensure the default '未分类' category exists.

    Creates a category with name='未分类' and sort_order=0 if it doesn't exist.
    """
    from app.models.category import Category
    from sqlalchemy import select

    try:
        async with async_session() as db:
            result = await db.execute(select(Category).where(Category.name == "未分类"))
            if not result.scalar_one_or_none():
                default_category = Category(name="未分类", sort_order=0)
                db.add(default_category)
                await db.commit()
                logger.info("Created default '未分类' category")
            else:
                logger.debug("Default '未分类' category already exists")
    except Exception as e:
        logger.error(f"Failed to ensure default category: {e}")
        raise
