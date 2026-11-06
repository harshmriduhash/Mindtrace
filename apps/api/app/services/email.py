"""Transactional email adapter. Local mode logs verification links to stdout."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AuditEvent


def create_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def send_verification_email(*, email: str, token: str) -> str:
    settings = get_settings()
    link = f"{settings.app_origin}/verify-email?token={token}"
    subject = "Verify your Mindtrace email"
    body = f"Verify your Mindtrace account:\n\n{link}\n\nThis link expires in 24 hours."
    if settings.smtp_host and settings.smtp_user:
        try:
            import smtplib
            from email.message import EmailMessage

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = settings.email_from
            msg["To"] = email
            msg.set_content(body)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
            print(f"[mindtrace-email] sent verification to {email}")
        except Exception as exc:  # noqa: BLE001
            print(f"[mindtrace-email] SMTP failed ({exc}); link for {email}: {link}")
    else:
        print(f"[mindtrace-email] verification link for {email}: {link}")
    return link


def issue_email_verification(db: Session, *, user_id, email: str) -> str:
    token = create_verification_token()
    token_hash = hash_token(token)
    expires = datetime.now(UTC) + timedelta(hours=24)
    db.add(
        AuditEvent(
            actor_id=user_id,
            action="email_verification_issued",
            target_type="user",
            target_id=str(user_id),
            metadata_json={"token_hash": token_hash, "expires_at": expires.isoformat(), "email": email},
        )
    )
    link = send_verification_email(email=email, token=token)
    return link
