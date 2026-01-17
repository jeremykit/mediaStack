"""AudioExtractTask model for audio extraction from videos."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class AudioExtractStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class AudioExtractTask(Base):
    """Audio extract task model for tracking audio extraction jobs from videos."""

    __tablename__ = "audio_extract_tasks"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AudioExtractStatus), default=AudioExtractStatus.pending, index=True)
    output_path = Column(String(512), nullable=True)
    format = Column(String(8), default="mp3", nullable=False)
    bitrate = Column(String(8), default="128k", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    video = relationship("VideoFile", back_populates="audio_extract_tasks")

    # Indexes
    __table_args__ = (
        Index("ix_audio_extract_tasks_video_id", "video_id"),
    )
