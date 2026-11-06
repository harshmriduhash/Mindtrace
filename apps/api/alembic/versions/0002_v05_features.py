"""v0.5 features: MFA, OAuth, projects, calendar, sandbox, adaptive review fields.

Revision ID: 0002_v05_features
Revises: 0001_initial_schema
Create Date: 2026-11-07
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0002_v05_features"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns(table)}
    return column in cols


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    if not _has_column(table, column.name):
        op.add_column(table, column)


def upgrade() -> None:
    from app.db.base import Base
    from app.models import entities  # noqa: F401

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    _add_column_if_missing("users", sa.Column("mfa_enabled", sa.Boolean(), server_default=sa.text("0"), nullable=False))
    _add_column_if_missing("users", sa.Column("mfa_secret", sa.String(length=64), nullable=True))
    _add_column_if_missing(
        "users", sa.Column("mfa_recovery_codes_json", sa.JSON(), server_default=sa.text("'[]'"), nullable=False)
    )
    _add_column_if_missing("users", sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True))
    _add_column_if_missing("users", sa.Column("is_admin", sa.Boolean(), server_default=sa.text("0"), nullable=False))

    _add_column_if_missing(
        "review_states", sa.Column("consecutive_fails", sa.Integer(), server_default="0", nullable=False)
    )
    _add_column_if_missing(
        "review_states",
        sa.Column("remediation_mode", sa.String(length=32), server_default="standard", nullable=False),
    )

    try:
        with op.batch_alter_table("users") as batch:
            batch.alter_column("password_hash", existing_type=sa.String(255), nullable=True)
    except Exception:
        pass


def downgrade() -> None:
    pass
