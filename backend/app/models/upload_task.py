"""UploadTask model for chunked file uploads."""
import enum
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum
from sqlalchemy.sql import func

from app.database import Base


class UploadStatus(str, enum.Enum):
    """Upload task status enum."""
    uploading = "uploading"
    completed = "completed"
    failed = "failed"


class UploadTask(Base):
    """Chunked upload task model."""

    __tablename__ = "upload_tasks"

    id = Column(String(36), primary_key=True)  # UUID
    filename = Column(String(256), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    uploaded_chunks = Column(Integer, default=0, nullable=False)
    status = Column(Enum(UploadStatus), default=UploadStatus.uploading, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
