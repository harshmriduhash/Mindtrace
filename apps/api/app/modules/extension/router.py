"""Browser extension capture API (Bearer extension token)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import UnauthorizedError
from app.core.security import safe_decode_token
from app.db.session import get_db
from app.models import User
from app.modules.sources.service import extract_and_attach_concepts
from app.models import Source
from app.services.analytics import track
from app.services.ssrf import fetch_public_text
from app.core.errors import AppError

router = APIRouter(tags=["extension"])


class ExtensionTokenOut(BaseModel):
    token: str
    expires_in_days: int
    api_base_hint: str


class CaptureIn(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: str | None = None
    selected_text: str | None = Field(default=None, max_length=100_000)
    fetch_page: bool = False


class CaptureOut(BaseModel):
    source_id: UUID
    status: str
    concepts_ready: bool


def get_extension_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Extension Bearer token required")
    token = authorization.split(" ", 1)[1]
    payload = safe_decode_token(token)
    if not payload or payload.get("scope") != "extension" or "sub" not in payload:
        raise UnauthorizedError("Invalid extension token")
    user = db.get(User, UUID(payload["sub"]))
    if not user or user.status != "active":
        raise UnauthorizedError("Account unavailable")
    return user


@router.post("/auth/extension-token", response_model=ExtensionTokenOut)
def create_extension_token(user: User = Depends(get_current_user)) -> ExtensionTokenOut:
    settings = get_settings()
    from jose import jwt

    # Dedicated 90-day Bearer token (scope=extension); not the short-lived web session cookie.
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "scope": "extension",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=90)).timestamp()),
        },
        settings.session_secret,
        algorithm="HS256",
    )
    return ExtensionTokenOut(
        token=token,
        expires_in_days=90,
        api_base_hint=settings.api_origin.rstrip("/") + settings.api_prefix,
    )


@router.post("/extension/capture", response_model=CaptureOut)
def capture_from_extension(
    payload: CaptureIn,
    user: User = Depends(get_extension_user),
    db: Session = Depends(get_db),
) -> CaptureOut:
    settings = get_settings()
    text = (payload.selected_text or "").strip()
    if payload.fetch_page and payload.url and not text:
        try:
            text = fetch_public_text(payload.url)
        except AppError:
            text = f"Saved from {payload.url}. Add notes in Mindtrace if page text could not be fetched."
    if not text:
        text = f"Bookmark: {payload.title}" + (f"\n{payload.url}" if payload.url else "")
    if len(text) > settings.max_text_chars:
        text = text[: settings.max_text_chars]

    source = Source(
        user_id=user.id,
        type="url" if payload.url else "text",
        title=payload.title,
        source_uri=payload.url,
        status="processing",
        metadata_json={"via": "browser_extension"},
    )
    db.add(source)
    db.flush()
    extract_and_attach_concepts(db, source=source, text=text, user_id=user.id, create_job=False)
    track(db, user_id=user.id, event_name="extension_capture", properties={"source_id": str(source.id)})
    db.commit()
    db.refresh(source)
    return CaptureOut(source_id=source.id, status=source.status, concepts_ready=source.status == "ready_for_review")
