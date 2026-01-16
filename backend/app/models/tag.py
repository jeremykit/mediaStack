"""Tag model for video tagging."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Tag(Base):
    """Video tag model."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    videos = relationship(
        "VideoFile",
        secondary="video_tags",
        back_populates="tags"
    )
