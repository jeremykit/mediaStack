from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_free: int
    disk_percent: float
