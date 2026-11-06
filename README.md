<p align="center">
  <img src="docs/assets/mindtrace-mark.svg" alt="Mindtrace" width="72" height="72" />
</p>

<h1 align="center">Mindtrace</h1>

<p align="center">
  <strong>Learn it. Remember it. Apply it. Prove it.</strong>
</p>

<p align="center">
  The personal skill-development system that turns fragmented learning into durable capability — with evidence you can trust.
</p>

<p align="center">
  <a href="#what-problem-does-it-solve"><img src="https://img.shields.io/badge/Problem—Fragmented_learning-0F7A5F?style=flat-square" alt="Problem" /></a>
  <a href="#how-mindtrace-solves-it"><img src="https://img.shields.io/badge/Solution—Evidence_loop-C45C26?style=flat-square" alt="Solution" /></a>
  <a href="#does-it-save-time--money"><img src="https://img.shields.io/badge/ROI—Time_+_Money-161C19?style=flat-square" alt="ROI" /></a>
  <a href="#architecture"><img src="https://img.shields.io/badge/Architecture—HLD_·_LLD-2C3A32?style=flat-square" alt="Architecture" /></a>
  <img src="https://img.shields.io/badge/Status—Private_Beta_MVP-0A5A46?style=flat-square" alt="Status" />
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#product-tour">Product Tour</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#for-every-reader">Who this is for</a> ·
  <a href="#security--trust">Security</a>
</p>

---

## What is Mindtrace?

**In one sentence:**  
Mindtrace helps ambitious engineers stop “studying a lot” and start **actually remembering and applying** what they learn — with a transparent record of proof.

**In plain language:**  
Most people learn from videos, blogs, notes, and interview prep sites. A week later, they can’t explain the idea under pressure. Mindtrace connects those pieces into one loop:

> **Choose a skill → check your baseline → learn from your sources → retrieve from memory → practice realistically → fix repeated mistakes → show improvement**

It is **not** another chatbot, flashcard factory, course marketplace, or interview cheat tool.  
It is a **skill operating system** for people who care about real competence.

**Launch wedge:** Software engineers (~3–10 years experience) preparing for senior technical interviews — starting with **System Design**.

---

## What problem does it solve?

### The painful reality

| What learners do today | What usually happens |
|---|---|
| Watch videos / read docs | Feels productive, fades fast |
| Save tabs & notes | Capture ≠ understanding |
| Drill flashcards | Recognition ≠ recall under pressure |
| Attempt mock interviews | Feedback is generic; mistakes repeat |
| Check “progress” dashboards | Streaks & volume ≠ demonstrated skill |

**Core problem:**  
A motivated engineer cannot reliably convert fragmented learning into **durable recall** and **demonstrated technical capability**.

### Who feels this most?

- Engineers preparing for senior / staff interviews  
- Engineers closing a specific skill gap while working full-time  
- Returning learners who paused for weeks and lost context  

### What Mindtrace is *not* solving

- Doing interviews for you  
- Selling courses  
- Ranking employees for managers  
- Claiming “you’ve mastered X” from one AI score  

---

## How Mindtrace solves it

Mindtrace’s product is the **loop**, not the model.

```text
Skill goal
   ↓
Baseline evidence
   ↓
Import sources (text / URL / PDF) → approve concepts
   ↓
Active recall + practical tasks (explain / design / diagnose)
   ↓
Rubric feedback + error memory
   ↓
Deterministic review scheduling
   ↓
Progress timeline you can inspect, export, or delete
```

### The five memory types (why this compounds)

| Memory | What it stores | Why it matters |
|---|---|---|
| Semantic | Concepts you studied | Structured knowledge |
| Episodic | Specific practice events | History you can revisit |
| Procedural | Methods you reuse | Better under pressure |
| Error | Recurring misconceptions | Stops repeating the same miss |
| Progress | Evidence over time | Claims you can defend |

