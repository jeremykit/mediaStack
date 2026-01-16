"""ViewCodeCategory association table for many-to-many relationship."""
from sqlalchemy import Column, Integer, ForeignKey, Table

from app.database import Base


# Association table for ViewCode-Category many-to-many relationship
view_code_categories = Table(
    "view_code_categories",
    Base.metadata,
    Column("code_id", Integer, ForeignKey("view_codes.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
)
