"""Smoke tests for Skill Passport + extension token helpers."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import jwt

from app.core.config import get_settings
from app.core.security import safe_decode_token


def test_extension_token_roundtrip_scope():
    settings = get_settings()
    user_id = str(uuid4())
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": user_id,
            "email": "learner@example.com",
            "scope": "extension",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=90)).timestamp()),
        },
        settings.session_secret,
        algorithm="HS256",
    )
    payload = safe_decode_token(token)
    assert payload is not None
    assert payload["scope"] == "extension"
    assert payload["sub"] == user_id


def test_passport_module_importable():
    from app.modules.passport.router import get_passport
    from app.modules.voice.router import voice_prompts
    from app.modules.extension.router import capture_from_extension

    assert callable(get_passport)
    assert callable(voice_prompts)
    assert callable(capture_from_extension)
