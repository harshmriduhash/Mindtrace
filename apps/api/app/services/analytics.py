"""Product analytics — no raw prompts/answers in events."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AnalyticsEvent


def track(
    db: Session,
    *,
    event_name: str,
    user_id: UUID | None = None,
    session_id: str | None = None,
    properties: dict[str, Any] | None = None,
) -> AnalyticsEvent:
    event = AnalyticsEvent(
        user_id=user_id,
        session_id=session_id,
        event_name=event_name,
        properties_json=properties or {},
    )
    db.add(event)
    return event
