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
    SandboxRun,
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
from app.services.sandbox import SandboxError, run_python_tests


class ChallengeIn(BaseModel):
    reason: str = Field(min_length=10, max_length=4000)


class ImplementSubmitIn(BaseModel):
    code: str = Field(min_length=1, max_length=80_000)
    confidence: float | None = Field(default=None, ge=0, le=1)
    idempotency_key: str | None = None


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

    # Adaptive schedule next review.
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
            consecutive_fails=0,
            remediation_mode="standard",
        )
        db.add(state)
        db.flush()
    new_s, new_d, interval, fails, remediation = next_interval_days(
        result=sched_result,
        stability=state.stability,
        difficulty=state.difficulty,
        reps=state.reps,
        consecutive_fails=state.consecutive_fails,
    )
    state.stability = new_s
    state.difficulty = new_d
    state.reps += 1
    state.consecutive_fails = fails
    state.remediation_mode = remediation
    state.last_result = sched_result
    state.due_at = compute_due_at(interval)
    state.version += 1
    result["remediation_mode"] = remediation
    result["consecutive_fails"] = fails
    evaluation.result_json = result

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


@router.post("/practice-items/{item_id}/implement")
def submit_implement(
    item_id: UUID,
    payload: ImplementSubmitIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Run curated implement-task code in the restricted sandbox and record evidence."""
    item = db.get(PracticeItem, item_id)
    if not item or (not item.is_curated and item.user_id != user.id):
        raise NotFoundError("Practice item not found")
    if item.type != "implement":
        raise AppError("not_implement", "This practice item is not an implement task", 400)

    meta = item.metadata_json or {}
    tests = meta.get("tests") or []
    if not tests:
        raise AppError("no_tests", "Implement task has no sandbox tests configured", 500)

    if payload.idempotency_key:
        existing = db.scalar(
            select(Attempt).where(Attempt.user_id == user.id, Attempt.idempotency_key == payload.idempotency_key)
        )
        if existing:
            evaluation = db.scalar(select(Evaluation).where(Evaluation.attempt_id == existing.id))
            run = db.scalar(select(SandboxRun).where(SandboxRun.attempt_id == existing.id))
            return {
                "attempt_id": str(existing.id),
                "evaluation_id": str(evaluation.id) if evaluation else None,
                "sandbox": run.result_json if run else {},
            }

    attempt = Attempt(
        user_id=user.id,
        practice_item_id=item.id,
        response_text=payload.code,
        confidence=payload.confidence,
        status="submitted",
        submitted_at=datetime.now(UTC),
        idempotency_key=payload.idempotency_key,
    )
    db.add(attempt)
    db.flush()

    run = SandboxRun(
        user_id=user.id,
        attempt_id=attempt.id,
        practice_item_id=item.id,
        language=meta.get("language", "python"),
        status="running",
    )
    db.add(run)
    db.flush()

    try:
        sandbox_result = run_python_tests(user_code=payload.code, tests=tests)
        run.status = "passed" if sandbox_result["passed"] else "failed"
        run.stdout = sandbox_result.get("stdout")
        run.stderr = sandbox_result.get("stderr")
        run.exit_code = sandbox_result.get("exit_code")
        run.tests_passed = sandbox_result.get("tests_passed", 0)
        run.tests_total = sandbox_result.get("tests_total", 0)
        run.result_json = sandbox_result
    except SandboxError as exc:
        run.status = "error"
        run.stderr = exc.message
        run.result_json = {"error": exc.code, "message": exc.message}
        sandbox_result = {"passed": False, "tests_passed": 0, "tests_total": len(tests), "error": exc.code}

    # Map sandbox outcome onto rubric-ish score for scheduler / passport.
    ratio = (sandbox_result.get("tests_passed") or 0) / max(1, sandbox_result.get("tests_total") or 1)
    overall = round(ratio * 5, 2)
    result = {
        "overall_score": overall,
        "overall_max": 5,
        "uncertainty": 0.15 if sandbox_result.get("passed") else 0.35,
        "is_provisional": False,
        "model_version": "sandbox-v1",
        "prompt_version": "implement-v1",
        "status_suggestion": "demonstrated" if sandbox_result.get("passed") else "needs_review",
        "summary": (
            f"Sandbox: {sandbox_result.get('tests_passed', 0)}/{sandbox_result.get('tests_total', 0)} tests passed."
        ),
        "sandbox": sandbox_result,
        "evidence_quotes": [],
        "errors": []
        if sandbox_result.get("passed")
        else [{"error_code": "sandbox_fail", "description": "One or more sandbox tests failed", "severity": "medium"}],
    }

    evaluation = Evaluation(
        attempt_id=attempt.id,
        rubric_version=item.rubric_version,
        result_json=result,
        model_version="sandbox-v1",
        prompt_version="implement-v1",
        confidence=1.0 - float(result["uncertainty"]),
        is_provisional=False,
    )
    db.add(evaluation)

    if item.competency_id:
        skill = db.scalar(
            select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.competency_id == item.competency_id)
        )
        if skill:
            if sandbox_result.get("passed") and skill.evidence_count >= 1:
                skill.status = "demonstrated"
            elif sandbox_result.get("passed"):
                skill.status = "developing"
            else:
                skill.status = "needs_review"
            skill.evidence_count += 1
            skill.last_attempt_at = attempt.submitted_at

    sched_result = result_from_score(overall)
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
    new_s, new_d, interval, fails, remediation = next_interval_days(
        result=sched_result,
        stability=state.stability,
        difficulty=state.difficulty,
        reps=state.reps,
        consecutive_fails=getattr(state, "consecutive_fails", 0) or 0,
    )
    state.stability, state.difficulty = new_s, new_d
    state.reps += 1
    state.consecutive_fails = fails
    state.remediation_mode = remediation
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
    db.add(
        LearnerMemory(
            user_id=user.id,
            memory_type="procedural",
            content_json={
                "modality": "implement",
                "attempt_id": str(attempt.id),
                "passed": bool(sandbox_result.get("passed")),
                "tests_passed": sandbox_result.get("tests_passed"),
            },
            provenance_json={"source": "sandbox"},
            confidence=payload.confidence,
            status="active",
            competency_id=item.competency_id,
        )
    )
    db.add(UsageEvent(user_id=user.id, feature="sandbox_implement", units=1, cost_usd=0, metadata_json={}))
    track(db, user_id=user.id, event_name="implement_submitted", properties={"attempt_id": str(attempt.id)})
    db.commit()
    db.refresh(evaluation)
    return {
        "attempt_id": str(attempt.id),
        "evaluation_id": str(evaluation.id),
        "sandbox": sandbox_result,
        "result_json": result,
        "remediation_mode": remediation,
    }
