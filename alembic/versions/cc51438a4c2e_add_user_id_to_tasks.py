"""Add user_id to tasks

Revision ID: cc51438a4c2e
Revises: fe43401b93f9
Create Date: 2026-08-27 10:22:36.707594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc51438a4c2e'
down_revision: Union[str, Sequence[str], None] = 'fe43401b93f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add user_id temporarily as nullable
    op.add_column(
        "tasks",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # 2. Assign existing tasks to user ID 1
    op.execute(
        "UPDATE tasks SET user_id = 1 WHERE user_id IS NULL"
    )

    # 3. Make user_id required
    op.alter_column(
        "tasks",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 4. Create index
    op.create_index(
        op.f("ix_tasks_user_id"),
        "tasks",
        ["user_id"],
        unique=False,
    )

    # 5. Create foreign key
    op.create_foreign_key(
        "fk_tasks_user_id_users",
        "tasks",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_tasks_user_id_users",
        "tasks",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_tasks_user_id"),
        table_name="tasks",
    )

    op.drop_column("tasks", "user_id")