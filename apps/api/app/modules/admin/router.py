from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models import AnalyticsEvent, AuditEvent, Job, ProductFeedback, Subscription, User, UsageEvent
from app.services.mfa import verify_totp

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise ForbiddenError("Admin access required")


def require_admin_user(
    user: User = Depends(get_current_user),
    x_admin_mfa: str | None = Header(default=None),
) -> User:
    """Session-authenticated admin (is_admin) with MFA required when enabled."""
    if not user.is_admin:
        raise ForbiddenError("Admin access required")
    if user.mfa_enabled:
        if not x_admin_mfa or not user.mfa_secret or not verify_totp(user.mfa_secret, x_admin_mfa):
            raise ForbiddenError("Admin MFA code required (X-Admin-MFA header)")
    return user


def _overview(db: Session) -> dict[str, Any]:
    return {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "users_pending_deletion": db.scalar(select(func.count()).select_from(User).where(User.status == "pending_deletion"))
        or 0,
        "jobs_queued": db.scalar(select(func.count()).select_from(Job).where(Job.status == "queued")) or 0,
        "jobs_failed": db.scalar(select(func.count()).select_from(Job).where(Job.status == "failed")) or 0,
        "feedback_open": db.scalar(select(func.count()).select_from(ProductFeedback).where(ProductFeedback.status == "open"))
        or 0,
        "analytics_events": db.scalar(select(func.count()).select_from(AnalyticsEvent)) or 0,
        "usage_events": db.scalar(select(func.count()).select_from(UsageEvent)) or 0,
        "active_paid": db.scalar(select(func.count()).select_from(User).where(User.plan.in_(["plus", "pro"]))) or 0,
    }


def _list_jobs(db: Session) -> list[dict[str, Any]]:
    rows = db.scalars(select(Job).order_by(Job.created_at.desc()).limit(50)).all()
    return [
        {
            "id": str(r.id),
            "type": r.type,
            "status": r.status,
            "attempts": r.attempts,
            "error_code": r.error_code,
            "user_id": str(r.user_id) if r.user_id else None,
        }
        for r in rows
    ]


def _list_users(db: Session) -> list[dict[str, Any]]:
    rows = db.scalars(select(User).order_by(User.created_at.desc()).limit(100)).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "plan": u.plan,
            "status": u.status,
            "mfa_enabled": u.mfa_enabled,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in rows
    ]


@router.get("/overview")
def overview(_: None = Depends(require_admin_key), db: Session = Depends(get_db)) -> dict[str, Any]:
    return _overview(db)


@router.get("/overview/session")
def overview_session(admin: User = Depends(require_admin_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    data = _overview(db)
    data["admin_email"] = admin.email
    return data


@router.get("/jobs")
def list_jobs(_: None = Depends(require_admin_key), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _list_jobs(db)


@router.get("/jobs/session")
def list_jobs_session(_: User = Depends(require_admin_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _list_jobs(db)


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: str, _: None = Depends(require_admin_key), db: Session = Depends(get_db)) -> dict[str, str]:
    job = db.get(Job, UUID(job_id))
    if not job:
        raise NotFoundError("Job not found")
    job.status = "queued"
    job.error_code = None
    db.commit()
    return {"status": "queued"}


@router.post("/jobs/{job_id}/retry/session")
def retry_job_session(
    job_id: str, _: User = Depends(require_admin_user), db: Session = Depends(get_db)
) -> dict[str, str]:
    job = db.get(Job, UUID(job_id))
    if not job:
        raise NotFoundError("Job not found")
    job.status = "queued"
    job.error_code = None
    db.commit()
    return {"status": "queued"}


@router.get("/users")
def list_users(_: None = Depends(require_admin_key), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _list_users(db)


@router.get("/users/session")
def list_users_session(_: User = Depends(require_admin_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _list_users(db)


@router.get("/feedback")
def list_feedback(_: None = Depends(require_admin_key), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(select(ProductFeedback).order_by(ProductFeedback.created_at.desc()).limit(100)).all()
    return [
        {
            "id": str(r.id),
            "email": r.email,
            "category": r.category,
            "message": r.message,
            "status": r.status,
            "user_id": str(r.user_id) if r.user_id else None,
        }
        for r in rows
    ]


class FeedbackStatusIn(BaseModel):
    status: str = Field(pattern="^(open|closed|triaged)$")


@router.patch("/feedback/{feedback_id}")
def update_feedback(
    feedback_id: str,
    payload: FeedbackStatusIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    row = db.get(ProductFeedback, UUID(feedback_id))
    if not row:
        raise NotFoundError("Feedback not found")
    row.status = payload.status
    db.commit()
    return {"status": row.status}


class PromoteAdminIn(BaseModel):
    email: str
    is_admin: bool = True


@router.post("/users/promote")
def promote_admin(
    payload: PromoteAdminIn, _: None = Depends(require_admin_key), db: Session = Depends(get_db)
) -> dict[str, Any]:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise NotFoundError("User not found")
    user.is_admin = payload.is_admin
    db.add(
        AuditEvent(
            actor_id=None,
            action="admin_promote",
            target_type="user",
            target_id=str(user.id),
            metadata_json={"is_admin": payload.is_admin, "email": user.email},
            occurred_at=datetime.now(UTC),
        )
    )
    db.commit()
    return {"id": str(user.id), "email": user.email, "is_admin": user.is_admin}
