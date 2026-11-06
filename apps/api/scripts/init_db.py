#!/usr/bin/env python3
"""Create all tables from SQLAlchemy metadata (local/dev convenience). Prefer Alembic in staging/prod."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__ == "__main__":
    main()
