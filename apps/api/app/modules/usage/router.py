from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import UsageEvent, User

router = APIRouter(prefix="/usage", tags=["usage"])


class UsageOut(BaseModel):
    plan: str
    period_start: datetime
    period_end: datetime
    features: dict[str, dict]


@router.get("", response_model=UsageOut)
def get_usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UsageOut:
    settings = get_settings()
    now = datetime.now(UTC)
    day_start = now - timedelta(days=1)
    hour_start = now - timedelta(hours=1)

    def count(feature: str, since: datetime) -> int:
        return (
            db.scalar(
                select(func.count())
                .select_from(UsageEvent)
                .where(UsageEvent.user_id == user.id, UsageEvent.feature == feature, UsageEvent.occurred_at >= since)
            )
            or 0
        )

    imports_limit = settings.free_source_imports_per_hour if user.plan == "free" else 60
    ai_limit = settings.free_ai_evaluations_per_day if user.plan == "free" else 200

    return UsageOut(
        plan=user.plan,
        period_start=day_start,
        period_end=now,
        features={
            "source_imports_hour": {
                "used": count("source_import", hour_start),
                "limit": imports_limit,
                "reset": "hourly",
            },
            "tutor_explain_day": {
                "used": count("tutor_explain", day_start),
                "limit": ai_limit,
                "reset": "daily",
            },
            "assessment_evaluation_day": {
                "used": count("assessment_evaluation", day_start),
                "limit": ai_limit,
                "reset": "daily",
            },
            "concepts_approved_day": {
                "used": count("concepts_approved", day_start),
                "limit": None,
                "reset": "daily",
            },
        },
    )
