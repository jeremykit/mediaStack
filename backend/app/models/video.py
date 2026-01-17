from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class SourceType(str, enum.Enum):
    recorded = "recorded"
    uploaded = "uploaded"


class FileType(str, enum.Enum):
    video = "video"
    audio = "audio"


class VideoStatus(str, enum.Enum):
    pending = "pending"
    published = "published"
    offline = "offline"


class VideoFile(Base):
    __tablename__ = "video_files"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("record_tasks.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    duration = Column(Integer, nullable=True)
    thumbnail = Column(String(512), nullable=True)
    view_count = Column(Integer, default=0)
    source_type = Column(Enum(SourceType), default=SourceType.recorded)
    file_type = Column(Enum(FileType), default=FileType.video)
    status = Column(Enum(VideoStatus), default=VideoStatus.pending, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    task = relationship("RecordTask", back_populates="video")
    category = relationship("Category", back_populates="videos")
    reviewer = relationship("Admin", foreign_keys=[reviewed_by])
    tags = relationship(
        "Tag",
        secondary="video_tags",
        back_populates="videos"
    )
    images = relationship("VideoImage", back_populates="video", cascade="all, delete-orphan")
    texts = relationship("VideoText", back_populates="video", cascade="all, delete-orphan")
    links = relationship("VideoLink", back_populates="video", cascade="all, delete-orphan")
    audio_extract_tasks = relationship("AudioExtractTask", back_populates="video", cascade="all, delete-orphan")
