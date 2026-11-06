"""Hard account purge — deletes user-owned rows then the user."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    Attempt,
    AttemptError,
    AuditEvent,
    BaselineSession,
    CalendarConnection,
    Concept,
    ConceptEdge,
    ConceptSource,
    ErrorPattern,
    Evaluation,
    Goal,
    Job,
    LearnerMemory,
    OAuthAccount,
    PracticeItem,
    ProductFeedback,
    Profile,
    ProjectEvidence,
    ReviewEvent,
    ReviewState,
    SandboxRun,
    SkillDispute,
    Source,
    SourceSegment,
    Subscription,
    UsageEvent,
    User,
    UserSkill,
)
from app.services.storage import object_storage


def hard_purge_user(db: Session, user_id: UUID) -> dict[str, int]:
    user = db.get(User, user_id)
    if not user:
        return {"purged": 0}

    counts: dict[str, int] = {}

    # Collect storage keys before deleting sources.
    sources = db.scalars(select(Source).where(Source.user_id == user_id)).all()
    for source in sources:
        if source.object_key:
            try:
                object_storage.delete(source.object_key)
            except Exception:  # noqa: BLE001
                pass
        segs = db.scalars(select(SourceSegment).where(SourceSegment.source_id == source.id)).all()
        for seg in segs:
            db.execute(delete(ConceptSource).where(ConceptSource.source_segment_id == seg.id))
        db.execute(delete(SourceSegment).where(SourceSegment.source_id == source.id))
    counts["sources"] = len(sources)

    attempts = db.scalars(select(Attempt).where(Attempt.user_id == user_id)).all()
    for attempt in attempts:
        db.execute(delete(Evaluation).where(Evaluation.attempt_id == attempt.id))
        db.execute(delete(AttemptError).where(AttemptError.attempt_id == attempt.id))
    counts["attempts"] = len(attempts)

    for model in (
        SandboxRun,
        ReviewEvent,
        ReviewState,
        LearnerMemory,
        ErrorPattern,
        ConceptEdge,
        Concept,
        UserSkill,
        SkillDispute,
        BaselineSession,
        Goal,
        PracticeItem,  # user-owned only — curated have user_id NULL
        ProjectEvidence,
        CalendarConnection,
        OAuthAccount,
        Job,
        UsageEvent,
        ProductFeedback,
        Subscription,
        Profile,
        Source,
        Attempt,
    ):
        if model is PracticeItem:
            result = db.execute(delete(PracticeItem).where(PracticeItem.user_id == user_id))
        elif model is ProductFeedback:
            result = db.execute(delete(ProductFeedback).where(ProductFeedback.user_id == user_id))
        else:
            result = db.execute(delete(model).where(model.user_id == user_id))  # type: ignore[attr-defined]
        counts[model.__tablename__] = result.rowcount or 0

    db.add(
        AuditEvent(
            actor_id=None,
            action="account_hard_purged",
            target_type="user",
            target_id=str(user_id),
            metadata_json={"counts": counts, "email_hash": user.email.split("@")[-1]},
            occurred_at=datetime.now(UTC),
        )
    )
    db.delete(user)
    db.commit()
    counts["purged"] = 1
    return counts
