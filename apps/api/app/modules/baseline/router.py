"""Multi-item baseline with balanced competency sampling and pause/resume."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
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
    BaselineSession,
    Competency,
    Evaluation,
    Goal,
    PracticeItem,
    SkillPath,
    User,
    UserSkill,
)
from app.modules.practice.scheduler import compute_due_at, next_interval_days, result_from_score
from app.models import ReviewEvent, ReviewState, UsageEvent, ErrorPattern, AttemptError, LearnerMemory
from app.services.analytics import track

router = APIRouter(prefix="/baselines", tags=["baselines"])


class BaselineOut(BaseModel):
    id: UUID
    status: str
    current_index: int
    total_items: int
    current_item: dict[str, Any] | None
    completed_item_ids: list[str]
    summary: dict[str, Any]


class BaselineSubmitIn(BaseModel):
    response_text: str = Field(min_length=1, max_length=50_000)
    confidence: float | None = Field(default=None, ge=0, le=1)


def _select_balanced_items(db: Session, path_id: UUID, limit: int = 4) -> list[PracticeItem]:
    comps = db.scalars(
        select(Competency).where(Competency.path_id == path_id).order_by(Competency.sort_order)
    ).all()
    selected: list[PracticeItem] = []
    used_comp: set[UUID] = set()
    for comp in comps:
        item = db.scalar(
            select(PracticeItem).where(
                PracticeItem.is_curated.is_(True),
                PracticeItem.competency_id == comp.id,
                PracticeItem.type.in_(["baseline", "explain", "design", "diagnose", "recall"]),
            ).limit(1)
        )
        if item and comp.id not in used_comp:
            selected.append(item)
            used_comp.add(comp.id)
        if len(selected) >= limit:
            break
    if len(selected) < 2:
        fallback = db.scalars(
            select(PracticeItem).where(PracticeItem.is_curated.is_(True), PracticeItem.type == "baseline").limit(limit)
        ).all()
        selected = list(fallback)
    return selected


def _serialize(db: Session, session: BaselineSession) -> BaselineOut:
    item_ids = [UUID(x) for x in (session.item_ids_json or [])]
    completed: list[str] = []
    for iid in item_ids[: session.current_index]:
        completed.append(str(iid))
    current_item = None
    if session.status in {"in_progress", "paused"} and session.current_index < len(item_ids):
        item = db.get(PracticeItem, item_ids[session.current_index])
        if item:
            current_item = {
                "id": str(item.id),
                "type": item.type,
                "prompt": item.prompt,
                "expected_minutes": item.expected_minutes,
                "difficulty": item.difficulty,
                "competency_id": str(item.competency_id) if item.competency_id else None,
            }
    return BaselineOut(
        id=session.id,
        status=session.status,
        current_index=session.current_index,
        total_items=len(item_ids),
        current_item=current_item,
        completed_item_ids=completed,
        summary=session.summary_json or {},
    )


@router.post("/start", response_model=BaselineOut)
def start_baseline(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BaselineOut:
    existing = db.scalar(
        select(BaselineSession).where(
            BaselineSession.user_id == user.id,
            BaselineSession.status.in_(["in_progress", "paused"]),
        ).order_by(BaselineSession.created_at.desc())
    )
    if existing:
        return _serialize(db, existing)

    goal = db.scalar(select(Goal).where(Goal.user_id == user.id, Goal.status == "active"))
    path_id = goal.skill_path_id if goal else None
    if not path_id:
        path = db.scalar(select(SkillPath).where(SkillPath.is_active.is_(True)).limit(1))
        path_id = path.id if path else None
    if not path_id:
        raise AppError("no_skill_path", "No skill path available for baseline", 400)

    items = _select_balanced_items(db, path_id, limit=4)
    if not items:
        raise AppError("no_items", "No baseline practice items seeded", 400)

    session = BaselineSession(
        user_id=user.id,
        skill_path_id=path_id,
        status="in_progress",
        current_index=0,
        item_ids_json=[str(i.id) for i in items],
        summary_json={"scores": []},
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    track(db, user_id=user.id, event_name="baseline_started", properties={"session_id": str(session.id)})
    db.commit()
    return _serialize(db, session)


@router.get("/active", response_model=BaselineOut | None)
def active_baseline(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BaselineOut | None:
    session = db.scalar(
        select(BaselineSession).where(
            BaselineSession.user_id == user.id,
            BaselineSession.status.in_(["in_progress", "paused", "completed"]),
        ).order_by(BaselineSession.created_at.desc())
    )
    return _serialize(db, session) if session else None


@router.get("/{session_id}", response_model=BaselineOut)
def get_baseline(
    session_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> BaselineOut:
    session = db.scalar(
        select(BaselineSession).where(BaselineSession.id == session_id, BaselineSession.user_id == user.id)
    )
    if not session:
        raise NotFoundError("Baseline session not found")
    return _serialize(db, session)


@router.post("/{session_id}/pause", response_model=BaselineOut)
def pause_baseline(
    session_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> BaselineOut:
    session = db.scalar(
        select(BaselineSession).where(BaselineSession.id == session_id, BaselineSession.user_id == user.id)
    )
    if not session:
        raise NotFoundError("Baseline session not found")
    if session.status != "in_progress":
        raise AppError("invalid_state", "Only in-progress baselines can be paused", 400)
    session.status = "paused"
    session.paused_at = datetime.now(UTC)
    db.commit()
    db.refresh(session)
    return _serialize(db, session)


@router.post("/{session_id}/resume", response_model=BaselineOut)
def resume_baseline(
    session_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> BaselineOut:
    session = db.scalar(
        select(BaselineSession).where(BaselineSession.id == session_id, BaselineSession.user_id == user.id)
    )
    if not session:
        raise NotFoundError("Baseline session not found")
    if session.status != "paused":
        raise AppError("invalid_state", "Only paused baselines can be resumed", 400)
    session.status = "in_progress"
    session.paused_at = None
    db.commit()
    db.refresh(session)
    return _serialize(db, session)


@router.post("/{session_id}/submit", response_model=BaselineOut)
def submit_baseline_item(
    session_id: UUID,
    payload: BaselineSubmitIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BaselineOut:
    session = db.scalar(
        select(BaselineSession).where(BaselineSession.id == session_id, BaselineSession.user_id == user.id)
    )
    if not session:
        raise NotFoundError("Baseline session not found")
    if session.status not in {"in_progress"}:
        raise AppError("invalid_state", "Baseline is not accepting answers", 400)

    item_ids = [UUID(x) for x in (session.item_ids_json or [])]
    if session.current_index >= len(item_ids):
        raise AppError("complete", "Baseline already complete", 400)

    item = db.get(PracticeItem, item_ids[session.current_index])
    if not item:
        raise NotFoundError("Practice item missing")

    attempt = Attempt(
        user_id=user.id,
        practice_item_id=item.id,
        response_text=payload.response_text,
        confidence=payload.confidence,
        status="submitted",
        submitted_at=datetime.now(UTC),
    )
    db.add(attempt)
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

    scores = list((session.summary_json or {}).get("scores") or [])
    scores.append(
        {
            "practice_item_id": str(item.id),
            "attempt_id": str(attempt.id),
            "evaluation_id": str(evaluation.id),
            "overall_score": result.get("overall_score"),
            "competency_id": str(item.competency_id) if item.competency_id else None,
        }
    )
    session.summary_json = {**(session.summary_json or {}), "scores": scores}
    session.current_index += 1

    if session.current_index >= len(item_ids):
        session.status = "completed"
        session.completed_at = datetime.now(UTC)
        avg = sum(float(s.get("overall_score") or 0) for s in scores) / max(len(scores), 1)
        session.summary_json = {
            **session.summary_json,
            "average_score": round(avg, 2),
            "uncertainty_note": "Baseline scores are provisional coaching signals with uncertainty.",
        }
        track(db, user_id=user.id, event_name="baseline_completed", properties={"session_id": str(session.id)})

    # Schedule review for this item
    sched_result = result_from_score(float(result.get("overall_score") or 0))
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
    state.stability, state.difficulty, state.reps = new_s, new_d, state.reps + 1
    state.last_result = sched_result
    state.due_at = compute_due_at(interval)
    db.add(ReviewEvent(user_id=user.id, practice_item_id=item.id, result=sched_result, confidence=payload.confidence))
    db.add(UsageEvent(user_id=user.id, feature="assessment_evaluation", units=1, cost_usd=0, metadata_json={}))

    for err in result.get("errors") or []:
        pattern = ErrorPattern(
            user_id=user.id,
            competency_id=item.competency_id,
            error_code=err.get("error_code", "unknown"),
            description=err.get("description", "Unclassified"),
            severity=err.get("severity", "medium"),
        )
        db.add(pattern)
        db.flush()
        db.add(AttemptError(attempt_id=attempt.id, error_pattern_id=pattern.id, evidence_json={}))
        db.add(
            LearnerMemory(
                user_id=user.id,
                memory_type="error",
                content_json={"error_code": pattern.error_code, "description": pattern.description},
                provenance_json={"baseline_session_id": str(session.id)},
                confidence=0.7,
                status="active",
                competency_id=item.competency_id,
            )
        )

    db.commit()
    db.refresh(session)
    return _serialize(db, session)
