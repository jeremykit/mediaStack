"""VideoImage model for video gallery images."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class VideoImage(Base):
    """Video image model for storing gallery images associated with videos."""

    __tablename__ = "video_images"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(512), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    video = relationship("VideoFile", back_populates="images")

    # Indexes
    __table_args__ = (
        Index("ix_video_images_video_id", "video_id"),
        Index("ix_video_images_sort_order", "video_id", "sort_order"),
    )
