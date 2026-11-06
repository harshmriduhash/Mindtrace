#!/usr/bin/env python3
"""Run Mindtrace AI golden regression suite (deterministic provider by default)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai.provider import AIProvider

EVAL_DIR = ROOT / "evals" / "golden"


def main() -> int:
    provider = AIProvider()
    failed = 0

    extraction = json.loads((EVAL_DIR / "extraction_cases.json").read_text())
    for case in extraction:
        concepts = provider.extract_concepts(case["text"], case["title"])
        blob = " ".join(f"{c.get('title','')} {c.get('definition','')}" for c in concepts).lower()
        ok = len(concepts) >= case["expect_min_concepts"] and any(k in blob for k in case["must_include_any"])
        print(f"[extract] {case['id']}: {'PASS' if ok else 'FAIL'} ({len(concepts)} concepts)")
        failed += 0 if ok else 1

    evaluation = json.loads((EVAL_DIR / "evaluation_cases.json").read_text())
    for case in evaluation:
        result = provider.evaluate_response(
            prompt=case["prompt"],
            response=case["response"],
            rubric=case["rubric"],
            expected_keywords=case["expected_keywords"],
        )
        score = float(result.get("overall_score") or 0)
        ok = True
        if "min_overall" in case and score < case["min_overall"]:
            ok = False
        if "max_overall" in case and score > case["max_overall"]:
            ok = False
        print(f"[eval] {case['id']}: {'PASS' if ok else 'FAIL'} (score={score})")
        failed += 0 if ok else 1

    if failed:
        print(f"\n{failed} golden checks failed")
        return 1
    print("\nAll golden checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
