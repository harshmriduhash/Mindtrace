from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models import Competency, User, UserSkill, SkillPath
from app.schemas.common import CompetencyOut, SkillPathOut, UserSkillOut

router = APIRouter(tags=["skills"])


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


@router.get("/skills/{skill_id}", response_model=UserSkillOut)
def get_skill(
    skill_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> UserSkillOut:
    row = db.scalar(select(UserSkill).where(UserSkill.id == skill_id, UserSkill.user_id == user.id))
    if not row:
        raise NotFoundError("Skill not found")
    comp = db.get(Competency, row.competency_id)
    item = UserSkillOut.model_validate(row)
    item.competency = CompetencyOut.model_validate(comp) if comp else None
    return item


@router.get("/skill-paths/{slug}/competencies", response_model=list[CompetencyOut])
def list_competencies(slug: str, db: Session = Depends(get_db)) -> list[CompetencyOut]:
    path = db.scalar(select(SkillPath).where(SkillPath.slug == slug))
    if not path:
        raise NotFoundError("Skill path not found")
    rows = db.scalars(
        select(Competency).where(Competency.path_id == path.id).order_by(Competency.sort_order)
    ).all()
    return [CompetencyOut.model_validate(r) for r in rows]
