"""ViewCode schemas for request/response models."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class ViewCodeCreate(BaseModel):
    """Schema for creating a view code."""
    code: str = Field(min_length=6, max_length=12)
    is_active: bool = True
    expires_at: Optional[datetime] = None
    category_ids: List[int] = []

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('Code must contain only letters and numbers')
        return v


class ViewCodeUpdate(BaseModel):
    """Schema for updating a view code."""
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    category_ids: Optional[List[int]] = None


class ViewCodeResponse(BaseModel):
    """Schema for view code response."""
    id: int
    code: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    category_ids: List[int] = []
    category_names: List[str] = []

    class Config:
        from_attributes = True


class ViewCodeVerifyRequest(BaseModel):
    """Schema for verifying a view code."""
    code: str


class ViewCodeVerifyResponse(BaseModel):
    """Schema for view code verification response."""
    valid: bool
    category_ids: List[int] = []
    expires_at: Optional[datetime] = None
