from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus
from task_service.domain.errors import (
    InvalidTaskPriority,
    InvalidTaskSourceType,
    InvalidTaskStatus,
    InvalidTaskTitle,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Task:
    title: str
    priority: TaskPriority
    id: int | None = None
    uid: UUID = field(default_factory=uuid4)
    project_uid: UUID | None = None
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    source_type: TaskSourceType = TaskSourceType.MANUAL
    source_uid: UUID | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self._validate_title(self.title)
        self._validate_status(self.status)
        self._validate_priority(self.priority)
        self._validate_source_type(self.source_type)

    def change_title(self, title: str) -> None:
        self._validate_title(title)
        self.title = title.strip()
        self._touch()

    def change_description(self, description: str | None) -> None:
        self.description = description
        self._touch()

    def change_status(self, status: TaskStatus) -> None:
        self._validate_status(status)
        self.status = status
        self._touch()

    def change_priority(self, priority: TaskPriority) -> None:
        self._validate_priority(priority)
        self.priority = priority
        self._touch()

    def change_project_uid(self, project_uid: UUID | None) -> None:
        self.project_uid = project_uid
        self._touch()

    def change_source_type(self, source_type: TaskSourceType) -> None:
        self._validate_source_type(source_type)
        self.source_type = source_type
        self._touch()

    def change_source_uid(self, source_uid: UUID | None) -> None:
        self.source_uid = source_uid
        self._touch()

    def complete(self) -> None:
        self.change_status(TaskStatus.COMPLETED)

    def cancel(self) -> None:
        self.change_status(TaskStatus.CANCELLED)

    def _touch(self) -> None:
        self.updated_at = utc_now()

    @staticmethod
    def _validate_title(title: str) -> None:
        if not title or not title.strip():
            raise InvalidTaskTitle("Task title must not be empty")
        if len(title.strip()) < 3:
            raise InvalidTaskTitle("Task title must be at least 3 characters")

    @staticmethod
    def _validate_status(status: TaskStatus) -> None:
        if not isinstance(status, TaskStatus):
            raise InvalidTaskStatus("Task status must be a TaskStatus")

    @staticmethod
    def _validate_priority(priority: TaskPriority) -> None:
        if not isinstance(priority, TaskPriority):
            raise InvalidTaskPriority("Task priority must be a TaskPriority")

    @staticmethod
    def _validate_source_type(source_type: TaskSourceType) -> None:
        if not isinstance(source_type, TaskSourceType):
            raise InvalidTaskSourceType("Task source type must be a TaskSourceType")
