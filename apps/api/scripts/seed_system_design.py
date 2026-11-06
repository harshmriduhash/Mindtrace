#!/usr/bin/env python3
"""Seed System Design skill path, competencies, rubrics, and curated practice items."""

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
        {"id": "correctness", "label": "Technical correctness", "weight": 0.35, "max": 5},
        {"id": "tradeoffs", "label": "Trade-off reasoning", "weight": 0.35, "max": 5},
        {"id": "clarity", "label": "Structure and clarity", "weight": 0.30, "max": 5},
    ],
    "notes": "Coaching rubric. Scores are provisional evidence signals, not mastery certificates.",
}

COMPETENCIES = [
    {
        "slug": "requirements-and-scope",
        "title": "Requirements & scope",
        "definition": "Clarify functional/non-functional requirements, constraints, and success metrics before designing.",
        "sort_order": 1,
        "keywords": ["requirements", "latency", "availability", "scale", "constraints"],
    },
    {
        "slug": "high-level-design",
        "title": "High-level design",
        "definition": "Propose a coherent component architecture with clear data flow and API boundaries.",
        "sort_order": 2,
        "keywords": ["api", "service", "queue", "database", "cdn", "load balancer"],
    },
    {
        "slug": "data-modeling",
        "title": "Data modeling & storage",
        "definition": "Choose storage models, schemas, indexes, and consistency approach for the workload.",
        "sort_order": 3,
        "keywords": ["schema", "index", "consistency", "sharding", "partition"],
    },
    {
        "slug": "caching",
        "title": "Caching & performance",
        "definition": "Apply caching strategies, invalidation, and performance trade-offs appropriately.",
        "sort_order": 4,
        "keywords": ["cache", "ttl", "invalidation", "write-through", "write-back", "aside"],
    },
    {
        "slug": "reliability",
        "title": "Reliability & failure modes",
        "definition": "Identify failure modes and design for retries, idempotency, backpressure, and recovery.",
        "sort_order": 5,
        "keywords": ["retry", "timeout", "circuit breaker", "idempotent", "failover", "replication"],
    },
    {
        "slug": "scalability",
        "title": "Scalability & capacity",
        "definition": "Reason about throughput, bottlenecks, horizontal scaling, and capacity planning.",
        "sort_order": 6,
        "keywords": ["throughput", "bottleneck", "horizontal", "qps", "shard"],
    },
    {
        "slug": "communication",
        "title": "Interview communication",
        "definition": "Structure explanations, ask clarifying questions, and defend decisions under time pressure.",
        "sort_order": 7,
        "keywords": ["clarify", "trade-off", "assumption", "walkthrough"],
    },
]


PRACTICE = [
    {
        "comp": "caching",
        "type": "baseline",
        "prompt": "Explain cache-aside vs write-through vs write-back. When would you choose each, and what failure modes matter?",
        "minutes": 8,
        "keywords": ["cache-aside", "write-through", "write-back", "invalidation", "consistency"],
    },
    {
        "comp": "requirements-and-scope",
        "type": "baseline",
        "prompt": "You are designing a URL shortener. What clarifying questions do you ask first, and which NFRs drive the architecture?",
        "minutes": 8,
        "keywords": ["latency", "availability", "read", "write", "scale", "analytics"],
    },
    {
        "comp": "reliability",
        "type": "baseline",
        "prompt": "A payment API is timing out intermittently. Diagnose likely causes and propose safeguards (timeouts, retries, idempotency).",
        "minutes": 10,
        "keywords": ["timeout", "retry", "idempotent", "circuit", "queue"],
    },
    {
        "comp": "high-level-design",
        "type": "design",
        "prompt": "Design a news feed for 10M DAU. Outline major components, data flow, and the first bottleneck you would expect.",
        "minutes": 15,
        "keywords": ["fan-out", "cache", "timeline", "queue", "database", "cdn"],
    },
    {
        "comp": "data-modeling",
        "type": "explain",
        "prompt": "Compare SQL vs NoSQL for a multi-tenant billing ledger. Defend a choice with consistency and query patterns.",
        "minutes": 10,
        "keywords": ["acid", "consistency", "transactions", "query", "tenant"],
    },
    {
        "comp": "scalability",
        "type": "diagnose",
        "prompt": "p95 latency spiked after traffic doubled, but CPU on app servers is only 40%. What do you investigate and why?",
        "minutes": 10,
        "keywords": ["database", "lock", "network", "cache", "gc", "connection pool"],
    },
    {
        "comp": "caching",
        "type": "recall",
        "prompt": "Without looking anything up: what is the thundering herd problem, and how can you mitigate it?",
        "minutes": 6,
        "keywords": ["thundering herd", "lock", "stale", "ttl", "jitter"],
    },
    {
        "comp": "communication",
        "type": "explain",
        "prompt": "Walk through how you would structure a 35-minute system design interview answer from first minute to last.",
        "minutes": 8,
        "keywords": ["requirements", "api", "deep dive", "trade-off", "summary"],
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        path = db.scalar(select(SkillPath).where(SkillPath.slug == "system-design-senior"))
        if not path:
            path = SkillPath(
                slug="system-design-senior",
                title="System Design for Senior Engineers",
                description=(
                    "Build evidence that you can clarify requirements, design coherent architectures, "
                    "reason about data/caching/reliability trade-offs, and communicate under interview constraints."
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

        for p in PRACTICE:
            comp = comp_by_slug[p["comp"]]
            exists = db.scalar(
                select(PracticeItem).where(
                    PracticeItem.competency_id == comp.id,
                    PracticeItem.prompt == p["prompt"],
                )
            )
            if exists:
                continue
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
                    metadata_json={"expected_keywords": p["keywords"]},
                )
            )
            print(f"  + practice ({p['type']}) for {p['comp']}")

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
