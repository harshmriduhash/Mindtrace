"""IDOR / ownership boundary tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db
client = TestClient(fastapi_app)


def _signup(email: str) -> None:
    res = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "display_name": "T"},
    )
    assert res.status_code == 200, res.text


def test_user_cannot_read_other_users_source():
    _signup(f"a-{uuid.uuid4().hex[:8]}@example.com")
    create = client.post(
        "/api/v1/sources",
        json={"type": "text", "title": "mine", "text": "Cache-aside loads on miss and stores data."},
    )
    assert create.status_code == 202, create.text
    source_id = create.json()["id"]

    client.post("/api/v1/auth/logout")
    _signup(f"b-{uuid.uuid4().hex[:8]}@example.com")
    other = client.get(f"/api/v1/sources/{source_id}")
    assert other.status_code == 404


def test_user_cannot_read_other_users_memory_by_guessing():
    _signup(f"c-{uuid.uuid4().hex[:8]}@example.com")
    fake_id = str(uuid.uuid4())
    res = client.delete(f"/api/v1/memory/{fake_id}")
    assert res.status_code == 404
