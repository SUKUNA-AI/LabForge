from dataclasses import dataclass
from uuid import UUID

from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
    priority: TaskPriority = TaskPriority.MEDIUM
    description: str | None = None
    project_uid: UUID | None = None
    source_type: TaskSourceType = TaskSourceType.MANUAL
    source_uid: UUID | None = None


@dataclass(frozen=True)
class PutTaskCommand:
    uid: UUID
    title: str
    priority: TaskPriority = TaskPriority.MEDIUM
    description: str | None = None
    project_uid: UUID | None = None
    source_type: TaskSourceType = TaskSourceType.MANUAL
    source_uid: UUID | None = None


@dataclass(frozen=True)
class GetTaskCommand:
    uid: UUID


@dataclass(frozen=True)
class ListTasksCommand:
    project_uid: UUID | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    source_type: TaskSourceType | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class UpdateTaskCommand:
    uid: UUID
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    project_uid: UUID | None = None
    source_type: TaskSourceType | None = None
    source_uid: UUID | None = None
    fields_set: frozenset[str] | None = None
