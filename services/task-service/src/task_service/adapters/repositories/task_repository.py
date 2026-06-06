from abc import ABC, abstractmethod
from uuid import UUID
from typing import Sequence

from task_service.domain.task import Task

class AbstractTaskRepository(ABC):

    @abstractmethod
    async def add(self, task: Task) -> None:
        #Добавить новую задачу в хранилище
        pass

    @abstractmethod
    async def get_by_uid(self, uid: UUID) -> Task | None:
        #Получить задачу по её UUID. Вернуть None, если не найдена
        pass

    @abstractmethod
    async def list(self) -> Sequence[Task]:
        #Получить список всех задач
        pass
    
    @abstractmethod
    async def update(self, task: Task) -> None:
        #обновить задачу
        pass

    @abstractmethod
    async def delete(self, uid: UUID) -> None:
        #удалить задачу
        pass