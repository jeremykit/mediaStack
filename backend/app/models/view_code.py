"""ViewCode model for access control."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ViewCode(Base):
    """View code model for visitor access control."""

    __tablename__ = "view_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(12), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    categories = relationship(
        "Category",
        secondary="view_code_categories",
        back_populates="view_codes"
    )
