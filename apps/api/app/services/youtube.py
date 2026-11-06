"""YouTube transcript fetch — public captions only, no paywall bypass."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

from app.core.errors import AppError

YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/|live/))([A-Za-z0-9_-]{6,})"
)


def extract_video_id(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.hostname and "youtu.be" in parsed.hostname:
        vid = parsed.path.lstrip("/").split("/")[0]
        if vid:
            return vid
    if parsed.query:
        qs = parse_qs(parsed.query)
        if qs.get("v"):
            return qs["v"][0]
    m = YOUTUBE_ID_RE.search(url)
    if m:
        return m.group(1)
    raise AppError("invalid_youtube_url", "Could not parse YouTube video id", 400)


def fetch_youtube_transcript(url: str) -> tuple[str, dict[str, Any]]:
    video_id = extract_video_id(url)
    meta: dict[str, Any] = {"video_id": video_id, "source": "youtube"}

    # Prefer youtube-transcript-api when installed.
    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore

        segments = YouTubeTranscriptApi.get_transcript(video_id)
        lines = [f"[{s.get('start', 0):.0f}s] {s.get('text', '').strip()}" for s in segments]
        text = "\n".join(lines).strip()
        if not text:
            raise AppError("no_transcript", "No captions available for this video", 422)
        meta["segment_count"] = len(segments)
        meta["fetcher"] = "youtube_transcript_api"
        return text, meta
    except AppError:
        raise
    except Exception:
        pass

    # Fallback: timedtext list + track fetch (public captions).
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            list_url = f"https://www.youtube.com/api/timedtext?type=list&v={video_id}"
            list_resp = client.get(list_url)
            list_resp.raise_for_status()
            tracks = re.findall(r'lang_code="([^"]+)"', list_resp.text)
            if not tracks:
                raise AppError("no_transcript", "No public captions found for this video", 422)
            lang = "en" if "en" in tracks else tracks[0]
            track = client.get(
                f"https://www.youtube.com/api/timedtext?v={video_id}&lang={lang}&fmt=vtt"
            )
            if track.status_code >= 400:
                track = client.get(f"https://www.youtube.com/api/timedtext?v={video_id}&lang={lang}")
            track.raise_for_status()
            raw = track.text
            # Strip VTT/XML tags lightly
            text = re.sub(r"<[^>]+>", " ", raw)
            text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{2}:\d{2}:\d{2}\.\d{3}", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 40:
                raise AppError("no_transcript", "Caption track was empty or unusable", 422)
            meta["lang"] = lang
            meta["fetcher"] = "timedtext"
            return text, meta
    except AppError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AppError("youtube_fetch_failed", f"Could not fetch YouTube transcript: {exc}", 502) from exc
