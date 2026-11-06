from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    message: str


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: UUID
    email: EmailStr
    plan: str
    status: str
    onboarding_completed_at: datetime | None
    email_verified_at: datetime | None


class ProfileOut(ORMModel):
    display_name: str | None
    timezone: str
    role_target: str | None
    preferences_json: dict[str, Any]


class MeOut(BaseModel):
    user: UserOut
    profile: ProfileOut | None
    entitlements: dict[str, Any]


class OnboardingIn(BaseModel):
    display_name: str | None = None
    role_target: str = Field(min_length=2, max_length=120)
    skill_path_slug: str
    weekly_time_budget_minutes: int = Field(ge=30, le=1400, default=180)
    goal_title: str = Field(min_length=2, max_length=255)
    timezone: str = "UTC"


class SkillPathOut(ORMModel):
    id: UUID
    slug: str
    title: str
    description: str
    version: str


class CompetencyOut(ORMModel):
    id: UUID
    slug: str
    title: str
    definition: str
    parent_id: UUID | None
    sort_order: int


class UserSkillOut(ORMModel):
    id: UUID
    competency_id: UUID
    status: str
    confidence: float | None
    evidence_count: int
    last_attempt_at: datetime | None
    competency: CompetencyOut | None = None


class SourceCreateIn(BaseModel):
    type: str = Field(pattern="^(text|url|pdf)$")
    title: str = Field(min_length=1, max_length=500)
    text: str | None = None
    url: str | None = None
    idempotency_key: str | None = None


class ConceptOut(ORMModel):
    id: UUID
    title: str
    definition: str
    concept_type: str
    status: str
    confidence: float | None
    competency_id: UUID | None


class ApproveConceptsIn(BaseModel):
    concept_ids: list[UUID]
    reject_ids: list[UUID] = []


class PracticeItemOut(ORMModel):
    id: UUID
    type: str
    prompt: str
    difficulty: str
    expected_minutes: int
    competency_id: UUID | None
    rubric_version: str


class AttemptCreateIn(BaseModel):
    practice_item_id: UUID
    idempotency_key: str | None = None


class AttemptSubmitIn(BaseModel):
    response_text: str = Field(min_length=1, max_length=50_000)
    confidence: float | None = Field(default=None, ge=0, le=1)
    hint_used: bool = False


class AttemptOut(ORMModel):
    id: UUID
    practice_item_id: UUID
    status: str
    response_text: str | None
    confidence: float | None
    submitted_at: datetime | None


class EvaluationOut(ORMModel):
    id: UUID
    attempt_id: UUID
    rubric_version: str
    result_json: dict[str, Any]
    model_version: str
    confidence: float | None
    is_provisional: bool
    challenge_status: str = "none"
    challenge_reason: str | None = None


class RecommendationOut(BaseModel):
    action_type: str
    title: str
    reason: str
    estimated_minutes: int
    practice_item_id: UUID | None = None
    skill_gap: str | None = None
    href: str


class MemoryOut(ORMModel):
    id: UUID
    memory_type: str
    content_json: dict[str, Any]
    provenance_json: dict[str, Any]
    confidence: float | None
    status: str
    created_at: datetime


class ProgressOut(BaseModel):
    attempts_count: int
    evaluations_count: int
    concepts_approved: int
    error_patterns: int
    skills: list[UserSkillOut]
    recent_attempts: list[dict[str, Any]]
