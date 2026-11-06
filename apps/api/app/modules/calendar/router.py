"""Study calendar — ICS feed of due reviews + optional Google Calendar deep link."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models import CalendarConnection, PracticeItem, ReviewState, User

router = APIRouter(prefix="/calendar", tags=["calendar"])


class CalendarOut(BaseModel):
    feed_token: str
    ics_url: str
    google_url: str
    provider: str
    status: str


def _ensure_connection(db: Session, user: User) -> CalendarConnection:
    row = db.scalar(select(CalendarConnection).where(CalendarConnection.user_id == user.id))
    if row:
        return row
    row = CalendarConnection(
        user_id=user.id,
        provider="ics",
        feed_token=secrets.token_urlsafe(24),
        status="active",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/connection", response_model=CalendarOut)
def get_connection(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CalendarOut:
    settings = get_settings()
    row = _ensure_connection(db, user)
    ics_url = f"{settings.api_origin}{settings.api_prefix}/calendar/ics/{row.feed_token}"
    # Google Calendar "add by URL" deep link
    google_url = f"https://calendar.google.com/calendar/r?cid={ics_url}"
    return CalendarOut(
        feed_token=row.feed_token,
        ics_url=ics_url,
        google_url=google_url,
        provider=row.provider,
        status=row.status,
    )


@router.post("/connection/rotate", response_model=CalendarOut)
def rotate_feed(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CalendarOut:
    row = _ensure_connection(db, user)
    row.feed_token = secrets.token_urlsafe(24)
    db.commit()
    return get_connection(user=user, db=db)


def _ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


@router.get("/ics/{feed_token}")
def ics_feed(feed_token: str, db: Session = Depends(get_db)) -> Response:
    row = db.scalar(select(CalendarConnection).where(CalendarConnection.feed_token == feed_token))
    if not row or row.status != "active":
        raise NotFoundError("Calendar feed not found")

    now = datetime.now(UTC)
    horizon = now + timedelta(days=30)
    states = db.scalars(
        select(ReviewState)
        .where(ReviewState.user_id == row.user_id, ReviewState.due_at <= horizon)
        .order_by(ReviewState.due_at)
        .limit(100)
    ).all()

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mindtrace//Study Schedule//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Mindtrace Reviews",
    ]
    for state in states:
        item = db.get(PracticeItem, state.practice_item_id)
        title = (item.prompt[:80] if item else "Mindtrace review").replace("\n", " ")
        start = state.due_at.astimezone(UTC)
        end = start + timedelta(minutes=item.expected_minutes if item else 15)
        uid = f"{state.id}@mindtrace"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{_ics_escape('Mindtrace: ' + title)}",
                f"DESCRIPTION:{_ics_escape('Due review practice in Mindtrace')}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    body = "\r\n".join(lines) + "\r\n"
    return Response(content=body, media_type="text/calendar; charset=utf-8")


@router.get("/upcoming")
def upcoming(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    now = datetime.now(UTC)
    states = db.scalars(
        select(ReviewState)
        .where(ReviewState.user_id == user.id, ReviewState.due_at >= now - timedelta(days=1))
        .order_by(ReviewState.due_at)
        .limit(20)
    ).all()
    out = []
    for state in states:
        item = db.get(PracticeItem, state.practice_item_id)
        out.append(
            {
                "due_at": state.due_at.isoformat(),
                "practice_item_id": str(state.practice_item_id),
                "title": item.prompt[:120] if item else "Review",
                "remediation_mode": state.remediation_mode,
                "type": item.type if item else None,
            }
        )
    return out
