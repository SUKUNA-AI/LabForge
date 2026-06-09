from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from task_service.infrastructure.config import get_settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=settings.sql_echo)


@lru_cache
def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        get_async_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def dispose_async_engine() -> None:
    await get_async_engine().dispose()
    get_async_engine.cache_clear()
    get_async_session_maker.cache_clear()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session_maker()() as session:
        yield session
