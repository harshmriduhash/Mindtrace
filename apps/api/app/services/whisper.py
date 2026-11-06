"""Server-side speech-to-text via OpenAI Whisper when AI is enabled."""

from __future__ import annotations

import io
from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError


def transcribe_audio(*, data: bytes, filename: str = "audio.webm", content_type: str = "audio/webm") -> dict[str, Any]:
    settings = get_settings()
    if not settings.ai_enabled or not settings.openai_api_key:
        raise AppError(
            "whisper_unavailable",
            "Server STT requires AI_ENABLED=true and OPENAI_API_KEY",
            503,
        )
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise AppError("whisper_unavailable", "openai package not installed", 503) from exc

    client = OpenAI(api_key=settings.openai_api_key)
    bio = io.BytesIO(data)
    bio.name = filename
    try:
        result = client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=bio,
        )
    except Exception as exc:  # noqa: BLE001
        raise AppError("whisper_failed", f"Transcription failed: {exc}", 502) from exc

    text = getattr(result, "text", None) or (result.get("text") if isinstance(result, dict) else None)
    if not text:
        raise AppError("empty_transcript", "Whisper returned an empty transcript", 422)
    return {"transcript": text, "model": settings.whisper_model}
