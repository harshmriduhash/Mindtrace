"""Source ingestion pipeline helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.provider import ai_provider
from app.models import Concept, ConceptSource, Job, Source, SourceSegment, UsageEvent


def extract_and_attach_concepts(db: Session, *, source: Source, text: str, user_id) -> int:
    job = Job(
        user_id=user_id,
        type="source_extract",
        status="running",
        idempotency_key=(source.metadata_json or {}).get("idempotency_key"),
        payload_json={"source_id": str(source.id)},
    )
    db.add(job)
    db.flush()

    segment = SourceSegment(
        source_id=source.id,
        segment_index=0,
        text_ref=text[:4000] if text else "",
        page_or_timestamp="1",
        metadata_json={},
    )
    db.add(segment)
    db.flush()

    extracted = ai_provider.extract_concepts(text or source.title, source.title)
    for item in extracted:
        concept = Concept(
            user_id=user_id,
            title=str(item.get("title", "Untitled"))[:255],
            definition=str(item.get("definition", ""))[:4000],
            concept_type=str(item.get("concept_type", "idea")),
            status="proposed",
            confidence=item.get("confidence"),
        )
        db.add(concept)
        db.flush()
        db.add(
            ConceptSource(
                concept_id=concept.id,
                source_segment_id=segment.id,
                relation="extracted_from",
                confidence=item.get("confidence"),
            )
        )

    source.status = "ready_for_review"
    source.raw_text = text
    job.status = "completed"
    job.result_json = {"concepts": len(extracted)}
    db.add(UsageEvent(user_id=user_id, feature="source_import", units=1, cost_usd=0, metadata_json={"type": source.type}))
    return len(extracted)
