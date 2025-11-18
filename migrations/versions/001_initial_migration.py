"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-11-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("team_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("team_name"),
    )

    op.create_table(
        "users",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("team_name", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["team_name"], ["teams.team_name"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_team_name"), "users", ["team_name"], unique=False)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)

    op.create_table(
        "pull_requests",
        sa.Column("pull_request_id", sa.String(), nullable=False),
        sa.Column("pull_request_name", sa.String(), nullable=False),
        sa.Column("author_id", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "MERGED", name="prstatus"),
            nullable=False,
            server_default="OPEN",
        ),
        sa.Column(
            "assigned_reviewers",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("pull_request_id"),
    )
    op.create_index(
        op.f("ix_pull_requests_author_id"), "pull_requests", ["author_id"], unique=False
    )
    op.create_index(op.f("ix_pull_requests_status"), "pull_requests", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pull_requests_status"), table_name="pull_requests")
    op.drop_index(op.f("ix_pull_requests_author_id"), table_name="pull_requests")
    op.drop_table("pull_requests")
    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_index(op.f("ix_users_team_name"), table_name="users")
    op.drop_table("users")
    op.drop_table("teams")
    op.execute("DROP TYPE prstatus")
