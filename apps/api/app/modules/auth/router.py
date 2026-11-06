from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import AppError, ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import AuditEvent, Profile, Subscription, User
from app.schemas.common import LoginIn, MeOut, MessageOut, ProfileOut, SignupIn, UserOut
from app.services.email import hash_token, issue_email_verification
from app.services.rate_limit import check_rate_limit, client_ip

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupOut(MeOut):
    verification_link: str | None = None


class VerifyEmailIn(BaseModel):
    token: str = Field(min_length=10)


class ResendVerificationIn(BaseModel):
    email: EmailStr


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


@router.post("/signup", response_model=SignupOut)
def signup(payload: SignupIn, request: Request, response: Response, db: Session = Depends(get_db)) -> SignupOut:
    check_rate_limit(f"signup:{client_ip(request)}", limit=5, window_seconds=900)

    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise ConflictError("An account with this email already exists")

    settings = get_settings()
    # In local/dev, auto-verify so first-run UX is smooth; still issue a token for testing.
    auto_verify = settings.environment in {"local", "development", "test"}

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        email_verified_at=datetime.now(UTC) if auto_verify else None,
        status="active",
        plan="free",
        mfa_recovery_codes_json=[],
    )
    db.add(user)
    db.flush()
    profile = Profile(
        user_id=user.id,
        display_name=payload.display_name or payload.email.split("@")[0],
        timezone="UTC",
        preferences_json={},
    )
    db.add(profile)
    db.add(Subscription(user_id=user.id, status="none", plan_id="free"))
    link = issue_email_verification(db, user_id=user.id, email=user.email)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="signup",
            target_type="user",
            target_id=str(user.id),
            metadata_json={},
        )
    )
    db.commit()
    db.refresh(user)
    db.refresh(profile)

    token = create_access_token(user_id=user.id, email=user.email)
    _set_session_cookie(response, token)
    me = _me_payload(user, profile)
    return SignupOut(**me.model_dump(), verification_link=link if auto_verify else None)


class LoginWithMfaIn(LoginIn):
    mfa_code: str | None = Field(default=None, max_length=64)


@router.post("/login", response_model=MeOut)
def login(payload: LoginWithMfaIn, request: Request, response: Response, db: Session = Depends(get_db)) -> MeOut:
    check_rate_limit(f"login:{client_ip(request)}:{payload.email.lower()}", limit=5, window_seconds=900)

    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    if user.status not in {"active"}:
        raise UnauthorizedError("Account unavailable")

    if user.mfa_enabled and user.mfa_secret:
        from app.services.mfa import hash_recovery_code, verify_totp

        code = (payload.mfa_code or "").strip()
        if not code:
            raise AppError("mfa_required", "MFA code required", 401)
        ok = verify_totp(user.mfa_secret, code)
        if not ok:
            hashed = hash_recovery_code(code)
            codes = list(user.mfa_recovery_codes_json or [])
            if hashed in codes:
                codes.remove(hashed)
                user.mfa_recovery_codes_json = codes
                ok = True
        if not ok:
            raise UnauthorizedError("Invalid MFA code")

    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    token = create_access_token(user_id=user.id, email=user.email)
    _set_session_cookie(response, token)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="login",
            target_type="user",
            target_id=str(user.id),
            metadata_json={"mfa": bool(user.mfa_enabled)},
        )
    )
    db.commit()
    return _me_payload(user, profile)


@router.post("/logout", response_model=MessageOut)
def logout(response: Response) -> MessageOut:
    settings = get_settings()
    response.delete_cookie(settings.cookie_name, path="/")
    return MessageOut(message="Logged out")


@router.post("/verify-email", response_model=MessageOut)
def verify_email(payload: VerifyEmailIn, db: Session = Depends(get_db)) -> MessageOut:
    token_hash = hash_token(payload.token)
    # Scan recent verification events for matching hash (MVP; replace with dedicated table later).
    events = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.action == "email_verification_issued")
        .order_by(AuditEvent.occurred_at.desc())
        .limit(200)
    ).all()
    match = next((e for e in events if (e.metadata_json or {}).get("token_hash") == token_hash), None)
    if not match or not match.target_id:
        raise AppError("invalid_token", "Invalid or expired verification token", 400)

    expires_at = (match.metadata_json or {}).get("expires_at")
    if expires_at and datetime.fromisoformat(expires_at) < datetime.now(UTC):
        raise AppError("token_expired", "Verification token expired", 400)

    try:
        user = db.get(User, UUID(str(match.target_id)))
    except (ValueError, TypeError):
        user = None
    if not user:
        raise AppError("invalid_token", "Invalid verification token", 400)
    user.email_verified_at = datetime.now(UTC)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="email_verified",
            target_type="user",
            target_id=str(user.id),
            metadata_json={},
        )
    )
    db.commit()
    return MessageOut(message="Email verified")


@router.post("/resend-verification", response_model=MessageOut)
def resend_verification(
    payload: ResendVerificationIn, request: Request, db: Session = Depends(get_db)
) -> MessageOut:
    check_rate_limit(f"resend:{client_ip(request)}", limit=3, window_seconds=900)
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    # Always return success to avoid account enumeration.
    if user and not user.email_verified_at:
        issue_email_verification(db, user_id=user.id, email=user.email)
        db.commit()
    return MessageOut(message="If that account exists, a verification email was sent")


def _me_payload(user: User, profile: Profile | None) -> MeOut:
    settings = get_settings()
    return MeOut(
        user=UserOut.model_validate(user),
        profile=ProfileOut.model_validate(profile) if profile else None,
        entitlements={
            "plan": user.plan,
            "active_skill_paths": settings.free_active_skill_paths if user.plan == "free" else 5,
            "ai_evaluations_per_day": settings.free_ai_evaluations_per_day if user.plan == "free" else 200,
            "source_imports_per_hour": settings.free_source_imports_per_hour if user.plan == "free" else 60,
            "email_verified": bool(user.email_verified_at),
            "billing": "razorpay",
            "mfa_enabled": bool(user.mfa_enabled),
            "is_admin": bool(user.is_admin),
        },
    )


me_router = APIRouter(tags=["me"])


@me_router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOut:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    return _me_payload(user, profile)
