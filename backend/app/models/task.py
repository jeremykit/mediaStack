from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class TaskStatus(str, enum.Enum):
    pending = "pending"
    recording = "recording"
    completed = "completed"
    failed = "failed"
    interrupted = "interrupted"

class RecordTask(Base):
    __tablename__ = "record_tasks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("live_sources.id"), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    file_path = Column(String(512), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    duration = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    source = relationship("LiveSource", back_populates="tasks")
    video = relationship("VideoFile", back_populates="task", uselist=False)
