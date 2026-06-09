from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus


class ActionResponse(BaseModel):
    method: str
    href: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    project_uid: UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    source_type: TaskSourceType
    source_uid: UUID | None
    created_at: datetime
    updated_at: datetime
    links: dict[str, str]
    actions: dict[str, ActionResponse]


class TaskListMetaResponse(BaseModel):
    limit: int
    offset: int
    count: int


class PaginationLinksResponse(BaseModel):
    self: str
    next: str | None
    prev: str | None


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    meta: TaskListMetaResponse
    links: PaginationLinksResponse


class ApiErrorResponse(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str


class HealthLiveResponse(BaseModel):
    status: str


class HealthReadyResponse(BaseModel):
    status: str
    database: str


class TaskProfileResponse(BaseModel):
    fields: dict[str, Any]
    statuses: list[str]
    priorities: list[str]
    source_types: list[str]
    actions: dict[str, Any]
    links: dict[str, str]
