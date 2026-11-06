"""TOTP MFA setup and verification."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models import AuditEvent, User
from app.schemas.common import MessageOut
from app.services.email import send_mfa_enabled_email
from app.services.mfa import (
    generate_recovery_codes,
    generate_totp_secret,
    hash_recovery_code,
    provisioning_uri,
    verify_totp,
)

router = APIRouter(prefix="/auth/mfa", tags=["mfa"])


class MfaSetupOut(BaseModel):
    secret: str
    otpauth_url: str
    recovery_codes: list[str]


class MfaConfirmIn(BaseModel):
    code: str = Field(min_length=6, max_length=12)


class MfaDisableIn(BaseModel):
    code: str = Field(min_length=6, max_length=64)


@router.post("/setup", response_model=MfaSetupOut)
def setup_mfa(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MfaSetupOut:
    if user.mfa_enabled:
        raise AppError("mfa_already_enabled", "MFA is already enabled", 400)
    secret = generate_totp_secret()
    codes = generate_recovery_codes()
    user.mfa_secret = secret
    user.mfa_recovery_codes_json = [hash_recovery_code(c) for c in codes]
    user.mfa_enabled = False  # pending confirm
    db.commit()
    return MfaSetupOut(secret=secret, otpauth_url=provisioning_uri(secret=secret, email=user.email), recovery_codes=codes)


@router.post("/confirm", response_model=MessageOut)
def confirm_mfa(
    payload: MfaConfirmIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MessageOut:
    if not user.mfa_secret:
        raise AppError("mfa_not_started", "Call /auth/mfa/setup first", 400)
    if not verify_totp(user.mfa_secret, payload.code):
        raise AppError("invalid_mfa_code", "Invalid authenticator code", 400)
    user.mfa_enabled = True
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="mfa_enabled",
            target_type="user",
            target_id=str(user.id),
            metadata_json={},
        )
    )
    db.commit()
    send_mfa_enabled_email(email=user.email)
    return MessageOut(message="MFA enabled")


@router.post("/disable", response_model=MessageOut)
def disable_mfa(
    payload: MfaDisableIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MessageOut:
    if not user.mfa_enabled or not user.mfa_secret:
        raise AppError("mfa_not_enabled", "MFA is not enabled", 400)
    ok = verify_totp(user.mfa_secret, payload.code)
    if not ok:
        hashed = hash_recovery_code(payload.code)
        codes = list(user.mfa_recovery_codes_json or [])
        if hashed in codes:
            codes.remove(hashed)
            user.mfa_recovery_codes_json = codes
            ok = True
    if not ok:
        raise AppError("invalid_mfa_code", "Invalid code or recovery code", 400)
    user.mfa_enabled = False
    user.mfa_secret = None
    user.mfa_recovery_codes_json = []
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="mfa_disabled",
            target_type="user",
            target_id=str(user.id),
            metadata_json={},
        )
    )
    db.commit()
    return MessageOut(message="MFA disabled")


@router.get("/status")
def mfa_status(user: User = Depends(get_current_user)) -> dict:
    return {"enabled": bool(user.mfa_enabled), "pending_setup": bool(user.mfa_secret and not user.mfa_enabled)}
