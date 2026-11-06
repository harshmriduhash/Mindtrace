# Mindtrace MVP Phase Plan

**Source of truth:** `Mindtrace_Production_Grade_PRD_v0.1.md`  
**Goal:** Private beta-ready product for 30–50 invited engineers.

## Locked defaults (open PRD decisions)

| Decision | Choice | Rationale |
|---|---|---|
| Launch track | **System Design for Senior Engineers** | Highest interview density for 3–10 YoE wedge |
| First outcome | Independently explain & apply core SD competencies under interview-like constraints | Matches Persona A and WDSP |
| Content mode | Curated path **+** paste/URL/PDF import | PRD P0 requires both |
| Assessment types | Explain, design, diagnose, trade-off (text) | Code sandbox deferred (P1) |
| Launch geography | Global English; Stripe-ready USD | Avoid India dual-provider complexity for beta |
| Price test | Free + Plus **$10/mo** | Midpoint of $8–12 hypothesis |
| AI providers | Adapter with OpenAI-compatible primary; deterministic fallbacks when AI unavailable | Product before AI |
| Auth | Email + password via FastAPI sessions (HttpOnly cookies); OAuth later | Proven path, no custom crypto beyond Argon2id |

## Phases

### Phase 0 — Foundation (this repo slice)
- Monorepo: `apps/web` (Next.js), `apps/api` (FastAPI), `packages/contracts`
- Docker Compose: Postgres + Redis + MinIO
- Schema + Alembic, auth, CI stubs, seed System Design path
- Design system tokens (calm, technical — no purple AI gradients)

### Phase 1A — Activation vertical slice
Signup → onboarding (role/goal/time) → skill path select → baseline → Today next action

### Phase 1B — Learn loop
Source import (text/URL/PDF) → concept extraction (AI or heuristic fallback) → user approve → tutor grounded in approved sources

### Phase 1C — Practice loop
Active recall → deterministic FSRS-lite scheduler → practical text assessment → rubric eval → error memory → progress timeline

### Phase 1D — Trust & beta ops
Memory inspect/correct/export/delete · quotas · usage page · privacy/security/methodology pages · email verification · rate limits · PDF/URL ingest · tutor · golden AI evals  
**Billing:** Stripe deferred (not operating in India). Free plan + transparent usage quotas ship without payments.

### Phase 2+ (after beta signal)
Adaptive scheduling improvements, voice, Skill Passport, second path, browser extension, India-capable payments — only after retention evidence

## Vertical-slice rule
Ship one complete user outcome per slice (API + DB + UI + states + ownership checks). Do not build the entire PRD in one pass.

## North Star for engineering
Every feature must support: **Learn → Remember → Apply → Prove**, with evidence-linked progress claims.