**AI is a multiplier, not the product.**  
Auth, quotas, scheduling, ownership, and evidence rules stay deterministic in application code. AI helps extract concepts, tutor from *your* approved sources, and coach against versioned rubrics — with uncertainty shown, and fallbacks when AI is off.

---

## Does it save time & money?

**Yes — if “time” means hours that actually move skill, and “money” means avoiding wasted prep spend.**

### Time

| Without Mindtrace | With Mindtrace |
|---|---|
| Re-watch content you already “learned” | Next action is evidence-based |
| Reconstruct context after a break | Resume from skill state + error memory |
| Random practice from anxiety | Prioritized weak competencies |
| Unclear if you’re interview-ready | Baseline → applied tasks → timeline |

**Target first-value:** useful gap summary + first practice in **10–20 minutes**.

### Money

| Cost people already pay | How Mindtrace reduces waste |
|---|---|
| Multiple subscriptions (notes, Anki, mocks, courses) | One workflow connecting study → proof |
| Coaching / mocks with no longitudinal memory | Persistent error + evidence record |
| Extra interview cycles from weak transfer | Practice on transfer tasks, not recognition quizzes |
| Unlimited AI chat spend | Plan quotas + kill-switches; AI optional |

**Honest framing:** Mindtrace does not guarantee a job offer. It reduces the expensive pattern of *studying hard without retained, demonstrable skill*.

**Pricing note (India):** Card payments via Stripe are **not enabled** in this build (Stripe is not operating for this launch geography). The product ships as a **free beta with transparent usage quotas**. Paid billing will use an India-capable provider when validated.

---

## Product tour

| Area | What you get |
|---|---|
| **Today** | One clear next best action + why |
| **My Skills** | Competency map with evidence status (not fake mastery %) |
| **Learn** | Import **text / public URL / PDF** → extract → **you approve** concepts → tutor |
| **Practice** | Baseline, recall, design, diagnose — answer first, feedback after |
| **Memory** | Inspect recurring errors; delete what you don’t want kept |
| **Progress** | Timeline of attempts and evidence |
| **Usage / Settings** | Quotas, export, deletion |

Public trust pages: [`/methodology`](apps/web/src/app/methodology/page.tsx) · [`/privacy`](apps/web/src/app/privacy/page.tsx) · [`/security`](apps/web/src/app/security/page.tsx)

---

## Architecture

### High-Level Design (HLD)

```mermaid
flowchart TB
  subgraph Clients
    WEB["Next.js Web App<br/>Landing + Authenticated App"]
  end

  subgraph Edge
    CDN["CDN / TLS<br/>Same-origin API proxy"]
  end

  subgraph Platform["Mindtrace Modular Monolith"]
    API["FastAPI Application API"]
    WORK["Async-ready Job Model<br/>extract · evaluate · export"]
    AI["AI Provider Adapter<br/>OpenAI optional · deterministic fallback"]
  end

  subgraph Data
    DB[("PostgreSQL or SQLite<br/>System of record")]
    OBJ[("Object storage<br/>PDFs / artefacts")]
    REDIS[("Redis<br/>cache / queue when scaled")]
  end

  WEB --> CDN --> API
  API --> DB
  API --> OBJ
  API --> REDIS
  API --> WORK
  WORK --> AI
  API --> AI
```

**Why this shape:** one deployable API + one primary database = faster iteration, lower ops cost, clearer ownership. Workers isolate slow ingestion/evaluation. Split into microservices only when measured load or team boundaries require it.

### System context

```mermaid
C4Context
title Mindtrace — System Context
Person(learner, "Learner", "Engineer building demonstrable skill")
System(mt, "Mindtrace", "Skill goals, sources, recall, practice, evidence")
System_Ext(llm, "LLM Provider", "Optional concept/tutor/eval")
System_Ext(email, "Email adapter", "Verification links")
Rel(learner, mt, "HTTPS")
Rel(mt, llm, "Structured prompts")
Rel(mt, email, "Transactional mail / local log")
```

### Low-Level Design (LLD) — core modules

