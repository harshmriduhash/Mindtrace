#!/usr/bin/env python3
"""Seed Applied AI Engineering skill path + practice items (including implement)."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Competency, PracticeItem, SkillPath

DEFAULT_RUBRIC = {
    "version": "1.0.0",
    "dimensions": [
        {"id": "correctness", "label": "Technical correctness", "weight": 0.4, "max": 5},
        {"id": "tradeoffs", "label": "Trade-off reasoning", "weight": 0.3, "max": 5},
        {"id": "clarity", "label": "Structure and clarity", "weight": 0.3, "max": 5},
    ],
}

COMPETENCIES = [
    {
        "slug": "llm-fundamentals",
        "title": "LLM fundamentals",
        "definition": "Explain tokens, context windows, temperature, and failure modes of generative models.",
        "sort_order": 1,
        "keywords": ["token", "context", "temperature", "hallucination", "latency"],
    },
    {
        "slug": "prompt-engineering",
        "title": "Prompt engineering",
        "definition": "Design prompts with clear roles, constraints, schemas, and evaluation criteria.",
        "sort_order": 2,
        "keywords": ["prompt", "schema", "few-shot", "constraint", "system"],
    },
    {
        "slug": "rag-systems",
        "title": "RAG systems",
        "definition": "Design retrieval-augmented generation with chunking, embeddings, and citation discipline.",
        "sort_order": 3,
        "keywords": ["retrieval", "embedding", "chunk", "citation", "rerank"],
    },
    {
        "slug": "eval-observability",
        "title": "Eval & observability",
        "definition": "Define golden sets, regression tests, cost/latency budgets, and uncertainty display.",
        "sort_order": 4,
        "keywords": ["golden", "eval", "regression", "cost", "latency", "uncertainty"],
    },
    {
        "slug": "safety-guardrails",
        "title": "Safety & guardrails",
        "definition": "Apply prompt-injection defenses, tool permissioning, and data minimization.",
        "sort_order": 5,
        "keywords": ["injection", "tool", "permission", "pii", "allowlist"],
    },
]

PRACTICE = [
    {
        "comp": "llm-fundamentals",
        "type": "baseline",
        "prompt": "Explain temperature vs top-p. When would you lower each, and what product risks rise if you raise them?",
        "minutes": 8,
        "keywords": ["temperature", "top-p", "diversity", "determinism", "risk"],
    },
    {
        "comp": "rag-systems",
        "type": "design",
        "prompt": "Design a RAG pipeline for internal engineering docs. Cover chunking, retrieval, citation, and failure modes.",
        "minutes": 15,
        "keywords": ["chunk", "embedding", "retriever", "citation", "stale"],
    },
    {
        "comp": "prompt-engineering",
        "type": "explain",
        "prompt": "Write a system prompt pattern for rubric-based coaching that forbids inventing citations.",
        "minutes": 10,
        "keywords": ["system", "rubric", "citation", "refuse", "schema"],
    },
    {
        "comp": "eval-observability",
        "type": "diagnose",
        "prompt": "Production eval pass-rate dropped 12% after a model upgrade. What do you investigate first?",
        "minutes": 10,
        "keywords": ["golden", "prompt", "tokenizer", "latency", "regression"],
    },
    {
        "comp": "safety-guardrails",
        "type": "recall",
        "prompt": "Without looking anything up: name three prompt-injection defenses for a tool-using agent.",
        "minutes": 6,
        "keywords": ["allowlist", "sandbox", "instruction hierarchy", "output filter"],
    },
    {
        "comp": "rag-systems",
        "type": "implement",
        "prompt": "Implement `chunk_text(text, max_chars)` that splits on paragraph boundaries without exceeding max_chars.",
        "minutes": 12,
        "keywords": ["chunk", "split", "paragraph"],
        "starter_code": "def chunk_text(text: str, max_chars: int) -> list[str]:\n    \"\"\"Split text into chunks <= max_chars, preferring blank-line boundaries.\"\"\"\n    # TODO: implement\n    return [text]\n",
        "tests": [
            {
                "expression": "chunk_text('a'*10, 10)",
                "expected": ["aaaaaaaaaa"],
            },
            {
                "setup": "t='hello\\n\\nworld'",
                "expression": "chunk_text(t, 20)",
                "expected": ["hello", "world"],
            },
            {
                "setup": "t='one\\n\\ntwo\\n\\nthree'",
                "expression": "all(len(c) <= 5 for c in chunk_text(t, 5))",
                "expected": True,
            },
        ],
    },
    {
        "comp": "prompt-engineering",
        "type": "implement",
        "prompt": "Implement `score_keyword_coverage(response, keywords)` returning fraction of keywords found (case-insensitive).",
        "minutes": 10,
        "keywords": ["keyword", "coverage", "eval"],
        "starter_code": "def score_keyword_coverage(response: str, keywords: list[str]) -> float:\n    \"\"\"Return 0..1 fraction of keywords present in response (case-insensitive).\"\"\"\n    # TODO: implement\n    return 0.0\n",
        "tests": [
            {"expression": "score_keyword_coverage('Hello Cache World', ['cache', 'ttl'])", "expected": 0.5},
            {"expression": "score_keyword_coverage('', ['a'])", "expected": 0.0},
            {"expression": "score_keyword_coverage('A B C', ['a', 'b', 'c'])", "expected": 1.0},
        ],
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        path = db.scalar(select(SkillPath).where(SkillPath.slug == "applied-ai-engineering"))
        if not path:
            path = SkillPath(
                slug="applied-ai-engineering",
                title="Applied AI Engineering",
                description=(
                    "Build evidence that you can design LLM products with retrieval, evaluation, "
                    "cost controls, and safety guardrails — not just chat demos."
                ),
                version="1.0.0",
                published_at=datetime.now(UTC),
                is_active=True,
            )
            db.add(path)
            db.flush()
            print(f"Created skill path {path.slug}")
        else:
            print(f"Skill path exists: {path.slug}")

        comp_by_slug: dict[str, Competency] = {}
        for item in COMPETENCIES:
            existing = db.scalar(
                select(Competency).where(Competency.path_id == path.id, Competency.slug == item["slug"])
            )
            if existing:
                comp_by_slug[item["slug"]] = existing
                continue
            comp = Competency(
                path_id=path.id,
                slug=item["slug"],
                title=item["title"],
                definition=item["definition"],
                sort_order=item["sort_order"],
                rubric_json=DEFAULT_RUBRIC,
            )
            db.add(comp)
            db.flush()
            comp_by_slug[item["slug"]] = comp
            print(f"  + competency {comp.slug}")

        prereq = {
            "prompt-engineering": "llm-fundamentals",
            "rag-systems": "prompt-engineering",
            "eval-observability": "rag-systems",
            "safety-guardrails": "prompt-engineering",
        }
        for child_slug, parent_slug in prereq.items():
            child, parent = comp_by_slug.get(child_slug), comp_by_slug.get(parent_slug)
            if child and parent and child.parent_id != parent.id:
                child.parent_id = parent.id

        for p in PRACTICE:
            comp = comp_by_slug[p["comp"]]
            exists = db.scalar(
                select(PracticeItem).where(PracticeItem.competency_id == comp.id, PracticeItem.prompt == p["prompt"])
            )
            if exists:
                continue
            meta = {"expected_keywords": p["keywords"], "language": "python"}
            if p["type"] == "implement":
                meta["starter_code"] = p.get("starter_code", "")
                meta["tests"] = p.get("tests", [])
            db.add(
                PracticeItem(
                    user_id=None,
                    competency_id=comp.id,
                    skill_path_id=path.id,
                    type=p["type"],
                    prompt=p["prompt"],
                    rubric_json=DEFAULT_RUBRIC,
                    rubric_version="1.0.0",
                    difficulty="medium",
                    expected_minutes=p["minutes"],
                    is_curated=True,
                    metadata_json=meta,
                )
            )
            print(f"  + practice ({p['type']}) for {p['comp']}")

        db.commit()
        print("Applied AI seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
