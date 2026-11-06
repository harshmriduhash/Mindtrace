from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models import Attempt, Competency, Evaluation, PracticeItem, SkillDispute, SkillPath, User, UserSkill
from app.schemas.common import CompetencyOut, SkillPathOut, UserSkillOut
from app.services.analytics import track

router = APIRouter(tags=["skills"])


class DisputeIn(BaseModel):
    reason: str = Field(min_length=10, max_length=4000)


class SkillDetailOut(BaseModel):
    skill: UserSkillOut
    prerequisites: list[CompetencyOut]
    dependents: list[CompetencyOut]
    evidence: list[dict[str, Any]]
    disputed: bool
    dispute_note: str | None


@router.get("/skill-paths", response_model=list[SkillPathOut])
def list_skill_paths(db: Session = Depends(get_db)) -> list[SkillPathOut]:
    rows = db.scalars(select(SkillPath).where(SkillPath.is_active.is_(True)).order_by(SkillPath.title)).all()
    return [SkillPathOut.model_validate(r) for r in rows]


@router.get("/skills", response_model=list[UserSkillOut])
def list_user_skills(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserSkillOut]:
    rows = db.scalars(select(UserSkill).where(UserSkill.user_id == user.id)).all()
    out: list[UserSkillOut] = []
    for row in rows:
        comp = db.get(Competency, row.competency_id)
        item = UserSkillOut.model_validate(row)
        item.competency = CompetencyOut.model_validate(comp) if comp else None
        out.append(item)
    return out


@router.get("/skills/{skill_id}", response_model=SkillDetailOut)
def get_skill(
    skill_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> SkillDetailOut:
    row = db.scalar(select(UserSkill).where(UserSkill.id == skill_id, UserSkill.user_id == user.id))
    if not row:
        raise NotFoundError("Skill not found")
    comp = db.get(Competency, row.competency_id)
    item = UserSkillOut.model_validate(row)
    item.competency = CompetencyOut.model_validate(comp) if comp else None

    prereqs: list[CompetencyOut] = []
    dependents: list[CompetencyOut] = []
    if comp and comp.parent_id:
        parent = db.get(Competency, comp.parent_id)
        if parent:
            prereqs.append(CompetencyOut.model_validate(parent))
    if comp:
        kids = db.scalars(select(Competency).where(Competency.parent_id == comp.id).order_by(Competency.sort_order)).all()
        dependents = [CompetencyOut.model_validate(k) for k in kids]

    evidence: list[dict[str, Any]] = []
    if comp:
        items = db.scalars(select(PracticeItem).where(PracticeItem.competency_id == comp.id)).all()
        item_ids = [i.id for i in items]
        if item_ids:
            attempts = db.scalars(
                select(Attempt)
                .where(Attempt.user_id == user.id, Attempt.practice_item_id.in_(item_ids), Attempt.status == "submitted")
                .order_by(Attempt.submitted_at.desc())
                .limit(20)
            ).all()
            for a in attempts:
                ev = db.scalar(select(Evaluation).where(Evaluation.attempt_id == a.id))
                practice = db.get(PracticeItem, a.practice_item_id)
                evidence.append(
                    {
                        "attempt_id": str(a.id),
                        "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
                        "prompt": (practice.prompt[:120] if practice else None),
                        "overall_score": (ev.result_json or {}).get("overall_score") if ev else None,
                        "is_provisional": ev.is_provisional if ev else None,
                        "challenge_status": ev.challenge_status if ev else None,
                    }
                )

    return SkillDetailOut(
        skill=item,
        prerequisites=prereqs,
        dependents=dependents,
        evidence=evidence,
        disputed=bool(row.disputed),
        dispute_note=row.dispute_note,
    )


@router.post("/skills/{skill_id}/dispute", response_model=SkillDetailOut)
def dispute_skill(
    skill_id: UUID,
    payload: DisputeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillDetailOut:
    row = db.scalar(select(UserSkill).where(UserSkill.id == skill_id, UserSkill.user_id == user.id))
    if not row:
        raise NotFoundError("Skill not found")
    row.disputed = True
    row.dispute_note = payload.reason
    if row.status == "demonstrated":
        row.status = "needs_review"
    db.add(
        SkillDispute(
            user_id=user.id,
            user_skill_id=row.id,
            reason=payload.reason,
            status="open",
        )
    )
    track(db, user_id=user.id, event_name="skill_disputed", properties={"user_skill_id": str(row.id)})
    db.commit()
    return get_skill(skill_id, user, db)


@router.get("/skill-paths/{slug}/competencies", response_model=list[CompetencyOut])
def list_competencies(slug: str, db: Session = Depends(get_db)) -> list[CompetencyOut]:
    path = db.scalar(select(SkillPath).where(SkillPath.slug == slug))
    if not path:
        raise NotFoundError("Skill path not found")
    rows = db.scalars(
        select(Competency).where(Competency.path_id == path.id).order_by(Competency.sort_order)
    ).all()
    return [CompetencyOut.model_validate(r) for r in rows]


@router.get("/skill-paths/{slug}/map")
def competency_map(slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    path = db.scalar(select(SkillPath).where(SkillPath.slug == slug))
    if not path:
        raise NotFoundError("Skill path not found")
    comps = db.scalars(select(Competency).where(Competency.path_id == path.id).order_by(Competency.sort_order)).all()
    skills = {
        s.competency_id: s
        for s in db.scalars(select(UserSkill).where(UserSkill.user_id == user.id)).all()
    }
    nodes = []
    for c in comps:
        us = skills.get(c.id)
        nodes.append(
            {
                "id": str(c.id),
                "slug": c.slug,
                "title": c.title,
                "parent_id": str(c.parent_id) if c.parent_id else None,
                "status": us.status if us else "not_assessed",
                "evidence_count": us.evidence_count if us else 0,
                "disputed": us.disputed if us else False,
                "user_skill_id": str(us.id) if us else None,
            }
        )
    return {"path": SkillPathOut.model_validate(path).model_dump(), "nodes": nodes}
