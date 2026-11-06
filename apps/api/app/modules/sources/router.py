from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import AppError, NotFoundError, QuotaExceededError
from app.db.session import get_db
from app.models import Concept, ConceptSource, Source, SourceSegment, UsageEvent, User
from app.modules.sources.service import extract_and_attach_concepts
from app.schemas.common import ApproveConceptsIn, ConceptOut, SourceCreateIn
from app.services.pdf_extract import extract_pdf_text
from app.services.ssrf import fetch_public_text

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceOut(BaseModel):
    id: UUID
    type: str
    title: str
    status: str
    source_uri: str | None
    error_code: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


def _enforce_import_quota(db: Session, user: User) -> None:
    settings = get_settings()
    hour_ago = datetime.now(UTC) - timedelta(hours=1)
    recent = db.scalar(
        select(func.count()).select_from(Source).where(Source.user_id == user.id, Source.created_at >= hour_ago)
    )
    limit = settings.free_source_imports_per_hour if user.plan == "free" else 60
    if (recent or 0) >= limit:
        raise QuotaExceededError("Source import quota exceeded for this hour")


@router.post("", response_model=SourceOut, status_code=202)
def create_source(
    payload: SourceCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SourceOut:
    settings = get_settings()
    _enforce_import_quota(db, user)

    text = (payload.text or "").strip()
    meta: dict = {"idempotency_key": payload.idempotency_key}
    error_code = None

    try:
        if payload.type == "url":
            if not payload.url:
                raise AppError("invalid_url", "URL is required for url sources", 400)
            text = fetch_public_text(payload.url)
            meta["fetched"] = True
        elif payload.type == "text":
            if not text:
                raise AppError("empty_text", "Text content is required", 400)
        elif payload.type == "pdf":
            raise AppError("use_upload", "Use /sources/upload for PDF files", 400)
        else:
            raise AppError("invalid_type", "Unsupported source type", 400)
    except AppError as exc:
        source = Source(
            user_id=user.id,
            type=payload.type,
            title=payload.title,
            source_uri=payload.url,
            status="failed",
            raw_text=None,
            error_code=exc.code,
            metadata_json=meta,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        raise

    if len(text) > settings.max_text_chars:
        text = text[: settings.max_text_chars]

    source = Source(
        user_id=user.id,
        type=payload.type,
        title=payload.title,
        source_uri=payload.url,
        status="processing",
        metadata_json=meta,
    )
    db.add(source)
    db.flush()
    extract_and_attach_concepts(db, source=source, text=text, user_id=user.id)
    db.commit()
    db.refresh(source)
    return SourceOut.model_validate(source)


@router.post("/upload", response_model=SourceOut, status_code=202)
async def upload_pdf(
    title: str = Form(...),
    idempotency_key: str | None = Form(default=None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SourceOut:
    settings = get_settings()
    _enforce_import_quota(db, user)

    filename = file.filename or "upload.pdf"
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in {"application/pdf", "application/x-pdf"}:
        # Still allow if magic bytes check passes.
        pass

    from app.models import Job
    from app.services.storage import object_storage

    data = await file.read(settings.max_pdf_bytes + 1)
    try:
        text, pdf_meta = extract_pdf_text(data, max_bytes=settings.max_pdf_bytes)
    except AppError as exc:
        source = Source(
            user_id=user.id,
            type="pdf",
            title=title,
            status="failed",
            error_code=exc.code,
            metadata_json={"filename": filename, "idempotency_key": idempotency_key},
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        raise

    if len(text) > settings.max_text_chars:
        text = text[: settings.max_text_chars]

    checksum = object_storage.checksum(data)
    object_key = f"users/{user.id}/sources/{checksum}.pdf"
    object_storage.put_bytes(key=object_key, data=data, content_type="application/pdf")

    source = Source(
        user_id=user.id,
        type="pdf",
        title=title,
        status="processing",
        object_key=object_key,
        checksum=checksum,
        raw_text=text if settings.sync_ingest else None,
        metadata_json={"filename": filename, "idempotency_key": idempotency_key, **pdf_meta},
    )
    db.add(source)
    db.flush()

    job = Job(
        user_id=user.id,
        type="source_extract",
        status="queued",
        idempotency_key=idempotency_key,
        payload_json={"source_id": str(source.id)},
    )
    db.add(job)
    db.flush()

    if settings.sync_ingest:
        extract_and_attach_concepts(db, source=source, text=text, user_id=user.id, create_job=False)
        job.status = "completed"
        job.result_json = {"synced": True}
    db.commit()
    db.refresh(source)
    return SourceOut.model_validate(source)


@router.get("", response_model=list[SourceOut])
def list_sources(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SourceOut]:
    rows = db.scalars(select(Source).where(Source.user_id == user.id).order_by(Source.created_at.desc())).all()
    return [SourceOut.model_validate(r) for r in rows]


@router.get("/{source_id}", response_model=SourceOut)
def get_source(source_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> SourceOut:
    source = db.scalar(select(Source).where(Source.id == source_id, Source.user_id == user.id))
    if not source:
        raise NotFoundError("Source not found")
    return SourceOut.model_validate(source)


@router.get("/{source_id}/concepts", response_model=list[ConceptOut])
def list_source_concepts(
    source_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ConceptOut]:
    source = db.scalar(select(Source).where(Source.id == source_id, Source.user_id == user.id))
    if not source:
        raise NotFoundError("Source not found")
    segment_ids = db.scalars(select(SourceSegment.id).where(SourceSegment.source_id == source_id)).all()
    if not segment_ids:
        return []
    concept_ids = db.scalars(
        select(ConceptSource.concept_id).where(ConceptSource.source_segment_id.in_(segment_ids))
    ).all()
    concepts = db.scalars(select(Concept).where(Concept.id.in_(concept_ids), Concept.user_id == user.id)).all()
    return [ConceptOut.model_validate(c) for c in concepts]


@router.post("/{source_id}/approve-concepts", response_model=list[ConceptOut])
def approve_concepts(
    source_id: UUID,
    payload: ApproveConceptsIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConceptOut]:
    source = db.scalar(select(Source).where(Source.id == source_id, Source.user_id == user.id))
    if not source:
        raise NotFoundError("Source not found")

    approved: list[Concept] = []
    for cid in payload.concept_ids:
        concept = db.scalar(select(Concept).where(Concept.id == cid, Concept.user_id == user.id))
        if concept:
            concept.status = "approved"
            approved.append(concept)
    for cid in payload.reject_ids:
        concept = db.scalar(select(Concept).where(Concept.id == cid, Concept.user_id == user.id))
        if concept:
            concept.status = "rejected"

    source.status = "committed"
    db.add(UsageEvent(user_id=user.id, feature="concepts_approved", units=len(approved), cost_usd=0, metadata_json={}))
    db.commit()
    return [ConceptOut.model_validate(c) for c in approved]
