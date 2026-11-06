from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))  # nullable for OAuth-only
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    plan: Mapped[str] = mapped_column(String(32), default="free", nullable=False)
    onboarding_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(64))  # TOTP secret (base32)
    mfa_recovery_codes_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    deletion_requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    profile: Mapped[Optional[Profile]] = relationship(back_populates="user", uselist=False)


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    role_target: Mapped[Optional[str]] = mapped_column(String(120))
    preferences_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_path_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("skill_paths.id"))
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    weekly_time_budget_minutes: Mapped[int] = mapped_column(Integer, default=180, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class SkillPath(Base, TimestampMixin):
    __tablename__ = "skill_paths"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    competencies: Mapped[list[Competency]] = relationship(back_populates="path")


class Competency(Base, TimestampMixin):
    __tablename__ = "competencies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    path_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skill_paths.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("competencies.id"))
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rubric_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    path: Mapped[SkillPath] = relationship(back_populates="competencies")

    __table_args__ = (UniqueConstraint("path_id", "slug", name="uq_competency_path_slug"),)


class UserSkill(Base, TimestampMixin):
    __tablename__ = "user_skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    competency_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competencies.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="not_assessed", nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    disputed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dispute_note: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("user_id", "competency_id", name="uq_user_skill"),
        Index("ix_user_skills_user_competency", "user_id", "competency_id"),
        CheckConstraint(
            "status IN ('not_assessed','emerging','developing','demonstrated','needs_review')",
            name="ck_user_skill_status",
        ),
    )


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # text | url | pdf | youtube
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_uri: Mapped[Optional[str]] = mapped_column(Text)
    object_key: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(String(128))
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(64))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class SourceSegment(Base, TimestampMixin):
    __tablename__ = "source_segments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text_ref: Mapped[str] = mapped_column(Text, nullable=False)
    page_or_timestamp: Mapped[Optional[str]] = mapped_column(String(64))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class Concept(Base, TimestampMixin):
    __tablename__ = "concepts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    concept_type: Mapped[str] = mapped_column(String(64), default="idea", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="proposed", nullable=False)
    competency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("competencies.id"))
    confidence: Mapped[Optional[float]] = mapped_column(Float)


class ConceptEdge(Base, TimestampMixin):
    __tablename__ = "concept_edges"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    from_concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    to_concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    relation: Mapped[str] = mapped_column(String(64), nullable=False)


class ConceptSource(Base):
    __tablename__ = "concept_sources"

    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True)
    source_segment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_segments.id", ondelete="CASCADE"), primary_key=True
    )
    relation: Mapped[str] = mapped_column(String(64), default="extracted_from", nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)


class PracticeItem(Base, TimestampMixin):
    __tablename__ = "practice_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    competency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("competencies.id"))
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("concepts.id"))
    skill_path_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("skill_paths.id"))
    type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # recall | explain | design | diagnose | implement | baseline | voice
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    rubric_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    expected_minutes: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    is_curated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    # implement tasks: metadata_json may include starter_code, tests[], language, remediation_of


class Attempt(Base, TimestampMixin):
    __tablename__ = "attempts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    practice_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_items.id"), nullable=False)
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="in_progress", nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128))

    __table_args__ = (
        Index("ix_attempts_user_created", "user_id", "created_at"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_attempt_idempotency"),
    )


class Evaluation(Base, TimestampMixin):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"), unique=True)
    rubric_version: Mapped[str] = mapped_column(String(32), nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), default="deterministic-v1", nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), default="none", nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    is_provisional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    challenge_status: Mapped[str] = mapped_column(String(32), default="none", nullable=False)
    challenge_reason: Mapped[Optional[str]] = mapped_column(Text)
    challenged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class BaselineSession(Base, TimestampMixin):
    __tablename__ = "baseline_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_path_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("skill_paths.id"))
    status: Mapped[str] = mapped_column(String(32), default="in_progress", nullable=False)
    current_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    item_ids_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(128))
    event_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    properties_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProductFeedback(Base, TimestampMixin):
    __tablename__ = "product_feedback"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    email: Mapped[Optional[str]] = mapped_column(String(320))
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)


class SkillDispute(Base, TimestampMixin):
    __tablename__ = "skill_disputes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_skills.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)


class LearnerMemory(Base, TimestampMixin):
    __tablename__ = "learner_memories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_type: Mapped[str] = mapped_column(String(32), nullable=False)  # semantic|episodic|procedural|error|progress
    content_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    provenance_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    competency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("competencies.id"))


class ErrorPattern(Base, TimestampMixin):
    __tablename__ = "error_patterns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("competencies.id"))
    error_code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    recurrence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class AttemptError(Base):
    __tablename__ = "attempt_errors"

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"), primary_key=True)
    error_pattern_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("error_patterns.id", ondelete="CASCADE"), primary_key=True
    )
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class ReviewState(Base, TimestampMixin):
    __tablename__ = "review_states"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    practice_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_items.id", ondelete="CASCADE"), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)
    last_result: Mapped[Optional[str]] = mapped_column(String(32))
    reps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consecutive_fails: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remediation_mode: Mapped[str] = mapped_column(String(32), default="standard", nullable=False)
    # standard | varied | tutor_first | implement
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "practice_item_id", name="uq_review_state"),
        Index("ix_review_due", "user_id", "due_at"),
    )


class ReviewEvent(Base, TimestampMixin):
    __tablename__ = "review_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    practice_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_items.id"), nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128))
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(64))

    __table_args__ = (UniqueConstraint("user_id", "idempotency_key", name="uq_job_idempotency"),)


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), default="stripe", nullable=False)
    provider_customer_id: Mapped[Optional[str]] = mapped_column(String(128))
    provider_subscription_id: Mapped[Optional[str]] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="none", nullable=False)
    plan_id: Mapped[str] = mapped_column(String(64), default="free", nullable=False)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    feature: Mapped[str] = mapped_column(String(64), nullable=False)
    units: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(128))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # google | github
    provider_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(320))
    access_token_enc: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text)
    scopes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("provider", "provider_subject", name="uq_oauth_provider_subject"),)


class ProjectEvidence(Base, TimestampMixin):
    __tablename__ = "project_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), default="github", nullable=False)
    repo_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    repo_url: Mapped[str] = mapped_column(Text, nullable=False)
    competency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("competencies.id"))
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    languages_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    user_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "repo_full_name", name="uq_user_repo"),)


class CalendarConnection(Base, TimestampMixin):
    __tablename__ = "calendar_connections"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), default="ics", nullable=False)  # ics | google
    feed_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    google_refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class SandboxRun(Base, TimestampMixin):
    __tablename__ = "sandbox_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("attempts.id", ondelete="SET NULL"))
    practice_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_items.id"), nullable=False)
    language: Mapped[str] = mapped_column(String(32), default="python", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    stdout: Mapped[Optional[str]] = mapped_column(Text)
    stderr: Mapped[Optional[str]] = mapped_column(Text)
    exit_code: Mapped[Optional[int]] = mapped_column(Integer)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tests_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
