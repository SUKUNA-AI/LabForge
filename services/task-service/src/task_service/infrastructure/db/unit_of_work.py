from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from task_service.adapters.repositories.task_repository import AbstractTaskRepository
from task_service.adapters.repositories.sqlalchemy_task_repository import SqlAlchemyTaskRepository
from task_service.infrastructure.db.session import get_async_session_maker


class AbstractUnitOfWork(ABC):
    tasks: AbstractTaskRepository

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.rollback()


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self._session_factory = get_async_session_maker()

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.tasks = SqlAlchemyTaskRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
