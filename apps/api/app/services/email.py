"""Transactional email adapter — real SMTP when configured, else stdout."""

from __future__ import annotations

import hashlib
import secrets
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AuditEvent


def create_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def send_email(*, to: str, subject: str, body: str) -> bool:
    """Send via SMTP when configured. Returns True if SMTP accepted the message."""
    settings = get_settings()
    if not settings.smtp_host:
        print(f"[mindtrace-email] (no SMTP) to={to} subject={subject}\n{body}")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = to
    msg.set_content(body)

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                smtp.ehlo()
                try:
                    smtp.starttls()
                    smtp.ehlo()
                except smtplib.SMTPException:
                    pass
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
        print(f"[mindtrace-email] sent to {to}: {subject}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[mindtrace-email] SMTP failed ({exc}); falling back to log for {to}\n{body}")
        return False


def send_verification_email(*, email: str, token: str) -> str:
    settings = get_settings()
    link = f"{settings.app_origin}/verify-email?token={token}"
    subject = "Verify your Mindtrace email"
    body = f"Verify your Mindtrace account:\n\n{link}\n\nThis link expires in 24 hours."
    send_email(to=email, subject=subject, body=body)
    return link


def send_mfa_enabled_email(*, email: str) -> None:
    send_email(
        to=email,
        subject="Mindtrace MFA enabled",
        body="Two-factor authentication was enabled on your Mindtrace account. If you did not do this, reset your password and contact support.",
    )


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
    return send_verification_email(email=email, token=token)