```mermaid
flowchart LR
  subgraph API["apps/api"]
    AUTH[auth]
    ONB[onboarding]
    SKL[skills]
    SRC[sources]
    PRAC[practice]
    MEM[memory]
    PROG[progress]
    TUT[tutor]
    USE[usage]
    REC[recommendations]
  end

  AUTH --> ONB --> SKL
  SRC --> TUT
  SRC --> PRAC
  PRAC --> MEM
  PRAC --> PROG
  REC --> PRAC
  USE --> AUTH
```

| Module | Responsibility | Critical rules |
|---|---|---|
| `auth` | Signup/login/session, email verification, rate limits | Argon2id; HttpOnly cookies |
| `onboarding` | Goal, path, time budget | Seeds `user_skills` |
| `sources` | Text / SSRF-safe URL / PDF | User approves concepts before graph commit |
| `practice` | Attempts, rubric eval, FSRS-lite scheduler | Never drop a submitted response |
| `memory` | Semantic/episodic/error/progress | User can correct/delete |
| `tutor` | Source-grounded explanation | Only approved concepts + citations |
| `usage` | Quotas & transparency | Server-side enforcement |
| `recommendations` | Next best action | Deterministic priority rules |

### Request path — practice evaluation (LLD sequence)

```mermaid
sequenceDiagram
  participant U as Learner
  participant W as Next.js
  participant A as FastAPI
  participant D as Database
  participant AI as AI Adapter

  U->>W: Submit practice response
  W->>A: POST /assessments/{id}/submit
  A->>D: Persist response (immutable attempt)
  A->>AI: Evaluate vs rubric (or deterministic fallback)
  AI-->>A: Structured result + uncertainty
  A->>D: Evaluation + error patterns + review schedule
  A-->>W: Feedback (provisional coaching signal)
  W-->>U: Rubric breakdown + next step
```

### Data model (simplified ER)

```mermaid
erDiagram
  USER ||--o{ GOAL : has
  USER ||--o{ USER_SKILL : tracks
  SKILL_PATH ||--o{ COMPETENCY : contains
  COMPETENCY ||--o{ USER_SKILL : maps
  USER ||--o{ SOURCE : imports
  SOURCE ||--o{ SOURCE_SEGMENT : splits
  SOURCE_SEGMENT ||--o{ CONCEPT : extracts
  USER ||--o{ ATTEMPT : submits
  PRACTICE_ITEM ||--o{ ATTEMPT : prompts
  ATTEMPT ||--|| EVALUATION : scored_by
  USER ||--o{ LEARNER_MEMORY : owns
  USER ||--o{ REVIEW_STATE : schedules
```

### Repository layout

```text
Mindtrace/
├── apps/
│   ├── web/                 # Next.js 15 App Router (UI)
│   └── api/                 # FastAPI modular monolith
│       ├── app/
│       │   ├── modules/     # auth, sources, practice, …
│       │   ├── ai/          # provider adapter
│       │   ├── services/    # SSRF, PDF, email, rate limit
│       │   └── models/      # SQLAlchemy entities
│       ├── evals/golden/    # AI regression fixtures
│       └── scripts/         # seed, init_db, golden runner
├── packages/contracts/      # API contract notes
├── docs/                    # Phase plan + ADRs
├── docker-compose.yml       # Postgres + Redis + MinIO
└── Mindtrace_Production_Grade_PRD_v0.1.md
```

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js 15 + TypeScript + Tailwind | SEO public site + app in one stack |
| Backend | FastAPI modular monolith | Clear AI/doc boundaries, fast iteration |
| Database | SQLite (local) / PostgreSQL (prod) | Relational integrity for attempts & ownership |
| Auth | Sessions (HttpOnly cookie) + Argon2id | Proven, browser-friendly |
| AI | Provider adapter + deterministic fallback | Product works without API keys |
| Files | PDF parse via `pypdf`; URL fetch SSRF-safe | Beta-ready ingest without bypassing paywalls |
| Queue | Job records + Redis-ready | Async path without premature infra |

---

## Quick start

### Prerequisites

