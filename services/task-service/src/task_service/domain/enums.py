from enum import StrEnum

class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    TESTING = "testing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskSourceType(StrEnum):
    MANUAL = "manual"
    AGENT_RUN = "agent_run"
    EXPERIMENT = "experiment"
    NOTE = "note"
    RESEARCH = "research"
    WEEKLY_REVIEW = "weekly_review"
    ARCHITECTURE_REVIEW = "architecture_review"