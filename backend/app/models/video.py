from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class SourceType(str, enum.Enum):
    recorded = "recorded"
    uploaded = "uploaded"

class VideoFile(Base):
    __tablename__ = "video_files"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("record_tasks.id"), nullable=True)
    title = Column(String(128), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    duration = Column(Integer, nullable=True)
    thumbnail = Column(String(512), nullable=True)
    view_count = Column(Integer, default=0)
    source_type = Column(Enum(SourceType), default=SourceType.recorded)
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("RecordTask", back_populates="video")
