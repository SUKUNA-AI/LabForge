from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from task_service.domain.enums import TaskStatus, TaskPriority, TaskSourceType


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Task title")
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uid: UUID
    title: str
    description: str | None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    source_type: TaskSourceType
    source_uid: UUID | None
    project_uid: UUID | None
    created_at: datetime
    updated_at: datetime
