from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class ProtocolType(str, enum.Enum):
    rtmp = "rtmp"
    hls = "hls"

class LiveSource(Base):
    __tablename__ = "live_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    protocol = Column(Enum(ProtocolType), nullable=False)
    url = Column(String(512), nullable=False)
    retention_days = Column(Integer, default=365)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_check_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tasks = relationship("RecordTask", back_populates="source")
    schedules = relationship("Schedule", back_populates="source")
