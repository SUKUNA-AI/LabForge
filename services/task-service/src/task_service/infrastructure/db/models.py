from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from datetime import datetime
from enum import Enum as PyEnum
from task_service.infrastructure.db.base import Base

class TaskStatus(str, PyEnum):
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    TESTING = "Testing"
    COMPLETED = "Completed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TO_DO, nullable=False)
    priority = Column(String(50))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)
