from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func, text

from app.db.session import Base


class GoalTemplate(Base):
    __tablename__ = "goal_templates"
    __table_args__ = (PrimaryKeyConstraint("slug", "version"),)

    slug = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    defaults = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False, server_default=text("1"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
