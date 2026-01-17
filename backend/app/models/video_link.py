"""VideoLink model for video external links."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class VideoLink(Base):
    """Video link model for storing external links associated with videos."""

    __tablename__ = "video_links"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(64), nullable=False)
    url = Column(String(512), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    video = relationship("VideoFile", back_populates="links")

    # Indexes
    __table_args__ = (
        Index("ix_video_links_video_id", "video_id"),
        Index("ix_video_links_sort_order", "video_id", "sort_order"),
    )
