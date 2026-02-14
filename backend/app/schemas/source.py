from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.source import ProtocolType
from app.schemas.category import CategoryListResponse


class SourceCreate(BaseModel):
    name: str
    protocol: ProtocolType
    url: str
    retention_days: int = 365
    is_active: bool = True
    category_id: Optional[int] = None


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    protocol: Optional[ProtocolType] = None
    url: Optional[str] = None
    retention_days: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    protocol: ProtocolType
    url: str
    retention_days: int
    is_active: bool
    is_online: bool
    last_check_time: Optional[datetime]
    is_recording: bool = False
    category: Optional[CategoryListResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceStatusResponse(BaseModel):
    online: bool
    message: str


class BulkUpdateCategoryRequest(BaseModel):
    source_ids: List[int]
    category_id: int


class BulkUpdateCategoryResponse(BaseModel):
    updated_count: int


class CloudProviderCallback(BaseModel):
    """云厂商直播状态回调模型"""
    app: str = Field(..., description="应用域名")
    appid: int = Field(..., description="应用ID")
    appname: str = Field(..., description="应用名")
    channel_id: str = Field(..., description="频道ID/流ID")
    errcode: int = Field(..., description="错误码，0表示成功")
    errmsg: str = Field(..., description="错误信息")
    event_time: int = Field(..., description="事件时间戳")
    event_type: int = Field(..., description="事件类型")
    height: int = Field(0, description="视频高度")
    idc_id: int = Field(..., description="机房ID")
    node: str = Field(..., description="节点IP")
    sequence: str = Field(..., description="序列号")
    set_id: int = Field(..., description="集群ID")
    sign: str = Field(..., description="签名")
    stream_id: str = Field(..., description="流ID")
    stream_param: str = Field(..., description="流参数")
    t: int = Field(..., description="时间戳")
    user_ip: str = Field(..., description="用户IP")
    width: int = Field(0, description="视频宽度")

    class Config:
        extra = "allow"


class CallbackResponse(BaseModel):
    """回调应答模型"""
    code: int = 0
