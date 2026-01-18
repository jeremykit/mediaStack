"""VideoTrimTask model for video trimming operations."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TrimStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class VideoTrimTask(Base):
    """Video trim task model for tracking video trimming jobs."""

    __tablename__ = "video_trim_tasks"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(TrimStatus), default=TrimStatus.pending, index=True)

    # Trim parameters
    start_time = Column(Integer, nullable=False)  # seconds
    end_time = Column(Integer, nullable=False)    # seconds

    # Options
    extract_audio = Column(Boolean, default=False)
    keep_original = Column(Boolean, default=False)
    audio_bitrate = Column(String(8), default="192k")

    # Output paths
    trimmed_video_path = Column(String(512), nullable=True)
    extracted_audio_path = Column(String(512), nullable=True)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    video = relationship("VideoFile", back_populates="trim_tasks")

    # Indexes
    __table_args__ = (
        Index("ix_video_trim_tasks_video_id", "video_id"),
    )
