"""Voice practice — client transcript preferred; optional Whisper when AI enabled."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.provider import ai_provider
from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import AppError, NotFoundError
from app.db.session import get_db
from app.models import Attempt, Evaluation, PracticeItem, UsageEvent, User, UserSkill
from app.modules.practice.scheduler import compute_due_at, next_interval_days, result_from_score
from app.models import ReviewEvent, ReviewState, LearnerMemory
from app.services.analytics import track
from app.services.storage import object_storage

router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceSubmitIn(BaseModel):
    practice_item_id: uuid.UUID
    transcript: str = Field(min_length=1, max_length=50_000)
    confidence: float | None = Field(default=None, ge=0, le=1)
    duration_seconds: float | None = None


class VoiceResultOut(BaseModel):
    attempt_id: uuid.UUID
    evaluation_id: uuid.UUID
    transcript: str
    result_json: dict[str, Any]
    is_provisional: bool
    model_version: str


@router.get("/prompts")
def voice_prompts(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(PracticeItem).where(
            PracticeItem.is_curated.is_(True),
            PracticeItem.type.in_(["explain", "baseline", "recall", "voice"]),
        ).limit(20)
    ).all()
    return [
        {
            "id": str(r.id),
            "type": r.type,
            "prompt": r.prompt,
            "expected_minutes": r.expected_minutes,
            "competency_id": str(r.competency_id) if r.competency_id else None,
        }
        for r in rows
    ]


@router.post("/submit", response_model=VoiceResultOut)
def submit_voice_transcript(
    payload: VoiceSubmitIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VoiceResultOut:
    item = db.get(PracticeItem, payload.practice_item_id)
    if not item or (not item.is_curated and item.user_id != user.id):
        raise NotFoundError("Practice item not found")

    attempt = Attempt(
        user_id=user.id,
        practice_item_id=item.id,
        response_text=payload.transcript,
        confidence=payload.confidence,
        status="submitted",
        submitted_at=datetime.now(UTC),
        hint_used=False,
    )
    db.add(attempt)
    db.flush()

    keywords = (item.metadata_json or {}).get("expected_keywords") or []
    result = ai_provider.evaluate_response(
        prompt=item.prompt,
        response=payload.transcript,
        rubric=item.rubric_json or {},
        expected_keywords=keywords,
    )
    result["modality"] = "voice"
    if payload.duration_seconds is not None:
        result["duration_seconds"] = payload.duration_seconds

    evaluation = Evaluation(
        attempt_id=attempt.id,
        rubric_version=item.rubric_version,
        result_json=result,
        model_version=result.get("model_version", "deterministic-eval-v1"),
        prompt_version=result.get("prompt_version", "voice-v1"),
        confidence=1.0 - float(result.get("uncertainty", 0.3)),
        is_provisional=True,
    )
    db.add(evaluation)

    if item.competency_id:
        skill = db.scalar(
            select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.competency_id == item.competency_id)
        )
        if skill:
            suggested = result.get("status_suggestion", "developing")
            if suggested == "demonstrated" and skill.evidence_count < 1:
                skill.status = "developing"
            elif suggested in {"emerging", "developing", "demonstrated", "needs_review"}:
                skill.status = suggested
            skill.evidence_count += 1
            skill.last_attempt_at = attempt.submitted_at

    sched = result_from_score(float(result.get("overall_score") or 0))
    state = db.scalar(
        select(ReviewState).where(ReviewState.user_id == user.id, ReviewState.practice_item_id == item.id)
    )
    if not state:
        state = ReviewState(
            user_id=user.id,
            practice_item_id=item.id,
            due_at=datetime.now(UTC),
            stability=1.0,
            difficulty=0.3,
            reps=0,
        )
        db.add(state)
        db.flush()
    new_s, new_d, interval = next_interval_days(
        result=sched, stability=state.stability, difficulty=state.difficulty, reps=state.reps
    )
    state.stability, state.difficulty, state.reps = new_s, new_d, state.reps + 1
    state.last_result = sched
    state.due_at = compute_due_at(interval)
    db.add(ReviewEvent(user_id=user.id, practice_item_id=item.id, result=sched, confidence=payload.confidence))
    db.add(
        LearnerMemory(
            user_id=user.id,
            memory_type="episodic",
            content_json={"modality": "voice", "attempt_id": str(attempt.id), "score": result.get("overall_score")},
            provenance_json={"source": "voice_practice"},
            confidence=payload.confidence,
            status="active",
            competency_id=item.competency_id,
        )
    )
    db.add(UsageEvent(user_id=user.id, feature="voice_practice", units=1, cost_usd=0, metadata_json={}))
    track(db, user_id=user.id, event_name="voice_practice_submitted", properties={"attempt_id": str(attempt.id)})
    db.commit()
    db.refresh(evaluation)
    return VoiceResultOut(
        attempt_id=attempt.id,
        evaluation_id=evaluation.id,
        transcript=payload.transcript,
        result_json=result,
        is_provisional=evaluation.is_provisional,
        model_version=evaluation.model_version,
    )


@router.post("/upload")
async def upload_voice_audio(
    practice_item_id: str = Form(...),
    transcript: str = Form(...),
    confidence: float | None = Form(default=None),
    duration_seconds: float | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VoiceResultOut:
    """Store optional audio artefact, then evaluate transcript (browser STT or pasted text)."""
    settings = get_settings()
    object_key = None
    if file is not None:
        data = await file.read(settings.max_pdf_bytes)  # reuse size budget for audio
        if len(data) > 15 * 1024 * 1024:
            raise AppError("audio_too_large", "Audio exceeds 15MB limit", 400)
        object_key = f"users/{user.id}/voice/{uuid.uuid4().hex}.webm"
        object_storage.put_bytes(key=object_key, data=data, content_type=file.content_type or "audio/webm")

    # Optional server transcription path when AI enabled and no transcript provided
    final_transcript = transcript.strip()
    if not final_transcript and settings.ai_enabled and object_key:
        raise AppError(
            "transcript_required",
            "Provide a browser transcript for now. Server Whisper transcription can be enabled later.",
            400,
        )
    if not final_transcript:
        raise AppError("transcript_required", "Transcript is required for voice evaluation", 400)

    result = submit_voice_transcript(
        VoiceSubmitIn(
            practice_item_id=uuid.UUID(practice_item_id),
            transcript=final_transcript,
            confidence=confidence,
            duration_seconds=duration_seconds,
        ),
        user=user,
        db=db,
    )
    if object_key:
        # annotate attempt metadata via learner memory
        db.add(
            LearnerMemory(
                user_id=user.id,
                memory_type="episodic",
                content_json={"audio_object_key": object_key, "attempt_id": str(result.attempt_id)},
                provenance_json={"source": "voice_upload"},
                status="active",
            )
        )
        db.commit()
    return result