- Node.js 20+  
- Python 3.11+  
- Optional: Docker Desktop (Postgres / Redis / MinIO)

### 1) API

```bash
cd apps/api
source .venv/bin/activate          # or: python3 -m venv .venv && pip install -r requirements.txt
python scripts/init_db.py
python scripts/seed_system_design.py
uvicorn app.main:app --reload --port 8000
```

### 2) Web

```bash
cd apps/web
cp .env.local.example .env.local
npm install
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)**  
API health: **[http://localhost:8000/healthz](http://localhost:8000/healthz)**

> The web app proxies `/api/v1/*` → API so **session cookies work on localhost**.

### 3) Golden AI evals

```bash
cd apps/api && source .venv/bin/activate
python scripts/run_golden_evals.py
```

### 4) Optional Docker data plane

```bash
docker compose up -d
# then set DATABASE_URL=postgresql+psycopg://mindtrace:mindtrace@localhost:5432/mindtrace
```

### Environment highlights

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLite or Postgres |
| `SESSION_SECRET` | Sign cookies (change in prod) |
| `AI_ENABLED` / `OPENAI_API_KEY` | Optional LLM path |
| `NEXT_PUBLIC_API_URL` | Default `/api/v1` (same-origin) |

---

## For every reader

### If you’re a developer
Start with `apps/api/app/main.py` and `apps/web/src/app/app/`. Ownership is always `user_id`-scoped. AI never sets entitlements or final mastery alone. Run golden evals before changing prompts/rubrics.

### If you’re a founder / entrepreneur
The wedge is narrow on purpose: **System Design for senior engineers**. North-star metric is **Weekly Demonstrated Skill Progress (WDSP)** — not streaks. Moat hypothesis = longitudinal, user-controlled skill evidence that improves sequencing over time.

### If you’re a recruiter / hiring manager
Mindtrace is a **personal learning product**, not an employer surveillance or automated hiring score. Rubric outputs are **provisional coaching signals** with uncertainty — not a candidate ranking system.

### If you’re new to tech
Think of Mindtrace like a serious coach with a notebook: it remembers what you studied, what you forgot, what you keep getting wrong, and what to practice next — so your effort turns into skill you can show.

---

## Security & trust

- User-scoped authorization on every resource  
- Rate limits on signup / login / verification  
- SSRF blocks for private IPs, localhost, link-local, cloud metadata hosts  
- PDF magic-byte checks, size/page caps, encrypted PDFs rejected  
- Prompt-injection stance: imported text is **data**, never instructions  
- Export + deletion from Settings  
- Privacy / Security / Methodology pages in the product  

We do **not** claim SOC 2 / GDPR certification until independently verified.

---

## Roadmap snapshot

| Phase | Outcome | Status |
|---|---|---|
| 0 Foundation | Monorepo, schema, auth, design system | Done |
| 1A Activation | Signup → onboarding → Today | Done |
| 1B Learn | Text / URL / PDF + approve + tutor | Done |
| 1C Practice | Baseline, recall, rubric eval, scheduler, errors | Done |
| 1D Trust | Quotas, usage, privacy pages, email verify, golden evals | Done |
| Payments | India-capable billing (Stripe deferred) | Planned |
| V1 | Voice practice, Skill Passport, 2nd path | After retention signal |

Full product definition: [`Mindtrace_Production_Grade_PRD_v0.1.md`](Mindtrace_Production_Grade_PRD_v0.1.md)  
Phase plan: [`docs/MVP_PHASE_PLAN.md`](docs/MVP_PHASE_PLAN.md)  
ADR: [`docs/adr/0001-architecture.md`](docs/adr/0001-architecture.md)

---

## Brand promise

> **Turn what you study into what you can do.**  
> Build durable technical skills through active recall, realistic practice, and feedback that remembers where you need to improve.

**CTA:** Build my skill plan → [`/signup`](http://localhost:3000/signup)

---

<p align="center">
  <sub>Mindtrace — evidence over activity. Practice over passive consumption. User control over hidden memory.</sub>
</p>
