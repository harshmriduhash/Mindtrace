from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.core.security import safe_decode_token
from app.db.session import get_db
from app.models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    settings = get_settings()
    token = request.cookies.get(settings.cookie_name)
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
    if not token:
        raise UnauthorizedError()

    payload = safe_decode_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError("Invalid or expired session")

    user = db.get(User, UUID(payload["sub"]))
    if not user or user.status != "active":
        raise UnauthorizedError("Account unavailable")
    return user
