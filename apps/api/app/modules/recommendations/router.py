from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import PracticeItem, ReviewState, User, UserSkill
from app.schemas.common import RecommendationOut

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations/next", response_model=RecommendationOut)
def next_recommendation(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> RecommendationOut:
    now = datetime.now(UTC)

    due = db.scalar(
        select(ReviewState)
        .where(ReviewState.user_id == user.id, ReviewState.due_at <= now)
        .order_by(ReviewState.due_at)
        .limit(1)
    )
    if due:
        item = db.get(PracticeItem, due.practice_item_id)
        return RecommendationOut(
            action_type="review",
            title=item.prompt[:120] if item else "Due review",
            reason="Scheduled review based on your last performance and elapsed time.",
            estimated_minutes=item.expected_minutes if item else 8,
            practice_item_id=due.practice_item_id,
            href=f"/app/practice/review?item={due.practice_item_id}",
        )

    not_assessed = db.scalar(
        select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.status == "not_assessed").limit(1)
    )
    if not_assessed or not user.onboarding_completed_at:
        baseline = db.scalar(
            select(PracticeItem).where(PracticeItem.is_curated.is_(True), PracticeItem.type == "baseline").limit(1)
        )
        return RecommendationOut(
            action_type="baseline",
            title="Complete your baseline assessment",
            reason="Establish starting evidence before Mindtrace recommends targeted practice.",
            estimated_minutes=12,
            practice_item_id=baseline.id if baseline else None,
            skill_gap="not_assessed",
            href="/app/practice/baseline",
        )

    weak = db.scalar(
        select(UserSkill)
        .where(UserSkill.user_id == user.id, UserSkill.status.in_(["emerging", "needs_review"]))
        .order_by(UserSkill.updated_at)
        .limit(1)
    )
    if weak:
        item = db.scalar(
            select(PracticeItem).where(
                PracticeItem.competency_id == weak.competency_id,
                PracticeItem.is_curated.is_(True),
                PracticeItem.type.in_(["explain", "design", "diagnose", "recall"]),
            ).limit(1)
        )
        return RecommendationOut(
            action_type="practice",
            title=item.prompt[:120] if item else "Target a weak competency",
            reason="Prior attempt evidence shows this competency needs review.",
            estimated_minutes=item.expected_minutes if item else 10,
            practice_item_id=item.id if item else None,
            skill_gap=weak.status,
            href=f"/app/practice/assessment?item={item.id}" if item else "/app/practice",
        )

    item = db.scalar(
        select(PracticeItem).where(PracticeItem.is_curated.is_(True), PracticeItem.type == "design").limit(1)
    )
    return RecommendationOut(
        action_type="practice",
        title=item.prompt[:120] if item else "Import a learning source",
        reason="No due reviews. Continue building applied evidence on your skill path.",
        estimated_minutes=item.expected_minutes if item else 10,
        practice_item_id=item.id if item else None,
        href=f"/app/practice/assessment?item={item.id}" if item else "/app/learn",
    )
