from abc import ABC, abstractmethod
from uuid import UUID
from typing import Sequence
from task_service.domain.enums import TaskPriority, TaskSourceType, TaskStatus

from task_service.domain.task import Task

class AbstractTaskRepository(ABC):

    @abstractmethod
    async def add(self, task: Task) -> None:
        pass

    @abstractmethod
    async def get_by_uid(self, uid: UUID) -> Task | None:
        pass

    @abstractmethod
    async def list(self,
                   project_uid: UUID | None = None,
                   status: TaskStatus | None = None,
                   priority: TaskPriority | None = None,
                   source_type: TaskSourceType | None = None,
                   limit: int = 50, offset: int = 0) -> Sequence[Task]:
        pass

    @abstractmethod
    async def count(self,
                    project_uid: UUID | None = None,
                    status: TaskStatus | None = None,
                    priority: TaskPriority | None = None,
                    source_type: TaskSourceType | None = None) -> int:
        pass
    
    @abstractmethod
    async def update(self, task: Task) -> Task | None:
        pass

    @abstractmethod
    async def delete(self, uid: UUID) -> bool:
        pass
