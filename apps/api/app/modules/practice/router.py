from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.provider import ai_provider
from app.core.deps import get_current_user
from app.core.errors import AppError, NotFoundError
from app.db.session import get_db
from app.models import (
    Attempt,
    AttemptError,
    ErrorPattern,
    Evaluation,
    LearnerMemory,
    PracticeItem,
    ReviewEvent,
    ReviewState,
    UsageEvent,
    User,
    UserSkill,
)
from app.modules.practice.scheduler import compute_due_at, next_interval_days, result_from_score
from app.schemas.common import (
    AttemptCreateIn,
    AttemptOut,
    AttemptSubmitIn,
    EvaluationOut,
    PracticeItemOut,
)
from app.services.analytics import track


class ChallengeIn(BaseModel):
    reason: str = Field(min_length=10, max_length=4000)

router = APIRouter(tags=["practice"])


@router.get("/practice-items", response_model=list[PracticeItemOut])
def list_practice_items(
    type: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PracticeItemOut]:
    q = select(PracticeItem).where(
        (PracticeItem.is_curated.is_(True)) | (PracticeItem.user_id == user.id)
    )
    if type:
        q = q.where(PracticeItem.type == type)
    rows = db.scalars(q.order_by(PracticeItem.created_at.desc()).limit(50)).all()
    return [PracticeItemOut.model_validate(r) for r in rows]


@router.get("/practice-items/{item_id}", response_model=PracticeItemOut)
def get_practice_item(
    item_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> PracticeItemOut:
    item = db.get(PracticeItem, item_id)
    if not item or (not item.is_curated and item.user_id != user.id):
        raise NotFoundError("Practice item not found")
    return PracticeItemOut.model_validate(item)


@router.get("/reviews/due", response_model=list[PracticeItemOut])
def due_reviews(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PracticeItemOut]:
    now = datetime.now(UTC)
    states = db.scalars(
        select(ReviewState).where(ReviewState.user_id == user.id, ReviewState.due_at <= now).order_by(ReviewState.due_at)
    ).all()
    items: list[PracticeItemOut] = []
    for state in states:
        item = db.get(PracticeItem, state.practice_item_id)
        if item:
            items.append(PracticeItemOut.model_validate(item))
    return items


@router.post("/assessments", response_model=AttemptOut)
def create_attempt(
    payload: AttemptCreateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AttemptOut:
    item = db.get(PracticeItem, payload.practice_item_id)
    if not item or (not item.is_curated and item.user_id != user.id):
        raise NotFoundError("Practice item not found")

    if payload.idempotency_key:
        existing = db.scalar(
            select(Attempt).where(Attempt.user_id == user.id, Attempt.idempotency_key == payload.idempotency_key)
        )
        if existing:
            return AttemptOut.model_validate(existing)

    attempt = Attempt(
        user_id=user.id,
        practice_item_id=item.id,
        status="in_progress",
        idempotency_key=payload.idempotency_key,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return AttemptOut.model_validate(attempt)


@router.post("/assessments/{attempt_id}/submit", response_model=EvaluationOut)
def submit_attempt(
    attempt_id: UUID,
    payload: AttemptSubmitIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationOut:
    attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user.id))
    if not attempt:
        raise NotFoundError("Attempt not found")
    if attempt.status == "submitted":
        evaluation = db.scalar(select(Evaluation).where(Evaluation.attempt_id == attempt.id))
        if evaluation:
            return EvaluationOut.model_validate(evaluation)
        raise AppError("evaluation_pending", "Evaluation still pending", 202)

    item = db.get(PracticeItem, attempt.practice_item_id)
    if not item:
        raise NotFoundError("Practice item missing")

    # Preserve response first — never lose user work if eval fails.
    attempt.response_text = payload.response_text
    attempt.confidence = payload.confidence
    attempt.hint_used = payload.hint_used
    attempt.status = "submitted"
    attempt.submitted_at = datetime.now(UTC)
    db.flush()

    keywords = (item.metadata_json or {}).get("expected_keywords") or []
    result = ai_provider.evaluate_response(
        prompt=item.prompt,
        response=payload.response_text,
        rubric=item.rubric_json or {},
        expected_keywords=keywords,
    )

    evaluation = Evaluation(
        attempt_id=attempt.id,
        rubric_version=item.rubric_version,
        result_json=result,
        model_version=result.get("model_version", "deterministic-eval-v1"),
        prompt_version=result.get("prompt_version", "none"),
        confidence=1.0 - float(result.get("uncertainty", 0.3)),
        is_provisional=bool(result.get("is_provisional", True)),
    )
    db.add(evaluation)

    # Update skill status with deterministic rules (AI suggestion is advisory).
    if item.competency_id:
        skill = db.scalar(
            select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.competency_id == item.competency_id)
        )
        if skill:
            suggested = result.get("status_suggestion", "developing")
            if suggested in {"emerging", "developing", "demonstrated", "needs_review"}:
                # Don't jump to demonstrated from a single provisional score without prior evidence.
                if suggested == "demonstrated" and skill.evidence_count < 1:
                    skill.status = "developing"
                else:
                    skill.status = suggested
            skill.evidence_count += 1
            skill.last_attempt_at = attempt.submitted_at
            skill.confidence = payload.confidence

    for err in result.get("errors") or []:
        pattern = db.scalar(
            select(ErrorPattern).where(
                ErrorPattern.user_id == user.id,
                ErrorPattern.error_code == err.get("error_code", "unknown"),
                ErrorPattern.competency_id == item.competency_id,
            )
        )
        if pattern:
            pattern.recurrence_count += 1
            pattern.description = err.get("description", pattern.description)
        else:
            pattern = ErrorPattern(
                user_id=user.id,
                competency_id=item.competency_id,
                error_code=err.get("error_code", "unknown"),
                description=err.get("description", "Unclassified error"),
                severity=err.get("severity", "medium"),
            )
            db.add(pattern)
            db.flush()
        db.add(AttemptError(attempt_id=attempt.id, error_pattern_id=pattern.id, evidence_json={"quote": result.get("evidence_quotes", [])[:1]}))
        db.add(
            LearnerMemory(
                user_id=user.id,
                memory_type="error",
                content_json={"error_code": pattern.error_code, "description": pattern.description},
                provenance_json={"attempt_id": str(attempt.id), "evaluation": True},
                confidence=0.7,
                status="active",
                competency_id=item.competency_id,
            )
        )

    db.add(
        LearnerMemory(
            user_id=user.id,
            memory_type="episodic",
            content_json={
                "attempt_id": str(attempt.id),
                "practice_item_id": str(item.id),
                "overall_score": result.get("overall_score"),
                "summary": (payload.response_text[:200]),
            },
            provenance_json={"source": "attempt_submission"},
            confidence=payload.confidence,
            status="active",
            competency_id=item.competency_id,
        )
    )

    # Schedule next review.
    score = float(result.get("overall_score") or 0)
    sched_result = result_from_score(score)
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
        result=sched_result, stability=state.stability, difficulty=state.difficulty, reps=state.reps
    )
    state.stability = new_s
    state.difficulty = new_d
    state.reps += 1
    state.last_result = sched_result
    state.due_at = compute_due_at(interval)
    state.version += 1

    db.add(
        ReviewEvent(
            user_id=user.id,
            practice_item_id=item.id,
            result=sched_result,
            confidence=payload.confidence,
            occurred_at=datetime.now(UTC),
        )
    )
    db.add(UsageEvent(user_id=user.id, feature="assessment_evaluation", units=1, cost_usd=0, metadata_json={}))
    track(db, user_id=user.id, event_name="practice_submitted", properties={"attempt_id": str(attempt.id)})
    db.commit()
    db.refresh(evaluation)
    return EvaluationOut.model_validate(evaluation)


