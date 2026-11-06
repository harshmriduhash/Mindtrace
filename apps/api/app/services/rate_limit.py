"""Simple in-process rate limiter (Redis-backed later when multi-instance)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from app.core.errors import QuotaExceededError

_lock = Lock()
_buckets: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(key: str, *, limit: int, window_seconds: int) -> None:
    now = time.time()
    with _lock:
        q = _buckets[key]
        while q and now - q[0] > window_seconds:
            q.popleft()
        if len(q) >= limit:
            raise QuotaExceededError(f"Rate limit exceeded. Try again in {window_seconds} seconds.")
        q.append(now)


def client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
