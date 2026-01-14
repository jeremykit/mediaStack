from fastapi import APIRouter, Depends
import psutil

from app.models import Admin
from app.api.deps import get_current_user
from app.schemas.system import SystemStatusResponse
from app.config import settings

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(current_user: Admin = Depends(get_current_user)):
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(str(settings.storage_path))

    return SystemStatusResponse(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_total=disk.total,
        disk_used=disk.used,
        disk_free=disk.free,
        disk_percent=disk.percent,
    )
