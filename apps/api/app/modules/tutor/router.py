from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.provider import ai_provider
from app.core.deps import get_current_user
from app.core.errors import NotFoundError, QuotaExceededError
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Concept, ConceptSource, SourceSegment, UsageEvent, User
from datetime import UTC, datetime, timedelta
from sqlalchemy import func

router = APIRouter(prefix="/tutor", tags=["tutor"])


class TutorRequest(BaseModel):
    concept_id: UUID
    question: str | None = Field(default=None, max_length=2000)


class TutorResponse(BaseModel):
    explanation: str
    citations: list[dict]
    model_version: str
    prompt_version: str


@router.post("/explain", response_model=TutorResponse)
def explain_concept(
    payload: TutorRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TutorResponse:
    settings = get_settings()
    day_ago = datetime.now(UTC) - timedelta(days=1)
    used = db.scalar(
        select(func.count())
        .select_from(UsageEvent)
        .where(
            UsageEvent.user_id == user.id,
            UsageEvent.feature == "tutor_explain",
            UsageEvent.occurred_at >= day_ago,
        )
    )
    limit = settings.free_ai_evaluations_per_day if user.plan == "free" else 200
    if (used or 0) >= limit:
        raise QuotaExceededError("Daily tutor quota exceeded")

    concept = db.scalar(
        select(Concept).where(Concept.id == payload.concept_id, Concept.user_id == user.id, Concept.status == "approved")
    )
    if not concept:
        raise NotFoundError("Approved concept not found")

    segment_ids = db.scalars(
        select(ConceptSource.source_segment_id).where(ConceptSource.concept_id == concept.id)
    ).all()
    segments = db.scalars(select(SourceSegment).where(SourceSegment.id.in_(segment_ids))).all() if segment_ids else []
    sources = [s.text_ref for s in segments if s.text_ref]

    result = ai_provider.tutor_explain(concept.title, concept.definition, sources)
    if payload.question:
        result["explanation"] = (
            f"{result.get('explanation', '')}\n\n"
            f"**Your question:** {payload.question}\n"
            "Answer using only the approved concept and cited source excerpts above."
        )

    db.add(UsageEvent(user_id=user.id, feature="tutor_explain", units=1, cost_usd=0, metadata_json={}))
    db.commit()
    return TutorResponse(
        explanation=result.get("explanation", ""),
        citations=result.get("citations") or [],
        model_version=result.get("model_version", "deterministic-tutor-v1"),
        prompt_version=result.get("prompt_version", "none"),
    )
