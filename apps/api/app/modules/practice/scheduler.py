"""Deterministic review scheduler (FSRS-lite). Explainable, no neuroscientific claims."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def next_interval_days(*, result: str, stability: float, difficulty: float, reps: int) -> tuple[float, float, float]:
    """
    Returns (new_stability, new_difficulty, interval_days).
    result: again | hard | good | easy | fail | pass
    """
    mapped = {
        "fail": "again",
        "again": "again",
        "hard": "hard",
        "pass": "good",
        "good": "good",
        "easy": "easy",
    }.get(result, "good")

    d = min(0.9, max(0.1, difficulty))
    s = max(0.5, stability)

    if mapped == "again":
        s = max(0.5, s * 0.5)
        d = min(0.9, d + 0.08)
        interval = 0.25  # ~6 hours
    elif mapped == "hard":
        s = s * 1.1
        d = min(0.9, d + 0.03)
        interval = max(1.0, s * 0.8)
    elif mapped == "easy":
        s = s * (1.8 - d * 0.3)
        d = max(0.1, d - 0.04)
        interval = max(2.0, s * 2.2)
    else:  # good
        s = s * (1.4 - d * 0.2)
        interval = max(1.0, s * 1.3 if reps else 1.0)

    return round(s, 3), round(d, 3), round(interval, 3)


def compute_due_at(interval_days: float, now: datetime | None = None) -> datetime:
    now = now or datetime.now(UTC)
    return now + timedelta(days=interval_days)


def result_from_score(overall: float, overall_max: float = 5.0) -> str:
    ratio = overall / overall_max
    if ratio < 0.4:
        return "again"
    if ratio < 0.55:
        return "hard"
    if ratio < 0.85:
        return "good"
    return "easy"
