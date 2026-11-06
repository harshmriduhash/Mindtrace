#!/usr/bin/env python3
"""Create all tables from SQLAlchemy metadata (local/dev convenience). Prefer Alembic in staging/prod."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401


def _ensure_columns() -> None:
    """Add v0.5 columns on existing SQLite DBs (create_all does not alter)."""
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    with engine.begin() as conn:
        if "users" in tables:
            cols = {c["name"] for c in insp.get_columns("users")}
            alters = []
            if "mfa_enabled" not in cols:
                alters.append("ALTER TABLE users ADD COLUMN mfa_enabled BOOLEAN DEFAULT 0 NOT NULL")
            if "mfa_secret" not in cols:
                alters.append("ALTER TABLE users ADD COLUMN mfa_secret VARCHAR(64)")
            if "mfa_recovery_codes_json" not in cols:
                alters.append("ALTER TABLE users ADD COLUMN mfa_recovery_codes_json JSON DEFAULT '[]' NOT NULL")
            if "deletion_requested_at" not in cols:
                alters.append("ALTER TABLE users ADD COLUMN deletion_requested_at DATETIME")
            if "is_admin" not in cols:
                alters.append("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            for stmt in alters:
                conn.execute(text(stmt))
        if "review_states" in tables:
            cols = {c["name"] for c in insp.get_columns("review_states")}
            if "consecutive_fails" not in cols:
                conn.execute(text("ALTER TABLE review_states ADD COLUMN consecutive_fails INTEGER DEFAULT 0 NOT NULL"))
            if "remediation_mode" not in cols:
                conn.execute(
                    text("ALTER TABLE review_states ADD COLUMN remediation_mode VARCHAR(32) DEFAULT 'standard' NOT NULL")
                )


def main() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_columns()
    print("Database tables created.")


if __name__ == "__main__":
    main()
