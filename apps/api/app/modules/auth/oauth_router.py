"""Google + GitHub OAuth (authorization-code). Disabled when client ids empty."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import AuditEvent, OAuthAccount, Profile, Subscription, User

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])

_oauth_states: dict[str, dict[str, Any]] = {}


def _redirect_base() -> str:
    settings = get_settings()
    return (settings.oauth_redirect_base or settings.api_origin).rstrip("/")


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _upsert_oauth_user(
    db: Session,
    *,
    provider: str,
    subject: str,
    email: str,
    display_name: str | None,
    access_token: str | None = None,
) -> User:
    existing = db.scalar(
        select(OAuthAccount).where(OAuthAccount.provider == provider, OAuthAccount.provider_subject == subject)
    )
    if existing:
        user = db.get(User, existing.user_id)
        if not user:
            raise AppError("oauth_user_missing", "Linked user missing", 500)
        if access_token:
            existing.access_token_enc = access_token
        return user

    email_l = email.lower()
    user = db.scalar(select(User).where(User.email == email_l))
    if not user:
        user = User(
            email=email_l,
            password_hash=None,
            email_verified_at=datetime.now(UTC),
            status="active",
            plan="free",
            mfa_recovery_codes_json=[],
        )
        db.add(user)
        db.flush()
        db.add(
            Profile(
                user_id=user.id,
                display_name=display_name or email_l.split("@")[0],
                timezone="UTC",
                preferences_json={},
            )
        )
        db.add(Subscription(user_id=user.id, status="none", plan_id="free"))
    else:
        if not user.email_verified_at:
            user.email_verified_at = datetime.now(UTC)

    db.add(
        OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_subject=subject,
            email=email_l,
            access_token_enc=access_token,
        )
    )
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="oauth_login",
            target_type="user",
            target_id=str(user.id),
            metadata_json={"provider": provider},
        )
    )
    return user


@router.get("/providers")
def providers() -> dict[str, Any]:
    settings = get_settings()
    return {
        "google": bool(settings.google_oauth_client_id and settings.google_oauth_client_secret),
        "github": bool(settings.github_oauth_client_id and settings.github_oauth_client_secret),
    }


@router.get("/{provider}/start")
def oauth_start(provider: str) -> RedirectResponse:
    settings = get_settings()
    state = secrets.token_urlsafe(24)
    _oauth_states[state] = {"provider": provider}
    redirect_uri = f"{_redirect_base()}{settings.api_prefix}/auth/oauth/{provider}/callback"

    if provider == "google":
        if not settings.google_oauth_client_id:
            raise AppError("oauth_unconfigured", "Google OAuth is not configured", 503)
        params = urlencode(
            {
                "client_id": settings.google_oauth_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "online",
                "prompt": "select_account",
            }
        )
        return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

    if provider == "github":
        if not settings.github_oauth_client_id:
            raise AppError("oauth_unconfigured", "GitHub OAuth is not configured", 503)
        params = urlencode(
            {
                "client_id": settings.github_oauth_client_id,
                "redirect_uri": redirect_uri,
                "scope": "read:user user:email",
                "state": state,
            }
        )
        return RedirectResponse(f"https://github.com/login/oauth/authorize?{params}")

    raise AppError("unknown_provider", "Unsupported OAuth provider", 400)


@router.get("/{provider}/callback")
def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    code: str | None = None,
    state: str | None = None,
) -> RedirectResponse:
    settings = get_settings()
    if not code or not state or state not in _oauth_states:
        raise AppError("invalid_oauth_state", "Invalid OAuth state", 400)
    del _oauth_states[state]
    redirect_uri = f"{_redirect_base()}{settings.api_prefix}/auth/oauth/{provider}/callback"

    if provider == "google":
        with httpx.Client(timeout=20.0) as client:
            token_resp = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_oauth_client_id,
                    "client_secret": settings.google_oauth_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code >= 400:
                raise AppError("oauth_token_failed", "Google token exchange failed", 502)
            tokens = token_resp.json()
            info = client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            if info.status_code >= 400:
                raise AppError("oauth_profile_failed", "Google profile fetch failed", 502)
            profile = info.json()
        subject = str(profile.get("sub"))
        email = profile.get("email")
        if not email:
            raise AppError("oauth_email_required", "Email permission is required", 400)
        user = _upsert_oauth_user(
            db,
            provider="google",
            subject=subject,
            email=email,
            display_name=profile.get("name"),
            access_token=tokens.get("access_token"),
        )
    elif provider == "github":
        with httpx.Client(timeout=20.0, headers={"Accept": "application/json"}) as client:
            token_resp = client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.github_oauth_client_id,
                    "client_secret": settings.github_oauth_client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            tokens = token_resp.json()
            access = tokens.get("access_token")
            if not access:
                raise AppError("oauth_token_failed", "GitHub token exchange failed", 502)
            headers = {"Authorization": f"Bearer {access}", "Accept": "application/vnd.github+json"}
            info = client.get("https://api.github.com/user", headers=headers)
            profile = info.json()
            emails_resp = client.get("https://api.github.com/user/emails", headers=headers)
            emails = emails_resp.json() if emails_resp.status_code < 400 else []
        primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
        email = (primary or {}).get("email") or profile.get("email")
        if not email:
            raise AppError("oauth_email_required", "A verified GitHub email is required", 400)
        user = _upsert_oauth_user(
            db,
            provider="github",
            subject=str(profile.get("id")),
            email=email,
            display_name=profile.get("name") or profile.get("login"),
            access_token=access,
        )
    else:
        raise AppError("unknown_provider", "Unsupported OAuth provider", 400)

    db.commit()
    token = create_access_token(user_id=user.id, email=user.email)
    response = RedirectResponse(url=f"{settings.app_origin}/app/today")
    _set_session_cookie(response, token)
    return response
