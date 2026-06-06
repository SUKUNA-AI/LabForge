"""add task public uid and source fields

Revision ID: 8b9f2c4d1a6e
Revises: f21ca283e9cb
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "8b9f2c4d1a6e"
down_revision: Union[str, Sequence[str], None] = "f21ca283e9cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.add_column(
        "tasks",
        sa.Column("uid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute("UPDATE tasks SET uid = gen_random_uuid() WHERE uid IS NULL")
    op.alter_column(
        "tasks",
        "uid",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.create_index(op.f("ix_tasks_uid"), "tasks", ["uid"], unique=True)

    op.add_column(
        "tasks",
        sa.Column("project_uid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        op.f("ix_tasks_project_uid"),
        "tasks",
        ["project_uid"],
        unique=False,
    )

    op.add_column(
        "tasks",
        sa.Column("source_type", sa.String(length=50), nullable=True),
    )
    op.execute("UPDATE tasks SET source_type = 'manual' WHERE source_type IS NULL")
    op.alter_column(
        "tasks",
        "source_type",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.add_column(
        "tasks",
        sa.Column("source_uid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        op.f("ix_tasks_source_uid"),
        "tasks",
        ["source_uid"],
        unique=False,
    )

    op.execute(
        """
        UPDATE tasks
        SET priority = CASE
            WHEN priority IS NULL OR btrim(priority) = '' THEN 'medium'
            WHEN lower(btrim(priority)) = 'low' THEN 'low'
            WHEN lower(btrim(priority)) = 'medium' THEN 'medium'
            WHEN lower(btrim(priority)) = 'high' THEN 'high'
            WHEN lower(btrim(priority)) = 'critical' THEN 'critical'
            ELSE 'medium'
        END
        """
    )
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.add_column(
        "tasks",
        sa.Column("status_new", sa.String(length=50), nullable=True),
    )
    op.execute(
        """
        UPDATE tasks
        SET status_new = CASE
            WHEN status::text = 'TO_DO' THEN 'todo'
            WHEN status::text = 'IN_PROGRESS' THEN 'in_progress'
            WHEN status::text = 'IN_REVIEW' THEN 'in_review'
            WHEN status::text = 'TESTING' THEN 'testing'
            WHEN status::text = 'COMPLETED' THEN 'completed'
            WHEN status::text = 'To Do' THEN 'todo'
            WHEN status::text = 'In Progress' THEN 'in_progress'
            WHEN status::text = 'In Review' THEN 'in_review'
            WHEN status::text = 'Testing' THEN 'testing'
            WHEN status::text = 'Completed' THEN 'completed'
            ELSE 'todo'
        END
        """
    )
    op.alter_column(
        "tasks",
        "status_new",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.drop_column("tasks", "status")
    op.alter_column(
        "tasks",
        "status_new",
        new_column_name="status",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.execute("DROP TYPE IF EXISTS taskstatus")

    op.execute("UPDATE tasks SET updated_at = created_at WHERE updated_at IS NULL")
    op.alter_column(
        "tasks",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    task_status = postgresql.ENUM(
        "TO_DO",
        "IN_PROGRESS",
        "IN_REVIEW",
        "TESTING",
        "COMPLETED",
        name="taskstatus",
    )
    task_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "tasks",
        sa.Column("status_old", task_status, nullable=True),
    )
    op.execute(
        """
        UPDATE tasks
        SET status_old = (
            CASE
                WHEN status = 'todo' THEN 'TO_DO'
                WHEN status = 'in_progress' THEN 'IN_PROGRESS'
                WHEN status = 'in_review' THEN 'IN_REVIEW'
                WHEN status = 'testing' THEN 'TESTING'
                WHEN status = 'completed' THEN 'COMPLETED'
                WHEN status = 'cancelled' THEN 'COMPLETED'
                ELSE 'TO_DO'
            END
        )::taskstatus
        """
    )
    op.alter_column(
        "tasks",
        "status_old",
        existing_type=task_status,
        nullable=False,
    )
    op.drop_column("tasks", "status")
    op.alter_column(
        "tasks",
        "status_old",
        new_column_name="status",
        existing_type=task_status,
        nullable=False,
    )

    op.alter_column(
        "tasks",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        nullable=True,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.String(length=50),
        nullable=True,
    )

    op.drop_index(op.f("ix_tasks_source_uid"), table_name="tasks")
    op.drop_column("tasks", "source_uid")
    op.drop_column("tasks", "source_type")
    op.drop_index(op.f("ix_tasks_project_uid"), table_name="tasks")
    op.drop_column("tasks", "project_uid")
    op.drop_index(op.f("ix_tasks_uid"), table_name="tasks")
    op.drop_column("tasks", "uid")
