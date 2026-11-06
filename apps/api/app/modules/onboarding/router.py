from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import AppError, NotFoundError
from app.db.session import get_db
from app.models import Competency, Goal, Profile, SkillPath, User, UserSkill
from app.schemas.common import MeOut, OnboardingIn
from app.modules.auth.router import _me_payload

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/complete", response_model=MeOut)
def complete_onboarding(
    payload: OnboardingIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeOut:
    path = db.scalar(select(SkillPath).where(SkillPath.slug == payload.skill_path_slug, SkillPath.is_active.is_(True)))
    if not path:
        raise NotFoundError("Skill path not found")

    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if not profile:
        raise AppError("profile_missing", "Profile missing", 500)
    profile.display_name = payload.display_name or profile.display_name
    profile.role_target = payload.role_target
    profile.timezone = payload.timezone

    existing_goal = db.scalar(select(Goal).where(Goal.user_id == user.id, Goal.status == "active"))
    if existing_goal:
        existing_goal.title = payload.goal_title
        existing_goal.skill_path_id = path.id
        existing_goal.weekly_time_budget_minutes = payload.weekly_time_budget_minutes
    else:
        db.add(
            Goal(
                user_id=user.id,
                title=payload.goal_title,
                skill_path_id=path.id,
                weekly_time_budget_minutes=payload.weekly_time_budget_minutes,
                status="active",
            )
        )

    competencies = db.scalars(select(Competency).where(Competency.path_id == path.id)).all()
    for comp in competencies:
        existing = db.scalar(
            select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.competency_id == comp.id)
        )
        if not existing:
            db.add(
                UserSkill(
                    user_id=user.id,
                    competency_id=comp.id,
                    status="not_assessed",
                    evidence_count=0,
                )
            )

    user.onboarding_completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    return _me_payload(user, profile)
