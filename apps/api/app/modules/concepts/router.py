from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models import Concept, ConceptSource, Source, SourceSegment, User
from app.schemas.common import ConceptOut
from app.services.analytics import track

router = APIRouter(prefix="/concepts", tags=["concepts"])


class ConceptPatchIn(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    definition: str | None = Field(default=None, min_length=1, max_length=8000)
    concept_type: str | None = None


class ProvenanceOut(BaseModel):
    source_id: str | None
    source_title: str | None
    source_type: str | None
    segment_id: str
    page_or_timestamp: str | None
    excerpt: str


class ConceptDetailOut(ConceptOut):
    provenance: list[ProvenanceOut] = []
    user_edited_at: str | None = None


@router.get("/{concept_id}", response_model=ConceptDetailOut)
def get_concept(
    concept_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConceptDetailOut:
    concept = db.scalar(select(Concept).where(Concept.id == concept_id, Concept.user_id == user.id))
    if not concept:
        raise NotFoundError("Concept not found")
    return _detail(db, concept)


@router.patch("/{concept_id}", response_model=ConceptDetailOut)
def patch_concept(
    concept_id: UUID,
    payload: ConceptPatchIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConceptDetailOut:
    concept = db.scalar(select(Concept).where(Concept.id == concept_id, Concept.user_id == user.id))
    if not concept:
        raise NotFoundError("Concept not found")
    if payload.title is not None:
        concept.title = payload.title
    if payload.definition is not None:
        concept.definition = payload.definition
    if payload.concept_type is not None:
        concept.concept_type = payload.concept_type
    # Stash edit marker in a lightweight way via provenance-like note on related ConceptSource confidence untouched
    meta_key = f"edited:{concept.id}"
    track(db, user_id=user.id, event_name="concept_edited", properties={"concept_id": str(concept.id)})
    db.commit()
    db.refresh(concept)
    detail = _detail(db, concept)
    detail.user_edited_at = datetime.now(UTC).isoformat()
    return detail


def _detail(db: Session, concept: Concept) -> ConceptDetailOut:
    links = db.scalars(select(ConceptSource).where(ConceptSource.concept_id == concept.id)).all()
    provenance: list[ProvenanceOut] = []
    for link in links:
        segment = db.get(SourceSegment, link.source_segment_id)
        if not segment:
            continue
        source = db.get(Source, segment.source_id)
        provenance.append(
            ProvenanceOut(
                source_id=str(source.id) if source else None,
                source_title=source.title if source else None,
                source_type=source.type if source else None,
                segment_id=str(segment.id),
                page_or_timestamp=segment.page_or_timestamp,
                excerpt=(segment.text_ref or "")[:280],
            )
        )
    base = ConceptOut.model_validate(concept)
    return ConceptDetailOut(**base.model_dump(), provenance=provenance)
