from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class TaskCreateRequest(RequestModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    project_uid: UUID | None = None
    source_type: TaskSourceType = TaskSourceType.MANUAL
    source_uid: UUID | None = None


class TaskPutRequest(RequestModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    project_uid: UUID | None = None
    source_type: TaskSourceType = TaskSourceType.MANUAL
    source_uid: UUID | None = None


class TaskUpdateRequest(RequestModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    project_uid: UUID | None = None
    source_type: TaskSourceType | None = None
    source_uid: UUID | None = None