@router.get("/assessments/{attempt_id}/result", response_model=EvaluationOut)
def get_result(
    attempt_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> EvaluationOut:
    attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user.id))
    if not attempt:
        raise NotFoundError("Attempt not found")
    evaluation = db.scalar(select(Evaluation).where(Evaluation.attempt_id == attempt.id))
    if not evaluation:
        raise NotFoundError("Evaluation not ready")
    return EvaluationOut.model_validate(evaluation)


@router.post("/evaluations/{evaluation_id}/challenge", response_model=EvaluationOut)
def challenge_evaluation(
    evaluation_id: UUID,
    payload: ChallengeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationOut:
    evaluation = db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise NotFoundError("Evaluation not found")
    attempt = db.scalar(select(Attempt).where(Attempt.id == evaluation.attempt_id, Attempt.user_id == user.id))
    if not attempt:
        raise NotFoundError("Evaluation not found")
    if evaluation.challenge_status == "challenged":
        return EvaluationOut.model_validate(evaluation)
    evaluation.challenge_status = "challenged"
    evaluation.challenge_reason = payload.reason
    evaluation.challenged_at = datetime.now(UTC)
    track(
        db,
        user_id=user.id,
        event_name="evaluation_challenged",
        properties={"evaluation_id": str(evaluation.id)},
    )
    db.commit()
    db.refresh(evaluation)
    return EvaluationOut.model_validate(evaluation)
