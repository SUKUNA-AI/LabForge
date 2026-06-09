from collections.abc import Mapping
from urllib.parse import urlencode

from fastapi import Query

DEFAULT_LIMIT = 50
MAX_LIMIT = 100


def pagination_params(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
) -> tuple[int, int]:
    return limit, offset


def pagination_href(
    base_url: str,
    *,
    limit: int,
    offset: int,
    filters: Mapping[str, object | None] | None = None,
) -> str:
    params = {
        key: str(value)
        for key, value in (filters or {}).items()
        if value is not None
    }
    params["limit"] = str(limit)
    params["offset"] = str(offset)

    return f"{base_url}?{urlencode(params)}"

