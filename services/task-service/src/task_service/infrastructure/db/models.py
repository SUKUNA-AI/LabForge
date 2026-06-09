from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from task_service.infrastructure.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    
    uid: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True, index=True, nullable=False, default=uuid.uuid4)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="todo")
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    source_uid: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True),index=True, nullable=True)
    project_uid: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
