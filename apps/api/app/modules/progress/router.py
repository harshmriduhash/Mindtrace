from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Attempt, Concept, Competency, ErrorPattern, Evaluation, User, UserSkill
from app.schemas.common import CompetencyOut, ProgressOut, UserSkillOut

router = APIRouter(tags=["progress"])


@router.get("/progress", response_model=ProgressOut)
def get_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProgressOut:
    attempts_count = db.scalar(select(func.count()).select_from(Attempt).where(Attempt.user_id == user.id)) or 0
    evaluations_count = db.scalar(
        select(func.count())
        .select_from(Evaluation)
        .join(Attempt, Attempt.id == Evaluation.attempt_id)
        .where(Attempt.user_id == user.id)
    ) or 0
    concepts_approved = db.scalar(
        select(func.count()).select_from(Concept).where(Concept.user_id == user.id, Concept.status == "approved")
    ) or 0
    error_patterns = db.scalar(
        select(func.count()).select_from(ErrorPattern).where(ErrorPattern.user_id == user.id)
    ) or 0

    skills_rows = db.scalars(select(UserSkill).where(UserSkill.user_id == user.id)).all()
    skills: list[UserSkillOut] = []
    for row in skills_rows:
        comp = db.get(Competency, row.competency_id)
        item = UserSkillOut.model_validate(row)
        item.competency = CompetencyOut.model_validate(comp) if comp else None
        skills.append(item)

    recent = db.scalars(
        select(Attempt).where(Attempt.user_id == user.id).order_by(Attempt.created_at.desc()).limit(20)
    ).all()
    recent_attempts: list[dict[str, Any]] = []
    for a in recent:
        evaluation = db.scalar(select(Evaluation).where(Evaluation.attempt_id == a.id))
        recent_attempts.append(
            {
                "id": str(a.id),
                "practice_item_id": str(a.practice_item_id),
                "status": a.status,
                "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
                "overall_score": (evaluation.result_json or {}).get("overall_score") if evaluation else None,
                "is_provisional": evaluation.is_provisional if evaluation else None,
            }
        )

    return ProgressOut(
        attempts_count=attempts_count,
        evaluations_count=evaluations_count,
        concepts_approved=concepts_approved,
        error_patterns=error_patterns,
        skills=skills,
        recent_attempts=recent_attempts,
    )
