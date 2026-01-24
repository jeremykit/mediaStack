"""Category model for video classification."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    """Video category model."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), unique=True, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    videos = relationship("VideoFile", back_populates="category")
    sources = relationship("LiveSource", back_populates="category")
    view_codes = relationship(
        "ViewCode",
        secondary="view_code_categories",
        back_populates="categories"
    )
