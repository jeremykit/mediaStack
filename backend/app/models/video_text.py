"""VideoText model for video rich text content."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class VideoText(Base):
    """Video text model for storing rich text content associated with videos."""

    __tablename__ = "video_texts"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(64), nullable=False)
    content = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    video = relationship("VideoFile", back_populates="texts")

    # Indexes
    __table_args__ = (
        Index("ix_video_texts_video_id", "video_id"),
        Index("ix_video_texts_sort_order", "video_id", "sort_order"),
    )
