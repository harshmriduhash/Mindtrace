from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import ErrorPattern, PracticeItem, ReviewState, User, UserSkill
from app.modules.practice.scheduler import prefer_alternate_type
from app.schemas.common import RecommendationOut

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations/next", response_model=RecommendationOut)
def next_recommendation(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> RecommendationOut:
    now = datetime.now(UTC)

    # 1) Adaptive remediation for items with elevated consecutive fails / remediation modes
    remediating = db.scalar(
        select(ReviewState)
        .where(
            ReviewState.user_id == user.id,
            ReviewState.remediation_mode.in_(["varied", "tutor_first", "implement"]),
            ReviewState.due_at <= now,
        )
        .order_by(ReviewState.consecutive_fails.desc(), ReviewState.due_at)
        .limit(1)
    )
    if remediating:
        base = db.get(PracticeItem, remediating.practice_item_id)
        preferred = prefer_alternate_type(base.type if base else "explain", remediating.remediation_mode)
        alt = None
        if base and base.competency_id:
            for t in preferred:
                alt = db.scalar(
                    select(PracticeItem).where(
                        PracticeItem.competency_id == base.competency_id,
                        PracticeItem.is_curated.is_(True),
                        PracticeItem.type == t,
                    ).limit(1)
                )
                if alt:
                    break
        item = alt or base
        reason = {
            "varied": "You missed this recently — trying a different question style.",
            "tutor_first": "Repeated misses — re-explain the concept, then practice again.",
            "implement": "Repeated misses — switch to a hands-on implement task.",
        }.get(remediating.remediation_mode, "Targeted remediation based on recent performance.")
        href = (
            f"/app/practice/implement?item={item.id}"
            if item and item.type == "implement"
            else (f"/app/practice/assessment?item={item.id}" if item else "/app/practice")
        )
        if remediating.remediation_mode == "tutor_first":
            href = "/app/learn"
        return RecommendationOut(
            action_type="remediation",
            title=(item.prompt[:120] if item else "Remediation practice"),
            reason=reason,
            estimated_minutes=item.expected_minutes if item else 10,
            practice_item_id=item.id if item else None,
            skill_gap=remediating.remediation_mode,
            href=href,
        )

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

    # Recurring error patterns drive next action
    top_error = db.scalar(
        select(ErrorPattern)
        .where(ErrorPattern.user_id == user.id, ErrorPattern.recurrence_count >= 2)
        .order_by(ErrorPattern.recurrence_count.desc())
        .limit(1)
    )
    if top_error and top_error.competency_id:
        item = db.scalar(
            select(PracticeItem).where(
                PracticeItem.competency_id == top_error.competency_id,
                PracticeItem.is_curated.is_(True),
                PracticeItem.type.in_(["diagnose", "implement", "explain"]),
            ).limit(1)
        )
        if item:
            return RecommendationOut(
                action_type="error_focus",
                title=item.prompt[:120],
                reason=f"Recurring error ({top_error.error_code}): {top_error.description[:120]}",
                estimated_minutes=item.expected_minutes,
                practice_item_id=item.id,
                skill_gap=top_error.error_code,
                href=(
                    f"/app/practice/implement?item={item.id}"
                    if item.type == "implement"
                    else f"/app/practice/assessment?item={item.id}"
                ),
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
                PracticeItem.type.in_(["explain", "design", "diagnose", "recall", "implement"]),
            ).limit(1)
        )
        return RecommendationOut(
            action_type="practice",
            title=item.prompt[:120] if item else "Target a weak competency",
            reason="Prior attempt evidence shows this competency needs review.",
            estimated_minutes=item.expected_minutes if item else 10,
            practice_item_id=item.id if item else None,
            skill_gap=weak.status,
            href=(
                f"/app/practice/implement?item={item.id}"
                if item and item.type == "implement"
                else (f"/app/practice/assessment?item={item.id}" if item else "/app/practice")
            ),
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
