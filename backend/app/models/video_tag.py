"""VideoTag association table for many-to-many relationship."""
from sqlalchemy import Column, Integer, ForeignKey, Table

from app.database import Base


# Association table for Video-Tag many-to-many relationship
video_tags = Table(
    "video_tags",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("video_files.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)
