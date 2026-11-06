"""Skill Passport — evidence-based competency summary (not a hiring credential)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Attempt, Competency, Evaluation, Goal, PracticeItem, Profile, SkillPath, User, UserSkill
from app.services.analytics import track

router = APIRouter(prefix="/passport", tags=["passport"])


class PassportOut(BaseModel):
    generated_at: str
    learner: dict[str, Any]
    goal: dict[str, Any] | None
    skill_path: dict[str, Any] | None
    summary: dict[str, Any]
    competencies: list[dict[str, Any]]
    disclaimer: str


@router.get("", response_model=PassportOut)
def get_passport(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PassportOut:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    goal = db.scalar(select(Goal).where(Goal.user_id == user.id, Goal.status == "active"))
    path = db.get(SkillPath, goal.skill_path_id) if goal and goal.skill_path_id else None

    skills = db.scalars(select(UserSkill).where(UserSkill.user_id == user.id)).all()
    competencies: list[dict[str, Any]] = []
    counts = {"demonstrated": 0, "developing": 0, "emerging": 0, "needs_review": 0, "not_assessed": 0}
    disputed_count = 0

    for skill in skills:
        comp = db.get(Competency, skill.competency_id)
        if not comp:
            continue
        counts[skill.status] = counts.get(skill.status, 0) + 1
        if skill.disputed:
            disputed_count += 1

        practice_ids = db.scalars(select(PracticeItem.id).where(PracticeItem.competency_id == comp.id)).all()
        evidence: list[dict[str, Any]] = []
        if practice_ids:
            attempts = db.scalars(
                select(Attempt)
                .where(
                    Attempt.user_id == user.id,
                    Attempt.practice_item_id.in_(practice_ids),
                    Attempt.status == "submitted",
                )
                .order_by(Attempt.submitted_at.desc())
                .limit(5)
            ).all()
            for attempt in attempts:
                ev = db.scalar(select(Evaluation).where(Evaluation.attempt_id == attempt.id))
                evidence.append(
                    {
                        "attempt_id": str(attempt.id),
                        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                        "overall_score": (ev.result_json or {}).get("overall_score") if ev else None,
                        "is_provisional": ev.is_provisional if ev else True,
                        "challenged": bool(ev and ev.challenge_status == "challenged"),
                    }
                )

        competencies.append(
            {
                "slug": comp.slug,
                "title": comp.title,
                "definition": comp.definition,
                "status": skill.status,
                "evidence_count": skill.evidence_count,
                "disputed": skill.disputed,
                "last_attempt_at": skill.last_attempt_at.isoformat() if skill.last_attempt_at else None,
                "recent_evidence": evidence,
            }
        )

    attempts_total = db.scalar(select(func.count()).select_from(Attempt).where(Attempt.user_id == user.id)) or 0
    track(db, user_id=user.id, event_name="passport_viewed", properties={})
    db.commit()

    return PassportOut(
        generated_at=datetime.now(UTC).isoformat(),
        learner={
            "display_name": profile.display_name if profile else None,
            "role_target": profile.role_target if profile else None,
            "plan": user.plan,
        },
        goal={"title": goal.title, "weekly_time_budget_minutes": goal.weekly_time_budget_minutes} if goal else None,
        skill_path={"slug": path.slug, "title": path.title, "version": path.version} if path else None,
        summary={
            "competency_counts": counts,
            "disputed_count": disputed_count,
            "attempts_total": attempts_total,
            "demonstrated_count": counts.get("demonstrated", 0),
        },
        competencies=sorted(competencies, key=lambda c: c["title"]),
        disclaimer=(
            "Mindtrace Skill Passport is a personal evidence summary for learning coaching. "
            "Statuses are based on practice attempts and provisional rubric scores with uncertainty. "
            "It is not a certification, hiring recommendation, or guarantee of interview performance."
        ),
    )
