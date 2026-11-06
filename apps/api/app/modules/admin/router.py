from typing import Any

from fastapi import APIRouter, Depends, Header
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ForbiddenError
from app.db.session import get_db
from app.models import AnalyticsEvent, Job, ProductFeedback, User, UsageEvent

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise ForbiddenError("Admin access required")


@router.get("/overview")
def overview(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "jobs_queued": db.scalar(select(func.count()).select_from(Job).where(Job.status == "queued")) or 0,
        "jobs_failed": db.scalar(select(func.count()).select_from(Job).where(Job.status == "failed")) or 0,
        "feedback_open": db.scalar(select(func.count()).select_from(ProductFeedback).where(ProductFeedback.status == "open"))
        or 0,
        "analytics_events": db.scalar(select(func.count()).select_from(AnalyticsEvent)) or 0,
        "usage_events": db.scalar(select(func.count()).select_from(UsageEvent)) or 0,
    }


@router.get("/jobs")
def list_jobs(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
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


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: str, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, str]:
    from uuid import UUID

    job = db.get(Job, UUID(job_id))
    if not job:
        raise ForbiddenError("Job not found")
    job.status = "queued"
    job.error_code = None
    db.commit()
    return {"status": "queued"}
