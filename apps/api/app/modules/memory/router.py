from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models import Attempt, AuditEvent, Concept, ErrorPattern, LearnerMemory, Source, User, UserSkill
from app.schemas.common import MemoryOut, MessageOut

router = APIRouter(tags=["memory"])


class MemoryPatchIn(BaseModel):
    content_json: dict[str, Any] | None = None
    status: str | None = Field(default=None, pattern="^(active|disputed|deleted)$")


@router.get("/memory", response_model=list[MemoryOut])
def list_memory(
    memory_type: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MemoryOut]:
    q = select(LearnerMemory).where(LearnerMemory.user_id == user.id, LearnerMemory.status != "deleted")
    if memory_type:
        q = q.where(LearnerMemory.memory_type == memory_type)
    rows = db.scalars(q.order_by(LearnerMemory.created_at.desc()).limit(100)).all()
    return [MemoryOut.model_validate(r) for r in rows]


@router.patch("/memory/{memory_id}", response_model=MemoryOut)
def patch_memory(
    memory_id: UUID,
    payload: MemoryPatchIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryOut:
    row = db.scalar(select(LearnerMemory).where(LearnerMemory.id == memory_id, LearnerMemory.user_id == user.id))
    if not row:
        raise NotFoundError("Memory not found")
    if payload.content_json is not None:
        row.content_json = payload.content_json
        provenance = dict(row.provenance_json or {})
        provenance["user_corrected_at"] = datetime.now(UTC).isoformat()
        row.provenance_json = provenance
    if payload.status:
        row.status = payload.status
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="memory_patch",
            target_type="learner_memory",
            target_id=str(row.id),
            metadata_json={},
        )
    )
    db.commit()
    db.refresh(row)
    return MemoryOut.model_validate(row)


@router.delete("/memory/{memory_id}", response_model=MessageOut)
def delete_memory(
    memory_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MessageOut:
    row = db.scalar(select(LearnerMemory).where(LearnerMemory.id == memory_id, LearnerMemory.user_id == user.id))
    if not row:
        raise NotFoundError("Memory not found")
    row.status = "deleted"
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="memory_delete",
            target_type="learner_memory",
            target_id=str(row.id),
            metadata_json={},
        )
    )
    db.commit()
    return MessageOut(message="Memory marked deleted")


@router.get("/memory/errors")
def list_errors(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(ErrorPattern).where(ErrorPattern.user_id == user.id).order_by(ErrorPattern.recurrence_count.desc())
    ).all()
    return [
        {
            "id": str(r.id),
            "error_code": r.error_code,
            "description": r.description,
            "severity": r.severity,
            "recurrence_count": r.recurrence_count,
            "competency_id": str(r.competency_id) if r.competency_id else None,
        }
        for r in rows
    ]


@router.post("/exports", status_code=202)
def export_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    concepts = db.scalars(select(Concept).where(Concept.user_id == user.id)).all()
    memories = db.scalars(select(LearnerMemory).where(LearnerMemory.user_id == user.id)).all()
    skills = db.scalars(select(UserSkill).where(UserSkill.user_id == user.id)).all()
    attempts = db.scalars(select(Attempt).where(Attempt.user_id == user.id)).all()
    sources = db.scalars(select(Source).where(Source.user_id == user.id)).all()
    payload = {
        "exported_at": datetime.now(UTC).isoformat(),
        "user_id": str(user.id),
        "email": user.email,
        "concepts": [{"id": str(c.id), "title": c.title, "definition": c.definition, "status": c.status} for c in concepts],
        "memories": [
            {
                "id": str(m.id),
                "type": m.memory_type,
                "content": m.content_json,
                "status": m.status,
            }
            for m in memories
            if m.status != "deleted"
        ],
        "skills": [{"competency_id": str(s.competency_id), "status": s.status, "evidence_count": s.evidence_count} for s in skills],
        "attempts": [
            {
                "id": str(a.id),
                "practice_item_id": str(a.practice_item_id),
                "status": a.status,
                "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
            }
            for a in attempts
        ],
        "sources": [{"id": str(s.id), "title": s.title, "type": s.type, "status": s.status} for s in sources],
    }
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="data_export_requested",
            target_type="user",
            target_id=str(user.id),
            metadata_json={},
        )
    )
    db.commit()
    return payload


@router.post("/account/deletion", response_model=MessageOut)
def request_deletion(
    user: User = Depends(get_current_user), db: Session = Depends(get_db), response: Response = None
) -> MessageOut:
    user.status = "pending_deletion"
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="account_deletion_requested",
            target_type="user",
            target_id=str(user.id),
            metadata_json={},
        )
    )
    # Soft-delete active learning memory for immediate effect; hard purge job later.
    memories = db.scalars(select(LearnerMemory).where(LearnerMemory.user_id == user.id)).all()
    for m in memories:
        m.status = "deleted"
    db.commit()
    return MessageOut(message="Deletion requested. Active learning memory has been deactivated.")
