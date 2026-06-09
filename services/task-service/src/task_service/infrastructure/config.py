import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    sql_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return Settings(
        database_url=database_url,
        sql_echo=_env_bool("SQL_ECHO", default=False),
    )
