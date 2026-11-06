"""GitHub project evidence — user-approved repo links as skill evidence."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import AppError, NotFoundError
from app.db.session import get_db
from app.models import LearnerMemory, ProjectEvidence, User, UserSkill
from app.services.analytics import track

router = APIRouter(prefix="/projects", tags=["projects"])


class LinkRepoIn(BaseModel):
    repo_url: str = Field(min_length=8, max_length=500)
    competency_id: UUID | None = None
    summary: str = Field(default="", max_length=2000)


def _parse_repo(url: str) -> str:
    cleaned = url.strip().rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    parts = cleaned.replace("https://", "").replace("http://", "").split("/")
    if "github.com" not in parts[0]:
        raise AppError("invalid_repo", "Only public GitHub repositories are supported", 400)
    if len(parts) < 3:
        raise AppError("invalid_repo", "Expected https://github.com/owner/repo", 400)
    return f"{parts[1]}/{parts[2]}"


@router.get("")
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(ProjectEvidence).where(ProjectEvidence.user_id == user.id, ProjectEvidence.status == "active")
    ).all()
    return [
        {
            "id": str(r.id),
            "repo_full_name": r.repo_full_name,
            "repo_url": r.repo_url,
            "summary": r.summary,
            "languages": r.languages_json,
            "competency_id": str(r.competency_id) if r.competency_id else None,
            "user_approved": r.user_approved,
        }
        for r in rows
    ]


@router.post("")
def link_project(
    payload: LinkRepoIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    full_name = _parse_repo(payload.repo_url)
    existing = db.scalar(
        select(ProjectEvidence).where(ProjectEvidence.user_id == user.id, ProjectEvidence.repo_full_name == full_name)
    )
    if existing and existing.status == "active":
        raise AppError("already_linked", "Repository already linked", 409)

    with httpx.Client(timeout=20.0, headers={"Accept": "application/vnd.github+json", "User-Agent": "Mindtrace"}) as client:
        repo_resp = client.get(f"https://api.github.com/repos/{full_name}")
        if repo_resp.status_code == 404:
            raise AppError("repo_not_found", "GitHub repository not found or private", 404)
        if repo_resp.status_code >= 400:
            raise AppError("github_error", "GitHub API error", 502)
        repo = repo_resp.json()
        langs_resp = client.get(f"https://api.github.com/repos/{full_name}/languages")
        languages = langs_resp.json() if langs_resp.status_code < 400 else {}

    if existing:
        row = existing
        row.status = "active"
        row.summary = payload.summary or repo.get("description") or row.summary
        row.languages_json = languages
        row.competency_id = payload.competency_id
        row.user_approved = True
        row.metadata_json = {
            "stars": repo.get("stargazers_count"),
            "forks": repo.get("forks_count"),
            "language": repo.get("language"),
            "topics": repo.get("topics") or [],
        }
    else:
        row = ProjectEvidence(
            user_id=user.id,
            provider="github",
            repo_full_name=full_name,
            repo_url=repo.get("html_url") or f"https://github.com/{full_name}",
            competency_id=payload.competency_id,
            summary=payload.summary or repo.get("description") or "",
            languages_json=languages,
            metadata_json={
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "language": repo.get("language"),
                "topics": repo.get("topics") or [],
            },
            status="active",
            user_approved=True,
        )
        db.add(row)

    if payload.competency_id:
        skill = db.scalar(
            select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.competency_id == payload.competency_id)
        )
        if skill:
            skill.evidence_count += 1
            if skill.status == "not_assessed":
                skill.status = "emerging"

    db.add(
        LearnerMemory(
            user_id=user.id,
            memory_type="progress",
            content_json={"kind": "github_project", "repo": full_name, "summary": row.summary},
            provenance_json={"source": "github", "user_approved": True},
            confidence=0.6,
            status="active",
            competency_id=payload.competency_id,
        )
    )
    track(db, user_id=user.id, event_name="project_linked", properties={"repo": full_name})
    db.commit()
    db.refresh(row)
    return {"id": str(row.id), "repo_full_name": row.repo_full_name, "languages": row.languages_json}


@router.delete("/{project_id}")
def unlink_project(
    project_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict[str, str]:
    row = db.scalar(
        select(ProjectEvidence).where(ProjectEvidence.id == project_id, ProjectEvidence.user_id == user.id)
    )
    if not row:
        raise NotFoundError("Project evidence not found")
    row.status = "deleted"
    db.commit()
    return {"status": "deleted"}
