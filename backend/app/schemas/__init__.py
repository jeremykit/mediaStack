from app.schemas.auth import LoginRequest, TokenResponse, AdminResponse
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse, SourceStatusResponse
from app.schemas.task import TaskResponse, TaskWithSourceResponse
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleWithSourceResponse
from app.schemas.video import VideoUpdate, VideoResponse, VideoPlayResponse
from app.schemas.system import SystemStatusResponse

__all__ = [
    "LoginRequest", "TokenResponse", "AdminResponse",
    "SourceCreate", "SourceUpdate", "SourceResponse", "SourceStatusResponse",
    "TaskResponse", "TaskWithSourceResponse",
    "ScheduleCreate", "ScheduleUpdate", "ScheduleResponse", "ScheduleWithSourceResponse",
    "VideoUpdate", "VideoResponse", "VideoPlayResponse",
    "SystemStatusResponse",
]
