# P0 Depth + Launch Plan

Build order (execute 1→9, then README + push).

| # | Workstream | Deliverable | Exit criteria |
|---|---|---|---|
| 1 | Multi-item baseline | Balanced sample across competencies; pause/resume | User completes ≥3 items; can pause mid-session |
| 2 | Concept edit + provenance | PATCH concept; show source/page/excerpt in Learn UI | User edits before approve; provenance visible |
| 3 | Challenge feedback | Appeal an evaluation with reason | Challenge stored; status `challenged` |
| 4 | Competency map depth | Prereq tree, evidence drill-down, dispute | Skill detail page shows all three |
| 5 | Postgres + Alembic | Initial migration; dual SQLite/Postgres | `alembic upgrade head` works |
| 6 | Object storage + workers | Local/S3 storage; queued extract jobs | PDF stored by key; worker processes queue |
| 7 | CI + tests | GitHub Actions + IDOR tests + golden evals | PR pipeline green locally |
| 8 | Analytics + observability | Event helper + structured request logs | Events emitted on core flows |
| 9 | India ops | Razorpay stub, ESP email, admin, terms, feedback | Pages/APIs present; keys optional |

**Deferred by product decision:** Stripe. Use Razorpay for India when keys are provided.
