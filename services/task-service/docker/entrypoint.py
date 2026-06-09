import os
import subprocess
import sys


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def main() -> None:
    if _env_bool("RUN_MIGRATIONS_ON_STARTUP", default=True):
        subprocess.run(["alembic", "upgrade", "head"], check=True)

    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    main()
