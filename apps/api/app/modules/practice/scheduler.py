"""Adaptive review scheduler (FSRS-lite + remediation modes)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def next_interval_days(
    *,
    result: str,
    stability: float,
    difficulty: float,
    reps: int,
    consecutive_fails: int = 0,
) -> tuple[float, float, float, int, str]:
    """
    Returns (new_stability, new_difficulty, interval_days, new_consecutive_fails, remediation_mode).
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
    fails = consecutive_fails

    if mapped == "again":
        s = max(0.5, s * 0.5)
        d = min(0.9, d + 0.08)
        fails += 1
        # After repeated fails, shorten interval and escalate remediation.
        if fails >= 3:
            interval = 0.08  # ~2 hours — switch teaching approach soon
        elif fails == 2:
            interval = 0.15
        else:
            interval = 0.25
    elif mapped == "hard":
        s = s * 1.1
        d = min(0.9, d + 0.03)
        fails = max(0, fails - 1)
        interval = max(1.0, s * 0.8)
    elif mapped == "easy":
        s = s * (1.8 - d * 0.3)
        d = max(0.1, d - 0.04)
        fails = 0
        interval = max(2.0, s * 2.2)
    else:  # good
        s = s * (1.4 - d * 0.2)
        fails = 0
        interval = max(1.0, s * 1.3 if reps else 1.0)

    remediation = remediation_for_fails(fails)
    return round(s, 3), round(d, 3), round(interval, 3), fails, remediation


def remediation_for_fails(consecutive_fails: int) -> str:
    if consecutive_fails >= 3:
        return "implement"
    if consecutive_fails == 2:
        return "tutor_first"
    if consecutive_fails == 1:
        return "varied"
    return "standard"


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


def prefer_alternate_type(current_type: str, remediation_mode: str) -> list[str]:
    """Suggest alternate practice modalities after repeated failure."""
    if remediation_mode == "implement":
        return ["implement", "diagnose", "explain"]
    if remediation_mode == "tutor_first":
        return ["explain", "recall", "design"]
    if remediation_mode == "varied":
        order = ["diagnose", "design", "explain", "recall", "implement", "voice"]
        return [t for t in order if t != current_type] + [current_type]
    return [current_type]
