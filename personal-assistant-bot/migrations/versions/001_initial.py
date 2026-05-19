"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("emoji", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("business_id", sa.Integer, sa.ForeignKey("businesses.id")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("due_date", sa.Date),
        sa.Column("due_time", sa.Time),
        sa.Column("priority", sa.Text, server_default="normal"),
        sa.Column("status", sa.Text, server_default="pending"),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("done_at", sa.TIMESTAMP),
    )

    op.create_table(
        "routines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("business_id", sa.Integer, sa.ForeignKey("businesses.id")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("frequency", sa.Text, nullable=False),
        sa.Column("weekdays", sa.Text),
        sa.Column("remind_time", sa.Time),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("last_done", sa.Date),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("business_id", sa.Integer, sa.ForeignKey("businesses.id")),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tags", ARRAY(sa.Text)),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("session_date", sa.Date, server_default=sa.func.current_date()),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("ai_messages")
    op.drop_table("notes")
    op.drop_table("routines")
    op.drop_table("tasks")
    op.drop_table("businesses")
