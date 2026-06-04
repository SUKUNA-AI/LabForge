from pathlib import Path
import sys


TASK_SERVICE_SRC = Path(__file__).resolve().parent / "services" / "task-service" / "src"
sys.path.insert(0, str(TASK_SERVICE_SRC))

from task_service.main import app  # noqa: E402
