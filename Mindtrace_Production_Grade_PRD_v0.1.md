# Mindtrace — Production-Grade Product Requirements Document
**Document type:** Product Requirements Document + Product Blueprint + Engineering Specification  
**Version:** 0.1 — First complete product definition  
**Status:** Draft for founder validation and implementation planning  
**Research snapshot:** 6 November 2026  
**Product:** Mindtrace  
**Category:** B2C learning, memory and skill-development platform  
**Initial audience:** Software engineers preparing for senior-level technical interviews and building demonstrable engineering capability

---

# Executive Summary

Mindtrace is a personal skill-development system that turns fragmented learning into retained knowledge, repeatable performance and evidence of competence.

A user can set a skill goal, bring learning material into Mindtrace, understand it, practise retrieving it, apply it to realistic problems, receive feedback, and revisit weaknesses at the right time. Mindtrace maintains a longitudinal learning record: concepts understood, concepts forgotten, mistakes repeated, practice performance, confidence calibration and demonstrated progress.

**Product promise:** Learn it. Remember it. Apply it. Prove it.

Mindtrace is not:
- A generic chatbot with a study prompt.
- A course marketplace or video-hosting platform.
- A note-taking app with AI summaries.
- A flashcard generator whose success metric is number of cards reviewed.
- An interview cheat sheet or a tool that supplies covert answers during real interviews.
- A hiring predictor or a guarantee of job offers.

**Initial wedge:** Software engineers with approximately 3–10 years of experience preparing for senior technical interviews or closing specific engineering skill gaps. Initial learning paths should be limited to a small, curated set of technical competencies, with System Design and Applied AI Engineering as candidate launch tracks. Track selection is an explicit validation decision, not a proven market fact.

**Core loop:**

`Choose a skill goal → Establish baseline → Learn/import material → Retrieve from memory → Apply in a realistic task → Diagnose errors → Schedule targeted practice → Demonstrate improvement`

**North Star Metric:** Weekly Demonstrated Skill Progress (WDSP): the number of active learners per week who complete a qualifying assessment or practical task and show a statistically/operationally meaningful improvement against their own baseline on a defined skill rubric. A completed quiz alone does not count.

**Primary product moat hypothesis:** A high-quality, user-controlled longitudinal skill graph connecting learning sources, concepts, retrieval outcomes, practical attempts, error patterns and evidence. The accumulated record should improve recommendations and make the product more useful over time. It is not a moat until it demonstrably improves outcomes and retention.

---

# 0. Product Philosophy

## 0.1 Product before AI

The product's core value is the learning workflow, not the presence of a language model.

| Value without AI | Additional value from AI |
|---|---|
| Skill plans, learning goals, schedules and progress history | Convert user-approved sources into structured concepts and practice material |
| Spaced retrieval and practice history | Generate varied questions and scenario-based practice |
| Rubrics and competency maps | Provide contextual feedback against a rubric |
| Error log and evidence portfolio | Classify recurring misconceptions and suggest targeted remediation |
| User-controlled memory and source provenance | Retrieve relevant prior learning context when coaching |

## 0.2 What AI makes possible

- Transform heterogeneous learning sources into a structured, source-linked knowledge model.
- Generate questions at different cognitive levels: explain, compare, diagnose, design, implement and critique.
- Adapt practice based on the learner's actual history.
- Identify recurring error patterns across multiple sessions.
- Compare a new practical attempt with prior attempts using explicit rubrics.
- Explain why a recommendation was made and which evidence supports it.

## 0.3 Product moat

**Potentially durable:**
1. Longitudinal learner history with explicit provenance and user corrections.
2. A high-quality competency framework and calibrated assessment rubrics for the initial technical niche.
3. Personalised practice sequencing that is measurably better than generic review queues.
4. A trustworthy evidence record of applied skill, not just content consumption.
5. User habit and workflow integration around a recurring skill-improvement loop.

**Easy to copy:** chat interface, summarisation, flashcard generation, generic quizzes, streaks, a skill dashboard, generic RAG.

## 0.4 Non-negotiable principles

- Never equate content consumed with mastery.
- Never show a precise mastery score without explaining its evidence and uncertainty.
- Never invent citations or claim a user demonstrated a skill when they did not.
- Let users inspect, edit, export and delete their learning memory.
- Distinguish self-reported confidence from observed performance.
- A model-generated question or evaluation must be validated before it affects a high-stakes progress record.
- Practice must teach the user to perform independently; it must not create dependence on the assistant.

---

# 1. Market and Problem Research

## 1.1 Research limitations

No direct user interviews, surveys, paid-conversion tests or proprietary market-sizing work have been performed for this PRD. Competitor pages are secondary evidence of available product capabilities and published pricing, not proof of demand, market share or willingness to pay.

Do not use an unsupported TAM/SAM/SOM figure in an investor deck. Build a bottom-up model only after validating reachable users, conversion, retention and price.

## 1.2 Problem hypothesis

Software engineers learn through a fragmented collection of:
- Documentation, articles, videos, courses and books.
- Notes, bookmarks, browser tabs and code snippets.
- Coding exercises and interview question banks.
- Mock interviews and peer feedback.
- Personal projects and production incidents.

These activities are weakly connected. A user may consume substantial material but later fail to explain it, retrieve it under pressure, apply it to a new problem or recognise a repeated misconception.

**Hypothesis to validate:** Engineers do not primarily need more content. They need a system that connects learning to recall, application, feedback and measurable progress.

## 1.3 Problem → alternatives → gap → solution → outcome

| Stage | Definition |
|---|---|
| Problem | Learning activity is fragmented; retention and applied competence are hard to measure |
| Existing alternatives | Notes, bookmarks, Anki, RemNote, courses, coding platforms, mock-interview products, generic AI chat |
| Gap | These tools often optimise one stage—capture, content, repetition, practice or feedback—without a coherent learner model across stages |
| Mindtrace solution | A persistent skill-development workflow that connects sources, concepts, recall, practical attempts, mistakes and progress |
| Desired outcome | The learner can independently explain, retrieve, apply and defend a skill in a new context |

## 1.4 Competitor landscape

The following is a product-level comparison, not a claim that competitors lack every capability listed.

| Product | Strong position | Published pricing/capability evidence observed | Mindtrace implication |
|---|---|---|---|
| Anki | Spaced-repetition flashcards and scheduling | Official site describes cross-device sync, media, customisation and large decks; FSRS is supported in current documentation | Do not compete on flashcards or scheduling alone |
| RemNote | Notes, knowledge organisation, PDFs, flashcards and AI learning | Pricing page lists Free, Pro and Pro+AI tiers; Pro+AI displayed at $18/month on the page reviewed | Mindtrace must connect learning to practical skill evidence and longitudinal error patterns |
| Readwise / Reader | Capture, read, highlight, organise and review content | Full Readwise displayed at $9.99/month billed annually and $12.99 monthly on pricing pages reviewed | Do not become another read-it-later/highlight library |
| Brilliant | Structured interactive learning and guided courses | Individual Premium displayed at $20/month on its subscription page | Structured paths and hands-on learning are proven product patterns; content quality matters |
| Huru | Spoken AI mock interviews and answer feedback | Its public site states job-seeker features are free as of September 2026 | A paid Mindtrace plan cannot rely on generic mock-interview practice alone |
| Yoodli | AI roleplay, interview and communication practice | Individual Starter free, Pro $8/month annual billing, Advanced $20/month annual billing on pricing page reviewed | Practice feedback is a competitive category; Mindtrace must connect it to durable skill development |
| InterviewSkool | Coding/DSA and system-design mock interviews | Public page lists single-session and bundle pricing | Specialised interview simulation is an adjacent alternative |
| Thita.ai | Technical interview learning, problem library and voice mock interviews | Public page lists free tier and paid plans from $14.99/month | Technical interview products already combine content, practice and scoring |
| Bezen | AI/ML engineering learning and interview preparation | Public page lists a free plan and Pro pricing in INR | Applied AI engineering is a potentially relevant niche but has existing competitors |

**Research sources (checked 6 November 2026):**
- Anki: https://apps.ankiweb.net/ and https://github.com/ankitects/anki/blob/main/docs-site/manual/deck-options.mdx
- RemNote pricing: https://www.remnote.com/pricing
- RemNote AI flashcards: https://help.remnote.com/en/articles/10102901-generating-flashcards-with-ai
- Readwise pricing: https://readwise.io/pricing
- Brilliant pricing: https://brilliant.org/subscribe/
- Huru: https://huru.ai/about/ and https://huru.ai/press/
- Yoodli pricing: https://yoodli.ai/pricing
- InterviewSkool: https://www.interviewskool.com/
- Thita.ai: https://thita.ai/
- Bezen: https://bezen.in/

## 1.5 Whitespace hypothesis

Mindtrace should attempt to own the relationship between:
- A skill definition and its subskills.
- The material a learner used to study it.
- The learner's ability to retrieve and explain it.
- The learner's ability to apply it in realistic work.
- The mistakes and misconceptions observed during attempts.
- The next best practice action.
- The evidence that supports a progress claim.

This is a positioning hypothesis requiring interviews and prototype tests.

## 1.6 Research plan before broad launch

Conduct at least:
- 15 interviews with software engineers actively preparing for senior technical interviews.
- 5 interviews with engineers who recently completed an interview cycle.
- 5 interviews with engineers who abandoned a learning/study product.
- 5 paid or refundable pre-order tests after prototype validation.

Ask users to show their real current workflow, not merely react to a pitch. Observe where they save material, how they revisit it, how they practise, what they forget and what outcome they are paying to achieve.

---

# 2. Problem Definition

## 2.1 Core problem

A motivated engineer cannot reliably convert fragmented learning activity into durable recall and demonstrated technical capability.

## 2.2 Secondary problems

1. Captured resources are not converted into a useful learning plan.
2. Summaries create an illusion of understanding.
3. Review schedules are not connected to practical application.
4. Users repeat mistakes without a durable error history.
5. Generic quizzes test recognition rather than independent reasoning.
6. Progress dashboards reward streaks and volume instead of capability.
7. Interview preparation is often disconnected from the user's broader engineering growth.

## 2.3 Root causes

- Learning sources live in different tools.
- No shared skill taxonomy links resources to competencies.
- Practice outcomes are rarely stored in a structured, comparable form.
- Generic AI assistants have limited durable, validated learning state.
- Self-reported confidence is an unreliable proxy for competence.
- The user often chooses what to study based on recency, anxiety or convenience rather than evidence.

## 2.4 Jobs to be done

- When I learn a difficult technical concept, help me check whether I can explain it without looking.
- When I revisit a topic, show me what I previously misunderstood.
- When I prepare for a senior interview, identify the skills that matter and help me practise them.
- When I complete a practical exercise, evaluate my reasoning against a transparent rubric.
- When I have limited time, prioritise the next practice activity with the highest expected learning value.
- When I return after a break, restore my learning context without forcing me to reconstruct it.

## 2.5 Who it is for

**For:**
- Software engineers with 3–10 years of experience.
- Engineers preparing for senior, staff-track or specialist technical interviews.
- Engineers learning system design, backend engineering, databases, distributed systems fundamentals or applied AI engineering.
- Self-directed learners who already use multiple learning resources and want a more disciplined feedback loop.

**Not initially for:**
- K–12 learners or general school exam preparation.
- Universities requiring a full LMS.
- Employers seeking employee surveillance or automated performance ratings.
- Users looking for a course marketplace.
- Users who want an AI to complete assignments or interviews on their behalf.
- Every professional domain at launch.

---

# 3. Product Vision

## 3.1 Vision

Become the personal system people use to turn learning into demonstrable capability throughout their careers.

## 3.2 Mission

Help independent learners understand what they know, discover what they do not know, practise what matters and build evidence of improvement.

## 3.3 Product thesis

If Mindtrace connects source material, memory, retrieval practice, applied exercises and recurring errors into one transparent learner model, then learners will improve more consistently and return because the product helps them make progress—not because it generates more content.

## 3.4 Positioning

**For software engineers who want to grow beyond passive learning, Mindtrace is a personal skill-development system that connects what they study to what they can actually explain and do. Unlike notes, flashcards or mock-interview tools alone, Mindtrace maintains a longitudinal picture of their skills, mistakes and demonstrated progress.**

## 3.5 Product principles

1. Evidence over activity.
2. Practice over passive consumption.
3. Explainability over opaque scores.
4. User control over hidden memory.
5. Focused workflows over feature sprawl.
6. Reliable fundamentals over fashionable AI architecture.

## 3.6 Roadmap horizon

| Horizon | Product outcome |
|---|---|
| 6 months | Validate a narrow technical learning path, core recall/practice loop and paid demand |
| 12 months | Add more competency tracks, better assessments, source integrations and mobile-friendly practice |
| 2 years | Build a broad personal skill graph, richer project-based evidence and carefully chosen integrations |
| 3+ years | Become a durable personal learning record across career transitions and skill domains, if retention and outcomes justify expansion |

---

# 4. Business Model and Goals

## 4.1 Model

B2C subscription with a free entry tier and paid individual plans. Avoid enterprise complexity until consumer retention and unit economics are established.

## 4.2 Initial pricing hypotheses

These are test prices, not validated willingness-to-pay.

| Plan | Indicative price | Limits / entitlements |
|---|---:|---|
| Free | $0 | One active skill path, limited AI practice, basic review queue, limited source imports |
| Plus | $8–12/month | Multiple skill paths, higher AI practice allowance, full history, adaptive plan |
| Pro | $15–20/month | Advanced practical assessments, voice practice, deeper analytics, exports and larger usage allowance |
| Annual | 15–25% discount hypothesis | Annual prepaid subscription |
| Lifetime | Do not offer initially | Creates long-term AI and support cost exposure |

Localised INR pricing should be tested separately. Do not promise unlimited AI usage.

## 4.3 Trial and billing

- Free plan is the default; avoid requiring a card for initial activation.
- Optional 7-day paid-feature trial only after the user experiences the core loop.
- Upgrade/downgrade takes effect according to the payment provider's subscription rules.
- Cancellation stops renewal; access remains until the paid-through date unless payment provider/legal requirements dictate otherwise.
- Failed payments trigger provider-managed retries and clear user notifications.
- Refund policy must be published and comply with applicable consumer law.
- Store entitlements server-side; never trust client-supplied plan names.

## 4.4 North Star Metric

**Weekly Demonstrated Skill Progress (WDSP).**

A learner counts once in a week when:
1. They complete a qualifying assessment or practical task.
2. The task has a defined rubric and minimum evidence threshold.
3. The result is comparable with a prior baseline or prior attempt.
4. The improvement exceeds a pre-defined threshold or the user demonstrates a previously unproven competency.
5. The result is not solely self-reported.

Report the numerator and eligible active-learner denominator. Do not inflate WDSP by lowering assessment difficulty.

## 4.5 Supporting KPIs

**Product:** activation, time to first recall, first applied task completion, weekly active learners, D7/D30 retention, review completion, practice completion, source-to-practice conversion, skill-path completion.

**Learning quality:** delayed recall accuracy, transfer-task performance, repeated-error rate, confidence calibration, rubric inter-rater agreement, assessment reliability.

**Business:** MRR, ARR, ARPU, trial-to-paid, free-to-paid, churn, refund rate, failed payments, gross margin, CAC, payback period and LTV.

## 4.6 Initial success thresholds (hypotheses)

These are internal gates, not external benchmarks:
- 60% of new users complete a baseline and first practice activity within 24 hours.
- 35% of activated users return for a second learning session within 7 days.
- 25% of activated users complete at least one applied task in their first 14 days.
- 20% of users who reach a meaningful outcome convert to paid within the first 60 days.
- At least 70% of assessed outputs in the golden evaluation set meet the minimum rubric-quality threshold.
- AI and infrastructure variable cost remains below 25% of subscription revenue at the target usage mix.

Revisit these after the first 100–200 activated users; do not treat them as forecasts.

---

# 5. User Personas

## Persona A — Interview-focused senior engineer (primary)

- **Background:** 3–10 years of software engineering experience; preparing for senior roles.
- **Goals:** improve system design, backend, coding explanation and technical communication.
- **Pain:** studies across videos, blogs, notes and question banks but cannot tell what is retained.
- **Workflow:** identifies a target role, studies topics, solves problems, attends mock interviews.
- **Technical proficiency:** high.
- **Buying authority:** individual.
- **Usage:** 4–6 sessions per week during active preparation.
- **Objections:** another study app, generic AI feedback, inaccurate scoring, time overhead.
- **Success:** can independently explain and apply target concepts under interview-like constraints.

## Persona B — Continuous-growth engineer

- **Background:** employed engineer who wants to improve one or two capabilities while working.
- **Goals:** learn a new technical area and apply it at work or in a personal project.
- **Pain:** inconsistent study schedule and poor recall after completing a course.
- **Usage:** 2–4 sessions per week.
- **Success:** applies a skill in a project and can explain trade-offs.

## Persona C — Returning learner

- **Background:** has paused learning for weeks or months.
- **Goals:** resume without reconstructing all prior context.
- **Pain:** lost notes, forgotten progress and uncertainty about where to restart.
- **Success:** receives a short, evidence-based re-entry plan.

Do not build manager, teacher, classroom or enterprise-admin personas into the first release.

---

# 6. Complete Feature Map

Priority definitions: P0 required for launch; P1 important after core validation; P2 future; Out of scope means explicitly excluded from the current product direction.

| Feature | Priority | Purpose / acceptance outcome |
|---|---|---|
| Account and profile | P0 | Secure account, learner preferences and timezone |
| Skill goal setup | P0 | User chooses role/goal, timeframe and available study time |
| Competency map | P0 | Shows skills, subskills, prerequisites and evidence status |
| Baseline assessment | P0 | Establishes initial evidence and uncertainty |
| Learning source import | P0 | Paste text/URL and upload PDF within supported limits |
| Source provenance | P0 | Every extracted concept retains source and location metadata |
| Concept extraction | P0 | User can review/edit extracted concepts before saving |
| AI tutor | P0 | Explains concepts using approved learner sources and curated knowledge |
| Active recall | P0 | Questions require unaided retrieval before revealing explanation |
| Review scheduler | P0 | Schedules review based on performance and elapsed time |
| Practical exercises | P0 | Includes explain/design/diagnose/implement task types |
| Error memory | P0 | Captures misconception, evidence, severity and recurrence |
| Progress timeline | P0 | Shows attempts, changes and evidence over time |
| Adaptive next-step recommendation | P0 | Recommends one clear next action with reason |
| User memory controls | P0 | Inspect, correct, export and delete stored learning memory |
| Skill Passport | P1 | Evidence-based summary of demonstrated competencies |
| Voice practice | P1 | Spoken explanation and interview-style practice |
| Browser extension | P1 | Save source material from supported pages |
| GitHub project evidence | P2 | Link user-approved repositories/projects to skill evidence |
| Calendar integration | P2 | Optional study scheduling |
| Mobile native apps | P2 | Only after mobile web usage validates demand |
| Social leaderboards | Out of scope | Distracts from individual mastery and adds privacy issues |
| Covert live interview assistance | Out of scope | Integrity and platform-policy risk |
| Course marketplace | Out of scope | Not core differentiation |
| Employer surveillance dashboard | Out of scope | Conflicts with personal learner trust |

## 6.1 Feature requirements: baseline assessment

**Purpose:** understand the user's starting capability rather than infer it from profile or content history.

**Inputs:** selected skill path, time limit, task type, optional confidence rating.

**System behaviour:**
- Select a balanced sample across competency subskills.
- Mix explanation, scenario diagnosis and practical reasoning.
- Avoid revealing answers before submission.
- Record answer, rubric dimensions, model version, rubric version and confidence.
- Mark insufficient evidence as unknown rather than weak.
- Provide a baseline report with uncertainty.

**Acceptance criteria:**
- User can complete or pause a baseline.
- Results are stored immutably as an attempt record.
- The user can inspect the rubric and feedback.
- No baseline score is generated from a profile-only questionnaire.

## 6.2 Feature requirements: learning source ingestion

**Supported initial inputs:** pasted text, public article URL where legally/technically accessible, PDF upload. YouTube transcript ingestion is P1 and must respect platform terms and copyright.

**Pipeline:** validate → extract → normalise → segment → classify concepts → link source spans → deduplicate → user review → commit.

**Rules:**
- Do not bypass paywalls or access controls.
- Do not store full copyrighted source content unless the user has rights and the storage basis is appropriate.
- Store user notes, permitted excerpts, metadata and source references.
- Show extraction failures and partial results.
- Never silently create hundreds of flashcards.
- User approves concepts before they enter their learning graph.

## 6.3 Feature requirements: active recall and review

- Ask before showing hints or answers.
- Support free-text, short answer, compare/contrast, diagram explanation and scenario reasoning.
- Record correctness, rubric dimensions, response latency where useful, confidence and hint usage.
- Distinguish recognition from recall.
- Schedule a review using an initial deterministic scheduler; do not claim neuroscientific precision.
- Allow user to mark an item ambiguous or incorrect.
- Repeatedly failed items should trigger a different teaching or practice approach, not endless identical questions.

## 6.4 Feature requirements: practical assessment

- Task has a skill mapping, difficulty, expected time, rubric and evaluation evidence.
- Task types include design a system, diagnose a failure, critique an architecture, explain a trade-off and implement a bounded exercise.
- Where code execution is introduced, run in an isolated sandbox with strict resource and network controls; this is P1/P2, not required for the first text-based practical assessment.
- Feedback must cite specific portions of the user's response or artefact.
- A model score is provisional until quality gates and evaluation tests pass.
- Users can challenge or correct feedback.

## 6.5 Feature requirements: learner memory

Five distinct memory categories:

| Memory type | What it stores | Example |
|---|---|---|
| Semantic | Concepts and relationships the learner has studied | Understands cache invalidation strategies |
| Episodic | Specific learning/practice events | Failed to explain write-through vs write-back on 12 Oct |
| Procedural | Repeatable methods or approaches | Uses a consistent system-design decomposition sequence |
| Error | Misconceptions and recurring mistakes | Confuses replication with partitioning |
| Progress | Evidence and changes over time | Improved trade-off explanation rubric from 2/5 to 4/5 |

Memory must include source, confidence, created/updated time, user correction history and deletion status. Derived memory is not an unquestionable fact.

---

# 7. End-to-End User Lifecycle

1. Discovery through technical learning content, search, referrals or engineering communities.
2. Landing page explains the learning-to-proof workflow.
3. Signup using email or supported OAuth.
4. Onboarding asks role, target skill, goal timeframe and weekly time budget.
5. User selects one launch skill path.
6. Baseline assessment establishes starting evidence.
7. Dashboard recommends the first learning action.
8. User imports or opens a learning source.
9. Mindtrace extracts concepts; user reviews and approves.
10. User completes active recall.
11. User attempts an applied task.
12. Mindtrace records evidence and errors.
13. Scheduler proposes the next review/practice session.
14. Returning user resumes from current skill state.
15. User sees progress and may upgrade when reaching a meaningful usage limit.
16. User can export or delete their data at any time.

## 7.1 First-value target

Within the first session, the user should:
- Select a concrete skill goal.
- Complete a short baseline.
- Receive a useful gap summary.
- Complete one recall or applied practice action.
- Understand why Mindtrace recommended the next action.

Target time-to-first-value: 10–20 minutes. Validate through usability testing.

---

# 8. Information Architecture

**Primary navigation**
- Today
- My Skills
- Learn
- Practice
- Memory
- Progress
- Settings

**Page hierarchy**
```text
/
├── product
├── pricing
├── security-and-privacy
├── login
├── signup
└── app
    ├── today
    ├── onboarding
    ├── skills
    │   └── [skillId]
    │       ├── overview
    │       ├── concepts
    │       ├── practice
    │       └── evidence
    ├── learn
    │   ├── sources
    │   └── [sourceId]
    ├── practice
    │   ├── review
    │   ├── assessment
    │   └── [attemptId]
    ├── memory
    ├── progress
    ├── billing
    └── settings
        ├── profile
        ├── privacy
        ├── notifications
        ├── sessions
        └── export-and-delete
```

Resource ownership is always user-scoped. Do not introduce shared workspaces or teams in the MVP.

---

# 9. Critical User Flows

## 9.1 Signup to first value

**Trigger:** user clicks Start learning.  
**Preconditions:** none.  
**Steps:** signup → verify email → choose role/goal → choose skill path → select time budget → baseline → first recommended action.  
**System:** persists onboarding state after each step; supports resume.  
**Outcome:** user sees an actionable skill plan.  
**Failure:** if assessment generation fails, use a pre-authored baseline set.  
**Recovery:** user can retry or continue with the deterministic fallback.

## 9.2 Import a source

**Trigger:** user pastes a URL, text or uploads a PDF.  
**Preconditions:** authenticated user; quota available; file passes validation.  
**Steps:** upload/submit → asynchronous processing → extraction status → concept preview → user approval → graph commit.  
**Failure:** unsupported URL, OCR failure, extraction timeout, duplicate source, unsafe file.  
**Recovery:** explain failure, retain original upload only according to retention rules, allow retry or manual text input.

## 9.3 Practice and record an error

**Trigger:** user starts a due review or practice task.  
**Steps:** present prompt → capture response → evaluate → show evidence-linked feedback → user accepts/challenges → update attempt and error history → schedule next action.  
**Failure:** LLM timeout or invalid structured output.  
**Recovery:** preserve response, retry evaluation safely, or show a pending result; never discard the user's work.

## 9.4 Delete learning memory

**Trigger:** user deletes a concept, source or account.  
**Steps:** confirmation → mark deletion request → delete primary records and derived embeddings → enqueue object-storage cleanup → record completion state.  
**Important:** deletion from primary storage does not imply immediate deletion from immutable backups; publish backup expiry window and ensure deleted data is not restored into active systems after recovery.

---

# 10. Screen Specifications and Text Wireframes

## 10.1 Today dashboard

```text
┌────────────────────────────────────────────────────────────┐
│ Mindtrace                         Search   Profile          │
├──────────────┬─────────────────────────────────────────────┤
│ Today        │ Good morning                                 │
│ My Skills    │ Your next best action                        │
│ Learn        │ ┌─────────────────────────────────────────┐  │
│ Practice     │ │ Explain cache invalidation              │  │
│ Memory       │ │ 8 min · Backend fundamentals             │  │
│ Progress     │ │ Why: last attempt missed 2 key trade-offs │  │
│              │ │ [Start practice]                          │  │
│              │ └─────────────────────────────────────────┘  │
│              │ Due reviews · Skill gaps · Recent evidence   │
│              │                                             │
│              │ Current goal: Senior backend engineer       │
│              │ Skill map: System design / Databases / APIs │
└──────────────┴─────────────────────────────────────────────┘
```

**States:** new user empty state; active plan; no due reviews; offline; AI provider degraded; assessment pending.

## 10.2 Skill detail

- Skill name and definition.
- Competency map with status: not assessed, emerging, developing, demonstrated, needs review.
- Evidence count and latest attempt.
- Concepts and prerequisites.
- Next recommended action and explanation.
- Recent mistakes.
- User can dispute a competency status.

## 10.3 Source detail

- Source title, type, URL/file metadata and import date.
- Extraction status.
- Extracted concept list with confidence and source location.
- Approve/edit/reject actions.
- Linked practice items.
- Delete source and choose whether to retain user-authored notes where legally/technically appropriate.

## 10.4 Practice session

- One task at a time.
- No answer reveal before submission.
- Optional timer and confidence rating.
- Save draft response.
- Submit.
- Feedback with rubric breakdown, evidence quotes, uncertainty and next step.
- Challenge feedback control.

## 10.5 Progress

- Timeline of assessments and attempts.
- Skill-level evidence history.
- Recall retention trend.
- Repeated error trend.
- Practice distribution.
- No gamified mastery percentage unless the methodology is explained and validated.

---

# 11. Frontend Architecture

**Recommendation:** Next.js App Router + TypeScript + React. Use a modular frontend; avoid premature micro-frontends.

- Server Components for data-heavy read views where suitable.
- Client Components for practice interaction, editor, timers and interactive visualisations.
- TanStack Query for client-side server state where needed.
- Zod for shared request/form schemas.
- React Hook Form for complex forms.
- Accessible component primitives (e.g. shadcn/ui) with a distinctive Mindtrace design system.
- Rich-text editor only where user-authored notes require it; avoid building a full Notion clone.
- Uploads use signed URLs and resumable transfer for larger files.
- Route-level error boundaries and retry controls.
- Autosave practice drafts with explicit saved state.

**Project structure**
```text
apps/web/
  app/
  components/
  features/
    onboarding/
    skills/
    sources/
    practice/
    memory/
    progress/
    billing/
  lib/
    api/
    auth/
    analytics/
    validation/
  styles/
packages/
  contracts/
  ui/
  types/
```

---

# 12. UI/UX and Design System

**Desired feel:** focused, intelligent, calm, premium, technical and trustworthy.

Design should make the next learning action obvious. Avoid a noisy gamification dashboard.

- Use a restrained neutral palette with one strong accent.
- Avoid generic purple/pink AI gradients.
- Typography should prioritise long-form technical content and code readability.
- Use compact cards, clear hierarchy, meaningful whitespace and strong focus states.
- Distinguish evidence-backed status from AI suggestions.
- Avoid confetti, streak pressure and manipulative urgency.
- Provide reduced-motion support.
- Use skeletons only for genuinely loading content; show progress for longer AI jobs.

Motion should communicate state transitions, not decorate every interaction.

---

# 13. Branding

**Brand personality:** rigorous, encouraging, intellectually honest, calm, precise.

**Logo direction:** an abstract trace/path connecting nodes or a progressive mark; avoid a brain icon or generic robot.

**Copy principles:**
- Say “You have evidence of…” rather than “You have mastered…” unless the mastery claim is justified.
- Say “This answer missed the failure-recovery trade-off” rather than “Bad answer.”
- Explain why a review is due.
- Avoid claims such as “learn 10x faster” without controlled evidence.

Example hero:
> **Turn what you study into what you can do.**  
> Build durable technical skills through active recall, realistic practice and feedback that remembers where you need to improve.

CTA: **Build my skill plan**

---

# 14. Advanced UI and Motion

Use:
- Subtle progress transitions on competency maps.
- Clear processing stages for source ingestion.
- Expandable evidence cards.
- Lightweight graph visualisation only when it clarifies prerequisites or relationships.
- A focused practice-session interface with minimal distractions.

Do not render a complex animated knowledge graph as the main dashboard. Provide a searchable list and graph view only when users have enough connected concepts to make the graph useful.

---

# 15. Design References

Use patterns, not copies:
- Linear: clear navigation, command/search patterns and restrained visual hierarchy.
- Notion: flexible content presentation, but do not reproduce its general-purpose workspace.
- Brilliant: structured interactive learning.
- Anki: low-friction review queue and scheduling transparency.
- Stripe: billing clarity and operational trust.
- shadcn/ui: accessible primitives and composability.

Every animation or visualisation must justify its performance and accessibility cost.

---

# 16. Responsive and Cross-Browser Design

- Desktop is the primary environment for technical source review and practical tasks.
- Mobile web supports review, short recall, progress inspection and voice practice.
- Tablet uses a single-column layout for practice and a two-pane layout for source review where space permits.
- Support current and previous major versions of Chrome, Safari, Firefox and Edge.
- Handle slow networks: persist drafts locally where safe, queue uploads, expose retry and avoid losing responses.
- Offline mode is not a launch requirement; cached read-only review content may be evaluated later.
- Do not store sensitive long-term learner records in unencrypted local storage.

---

# 17. Accessibility

Target WCAG 2.2 AA for core workflows.

- Keyboard access for all navigation, review and practice controls.
- Screen-reader labels for charts, progress states and rubric dimensions.
- Semantic headings and landmarks.
- Visible focus indicators.
- Contrast-compliant text and status indicators; never rely on colour alone.
- Captions/transcripts for audio content.
- Reduced motion.
- Accessible error announcements.
- Minimum 44×44 CSS pixel touch targets where practical.
- Allow additional time or disable timers for practice where timing is not the competency being assessed.

---

# 18. SEO and Public Website

Public pages:
- Homepage
- How Mindtrace works
- Skill paths
- Pricing
- Privacy and security
- Methodology: how progress is assessed
- Blog / technical learning guides
- FAQ
- Contact and support

SEO must target specific user problems and technical skill topics, not mass-produce thin AI-generated pages. Publish methodology and limitations transparently. Add canonical URLs, sitemap, robots.txt, Open Graph and relevant structured data.

---

# 19. Backend Architecture

## 19.1 Recommended launch architecture

A **modular monolith** with asynchronous workers.

```text
Browser
  │
  ▼
CDN / WAF
  │
  ▼
Next.js web application
  │ HTTPS
  ▼
Backend API (FastAPI modular monolith)
  ├── Identity / profile
  ├── Skill plans / competency map
  ├── Sources / ingestion
  ├── Concepts / learner memory
  ├── Practice / assessments
  ├── Scheduling
  ├── Recommendations
  ├── Billing / entitlements
  └── Analytics events
       │
       ├── PostgreSQL (+ pgvector only where justified)
       ├── Object storage
       ├── Queue / worker
       └── AI provider adapter
```

Why: one deployable API and one primary relational database reduce operational overhead. Separate workers isolate expensive or slow ingestion and evaluation tasks. Split services only when scaling, security or team ownership justifies it.

## 19.2 Backend modules

Each module owns its business rules and repository boundary. Avoid cross-module direct database writes; use explicit service interfaces or domain events.

## 19.3 Background jobs

- Source extraction and OCR.
- Concept extraction and deduplication.
- Embedding generation if semantic retrieval is enabled.
- Practice evaluation.
- Scheduled review generation.
- Data export and deletion.
- Billing webhook processing.
- Email delivery.

Jobs must be idempotent, retryable and observable.

---

# 20. API Architecture

Use REST JSON APIs under `/api/v1`. All endpoints require authentication except public metadata and auth flows.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Authenticate |
| GET | `/me` | Current profile and entitlements |
| PATCH | `/me` | Update profile/preferences |
| POST | `/onboarding/complete` | Save onboarding state |
| GET | `/skill-paths` | List available paths |
| POST | `/goals` | Create learner goal |
| GET | `/skills` | List user's skill states |
| GET | `/skills/{id}` | Skill detail and evidence |
| POST | `/assessments` | Create baseline/practice assessment |
| POST | `/assessments/{id}/submit` | Submit response |
| GET | `/assessments/{id}/result` | Retrieve evaluation |
| POST | `/sources` | Create source/import job |
| GET | `/sources/{id}` | Source processing status |
| POST | `/sources/{id}/approve-concepts` | Approve extracted concepts |
| GET | `/reviews/due` | Due review queue |
| POST | `/reviews/{id}/submit` | Submit recall response |
| GET | `/memory` | Search/view learner memory |
| PATCH | `/memory/{id}` | Correct user-editable memory |
| DELETE | `/memory/{id}` | Delete memory item |
| GET | `/progress` | Progress analytics |
| POST | `/billing/checkout` | Create checkout session |
| POST | `/webhooks/billing` | Verify/process billing events |
| POST | `/exports` | Start data export |
| POST | `/account/deletion` | Request account deletion |

**Conventions**
- Cursor pagination for event/attempt history.
- Maximum page size 100.
- Standard error body: `{ "error": { "code": "...", "message": "...", "request_id": "..." } }`.
- Use idempotency keys for job creation, checkout and webhook processing.
- Return `202 Accepted` for asynchronous jobs.
- `429` includes `Retry-After`.
- Do not expose internal stack traces or provider errors.

---

# 21. Authentication and Authorization

- Use a managed or well-maintained authentication implementation; do not write password/session cryptography from scratch.
- Email verification required before sensitive account operations.
- OAuth providers may be added after email signup is stable.
- Passwords, if managed locally, must use Argon2id with current recommended parameters.
- Secure, HttpOnly, SameSite cookies; rotate sessions after authentication and privilege changes.
- Session revocation and logout-all-devices.
- Rate-limit login, signup, password reset and verification.
- MFA is P1 for users and mandatory for internal admin access.
- User owns their personal account and data; no organisation-level RBAC in the consumer MVP.
- Every resource query must enforce `user_id` ownership server-side.
- Admin access is separate, least-privilege and audited.

---

# 22. Bot Protection and Abuse Prevention

- Signup velocity limits per IP and account.
- Email verification and disposable-email risk checks.
- Login and password-reset throttling.
- CAPTCHA/Turnstile on suspicious traffic, not every interaction by default.
- Detect repeated AI-generation abuse and automated scraping.
- Limit file uploads and URL fetches.
- Admin suspension and abuse review workflow.
- Never use client-only quotas.

---

# 23. Rate Limiting and Quotas

Initial configurable limits (tune using production data):
- Authentication: 5 failed attempts per 15 minutes per account plus IP-based protection.
- Source import: 10 new imports/hour on free tier; higher paid allowance.
- AI practice generation: plan-based daily/monthly quotas.
- Evaluation: concurrent job limit per user.
- Search: 60 requests/minute per authenticated user.
- Export/deletion: one active job of each type per user.

Use Redis-backed distributed rate limiting when multiple API instances are deployed. Return remaining quota and reset time. Do not make a quota reset dependent on client clocks.

---

# 24. API Security

- No public user API keys in MVP.
- Internal provider credentials remain server-side.
- Verify webhook signatures and timestamps.
- Enforce request size limits and schema validation.
- Use idempotency keys for state-changing operations.
- Apply endpoint-specific scopes if a public API is introduced later.
- Do not expose an API playground or SDK until there is an actual developer use case.

---

# 25. Frontend Data and Secret Protection

- No database credentials, LLM keys, payment secrets or signing keys in browser bundles.
- No PII in URL query parameters.
- Avoid persistent sensitive local storage.
- Return only fields needed by the current view.
- Enforce authorization in the API, never only in the UI.
- Disable production source maps or protect them appropriately.
- Redact secrets and sensitive learning content from client error telemetry.

---

# 26. Input Validation and Application Security

- Pydantic request/response schemas on API boundaries.
- Zod validation on frontend forms.
- Validate file MIME by content, not filename alone.
- Enforce URL allowlists and block private/link-local IP ranges to prevent SSRF.
- Protect against SQL injection using parameterised queries/ORM.
- Escape user content in rendered HTML.
- Sanitize imported HTML and markdown.
- Restrict archive extraction and decompression ratios.
- Enforce body, text, PDF page and processing-time limits.
- Protect against path traversal and unsafe file names.
- Treat imported documents and retrieved text as untrusted input.

---

# 27. Browser Security

- HTTPS everywhere and HSTS.
- Strict Content Security Policy.
- `X-Content-Type-Options: nosniff`.
- Appropriate `Referrer-Policy` and `Permissions-Policy`.
- CORS allowlist for production origins.
- CSRF protection for cookie-authenticated state-changing endpoints.
- Clickjacking protection with CSP `frame-ancestors`.
- Secure cookie attributes.
- Do not request microphone or camera permissions until a voice feature is explicitly invoked.

---

# 28. Database Architecture

Use PostgreSQL as the system of record. Use `pgvector` only if semantic retrieval is shown to improve retrieval quality over PostgreSQL full-text and metadata filters. Do not introduce a separate vector database at launch.

## 28.1 Core entities

| Table | Important fields |
|---|---|
| users | id, email, email_verified_at, created_at, status |
| profiles | user_id, display_name, timezone, role, preferences_json |
| goals | id, user_id, title, target_date, status, weekly_time_budget |
| skill_paths | id, slug, title, version, published_at |
| competencies | id, path_id, parent_id, slug, definition, rubric_json |
| user_skills | id, user_id, competency_id, status, confidence, updated_at |
| sources | id, user_id, type, title, source_uri, object_key, status, checksum |
| source_segments | id, source_id, segment_index, text_ref, page_or_timestamp, metadata |
| concepts | id, user_id, title, definition, concept_type, status |
| concept_edges | id, user_id, from_concept_id, to_concept_id, relation |
| concept_sources | concept_id, source_segment_id, relation, confidence |
| practice_items | id, user_id, competency_id, concept_id, type, prompt, rubric_version |
| attempts | id, user_id, practice_item_id, response_ref, status, submitted_at |
| evaluations | id, attempt_id, rubric_version, result_json, model_version, confidence |
| learner_memories | id, user_id, memory_type, content_json, provenance_json, confidence, status |
| error_patterns | id, user_id, competency_id, error_code, description, severity |
| attempt_errors | attempt_id, error_pattern_id, evidence_json |
| review_states | id, user_id, practice_item_id, due_at, stability, difficulty, last_result |
| review_events | id, user_id, practice_item_id, result, confidence, occurred_at |
| jobs | id, user_id, type, status, idempotency_key, attempts, error_code |
| subscriptions | id, user_id, provider, provider_customer_id, status, plan_id |
| usage_events | id, user_id, feature, units, cost_usd, occurred_at |
| audit_events | id, actor_id, action, target_type, target_id, metadata, occurred_at |

## 28.2 Data rules

- UUID primary keys.
- UTC timestamps; user timezone is a display/scheduling preference.
- Foreign keys and check constraints for valid state transitions.
- Unique constraints on provider event IDs, source checksums per user where appropriate, and idempotency keys.
- Index `(user_id, created_at DESC)` for timeline tables.
- Index `(user_id, due_at)` for review queue.
- Index `(user_id, competency_id)` for skill state.
- Full-text index on user-approved concept text.
- Tenant isolation is user-level; every query includes owner scope.
- Use soft deletion only when necessary for recoverability; deletion jobs must permanently remove eligible data according to published retention rules.
- Migration files are versioned and tested against a production-like dataset.
- Enable automated backups and point-in-time recovery according to selected provider capability.

---

# 29. Caching

Cache only data with a clear invalidation rule.

- Public skill-path catalogue: CDN/application cache, 5–15 minute TTL.
- User dashboard summary: short TTL (30–90 seconds) or cache invalidation on relevant events.
- Competency rubric versions: immutable, long-lived cache.
- Do not cache private AI responses across users.
- Cache keys include user ID and resource version where applicable.
- Redis failure should fall back to database reads for non-critical cache use.
- Track hit rate, miss rate, evictions and stale-read incidents.

---

# 30. Background Processing

Use a durable queue with a worker process. Redis-backed queue is acceptable for the initial deployment if persistence, retries and dead-letter handling are configured; a managed queue is preferable if operational burden becomes high.

Job envelope:
`job_id, user_id, job_type, payload_ref, idempotency_key, attempt, created_at, trace_id`

- Retry transient network/provider failures with exponential backoff and jitter.
- Do not retry invalid files or schema errors indefinitely.
- Dead-letter after bounded retries.
- Cap per-user concurrency.
- Provide job status and retry action.
- Ensure duplicate delivery does not duplicate concepts, billing events or usage charges.

---

# 31. Error Handling

- Typed domain errors and central exception middleware.
- Stable error codes and request IDs.
- Separate user-facing explanation from internal diagnostic data.
- Retry only transient failures.
- Preserve practice responses if evaluation fails.
- Record job failure reason without logging raw sensitive content.
- Alert on elevated failure rates and stuck jobs.

---

# 32. Reliability Engineering

- Readiness and liveness endpoints.
- Explicit timeouts for database, object storage, AI provider and external fetch.
- Retry with jitter only for idempotent operations.
- Circuit breaker around AI provider calls.
- Graceful degradation: source import can queue while AI provider is down; existing review items remain usable; saved attempts remain accessible.
- Graceful worker shutdown and queue visibility timeout.
- Backpressure when queue depth exceeds capacity.
- No dependency on a single AI provider for the entire product experience.

---

# 33. Failure-Mode Engineering

| Dependency/failure | Behaviour | Recovery/monitoring |
|---|---|---|
| PostgreSQL unavailable | Stop writes; show service issue; preserve client draft locally where safe | Health alert, retry with backoff, restore/PITR runbook |
| Redis unavailable | Bypass non-critical cache; pause queue submission if queue durability is not guaranteed | Alert, reconnect, replay safe jobs |
| Object storage unavailable | Keep import pending; do not mark source complete | Retry upload/process, verify checksum |
| LLM provider timeout | Preserve user response; show evaluation pending | Retry with bounded policy or fallback model |
| Embedding provider unavailable | Use keyword/full-text retrieval where possible | Reprocess embeddings later |
| Payment provider unavailable | Do not alter entitlements based on unverified state | Reconcile signed webhooks and provider API |
| Email provider unavailable | Queue transactional email | Retry and monitor delivery |
| Network interruption | Autosave response draft and show offline state | Resume on reconnect |

---

# 34. Idempotency and Concurrency

- Idempotency keys for source import, assessment submission, billing checkout and webhooks.
- Attempt submission is immutable after finalisation; corrections create a new attempt or an explicit appeal event.
- Lock review-state updates by `(user_id, practice_item_id)` or use optimistic versioning.
- Prevent two workers from processing the same ingestion job concurrently.
- Use database transactions for concept approval and source status transition.
- Use distributed locks only if database constraints/transactions cannot solve the race.

---

# 35. Storage and Files

- Private object storage buckets.
- Signed upload/download URLs with short expiry.
- Initial PDF limit: 25 MB and 200 pages (configurable after cost tests).
- Reject executables, encrypted PDFs that cannot be safely processed, malformed documents and unsupported MIME types.
- Malware scan uploaded files where supported.
- Encrypt objects at rest and in transit.
- Store checksum, file size, MIME, page count and processing status.
- Apply lifecycle policies to temporary extraction artefacts.
- User deletion triggers object deletion and embedding deletion.
- Never expose permanent public URLs for private source files.

---

# 36. Search

Search user-approved concepts, sources, practice history and skill names.

MVP:
- PostgreSQL full-text search.
- Filters by skill, source, memory type and date.
- Cursor pagination.
- Permission-aware queries scoped to current user.
- Search suggestions only after query history demonstrates value.

Semantic search may be added with pgvector if evaluation demonstrates better recall/precision. Measure Recall@k, MRR, nDCG and latency on a labelled query set. Do not add a vector database merely because the product uses AI.

---

# 37. Multi-Tenancy

No organisation or team tenancy in MVP. The security boundary is the individual user account.

Future organisation support must not be retrofitted by assuming users can see each other's data. Introduce explicit organisations, memberships, roles, tenant IDs, tenant quotas and audit trails only when an actual team product is validated.

---

# 38. AI / GenAI Architecture

## 38.1 AI use cases

1. Source concept extraction.
2. Explanation and tutoring.
3. Question and exercise generation.
4. Response evaluation against versioned rubrics.
5. Error classification.
6. Recommendation explanation.
7. Optional semantic retrieval.

## 38.2 AI should not own deterministic logic

Keep in application code:
- Authentication and authorization.
- Review scheduling state transitions.
- Billing entitlements.
- Quota enforcement.
- Evidence eligibility.
- Skill status rules.
- Deletion and retention.
- Rubric version selection.

## 38.3 Model strategy

Use a provider adapter with at least one primary model and a tested fallback for non-real-time tasks. Select models by measured quality, latency and cost on Mindtrace's own evaluation set. Do not hard-code model names throughout business logic.

Use smaller/cheaper models for classification and extraction only after quality validation. Use stronger models for complex assessment feedback where the quality gain justifies the cost.

## 38.4 Prompt architecture

- Version every production prompt.
- Store prompt ID, version, model, parameters and rubric version with each AI result.
- Use structured JSON output and server-side schema validation.
- Separate system instructions, task instructions, user content and retrieved source context.
- Treat source content as untrusted data, never as instructions.
- Do not include unnecessary user history in prompts.
- Maintain golden examples and regression tests.

## 38.5 RAG and retrieval

Retrieval is justified when tutoring needs to ground explanations in a user's approved sources or a curated technical knowledge base.

Pipeline:
`query → intent/skill filter → user permission filter → keyword + semantic retrieval → rerank → context budget → generation → citation validation`

Every cited source must map to a stored source segment. If no reliable source exists, say so. Do not fabricate page numbers, timestamps or URLs.

---

# 39. AI Gateway and Model Management

Start with an internal provider abstraction, not a separate gateway service.

Track per operation:
- Provider and model.
- Prompt version.
- Input/output tokens.
- Latency.
- Cost estimate and actual provider cost where available.
- Retry/fallback count.
- Structured-output validation result.
- User and feature attribution.
- Evaluation quality.

Implement model routing only when the evaluation dataset supports a meaningful quality/cost trade-off. A provider fallback must not silently change evaluation rubric or output schema.

---

# 40. RAG / Knowledge Systems

Initial content may consist of user-provided sources and a small curated skill-path knowledge base.

- Extract text and source metadata.
- Preserve page/section/timecode provenance.
- Chunk by semantic boundaries; do not use arbitrary fixed-size chunks as the only strategy.
- Store original source metadata separately from derived chunks.
- Embeddings are versioned by model.
- Re-embedding jobs are idempotent.
- Retrieval respects user ownership and source deletion.
- Track retrieval latency and source-grounded answer rate.
- Keep a keyword-search fallback.
- Do not ingest entire websites indiscriminately.

---

# 41. AI Memory

Memory types are specified in Section 6.5.

**Storage policy**
- Store only memory that improves a defined learning workflow.
- Separate raw attempt records from derived memory summaries.
- Preserve provenance and confidence.
- Let users inspect and correct derived memory.
- Use explicit retention settings for audio/video if introduced.
- Do not infer sensitive personal traits.
- Do not use learner content to train third-party models unless the user has explicitly consented and the legal basis is established.
- Deletion propagates to derived memory, embeddings and active indexes.

**Retrieval policy**
- Retrieve by current skill, task, recency and relevance.
- Exclude deleted, disputed or low-confidence memories by default.
- Do not retrieve unrelated personal context into an assessment.
- Explain which past attempts influenced a recommendation.

---

# 42. AI Guardrails and Security

- Prompt injection: imported source text is data, not instruction.
- Indirect prompt injection: strip/neutralise instruction-like content where feasible; isolate tool permissions.
- No autonomous external actions.
- Tool allowlist restricted to internal read-only retrieval and explicitly permitted ingestion operations.
- Validate every structured output.
- Detect unsupported citations.
- Avoid generating personal or sensitive inferences.
- Do not expose one user's source or memory to another.
- Human/user review before extracted concepts are committed.
- Evaluation results that affect skill progression must meet quality thresholds.
- User can flag an inaccurate evaluation.
- High-impact claims about job readiness must be qualified and evidence-linked.

---

# 43. AI Evaluation

Build a golden dataset before launch.

## Evaluation dimensions

| Task | Metrics |
|---|---|
| Concept extraction | Precision, recall, duplicate rate, provenance accuracy |
| Tutor answers | Groundedness, relevance, correctness, citation validity |
| Question generation | Ambiguity rate, coverage, difficulty calibration |
| Assessment grading | Agreement with expert rubric, dimension-level agreement, false-positive mastery |
| Error classification | Precision/recall by error category |
| Recommendations | Completion rate, usefulness rating, subsequent performance |
| Retrieval | Recall@k, MRR, nDCG, citation coverage |

Use expert-reviewed examples from the initial technical skill paths. Use at least two independent human raters for a subset of grading examples to estimate rubric consistency.

LLM-as-judge may help triage but cannot be the sole release gate. Track model and prompt regressions. Keep user-visible scores as coaching signals, not hiring decisions.

---

# 44. AI Observability

Trace each AI task with:
- Request ID and trace ID.
- User ID pseudonym or internal identifier.
- Feature and job type.
- Model/provider and prompt version.
- Token counts and latency.
- Retrieval source IDs (not unnecessary raw text).
- Validation result.
- Retry/fallback path.
- Cost estimate.
- Error category.

Do not log raw learner responses by default in general application logs. Store them in protected product data stores with access controls. Use sampled, redacted traces for debugging with explicit retention.

---

# 45. AI Cost and Performance

- Set per-feature token budgets.
- Limit source size and context length.
- Use async processing for source ingestion and long evaluations.
- Cache immutable skill-path content and deterministic outputs.
- Do not cache personalised answers across users.
- Batch embedding generation.
- Enforce plan-based quotas server-side.
- Track cost per activated user, weekly active learner and paid user.
- Alert on unusual spend per account and provider.
- Add kill switches for expensive AI features.
- Show users when they approach usage limits.

---

# 46. Product and Business Analytics

Track events:
- `signup_completed`
- `onboarding_started`
- `skill_path_selected`
- `baseline_started`
- `baseline_completed`
- `source_import_started`
- `source_import_completed`
- `concepts_approved`
- `recall_started`
- `recall_submitted`
- `practice_started`
- `practice_submitted`
- `evaluation_completed`
- `error_pattern_created`
- `recommendation_opened`
- `recommendation_completed`
- `skill_evidence_updated`
- `paywall_viewed`
- `checkout_started`
- `subscription_started`
- `subscription_cancelled`
- `data_export_requested`
- `account_deletion_requested`

Use event schemas with event ID, timestamp, user ID, session ID, source and properties. Do not put raw prompts, answer text or document content in analytics events.

Build activation funnels, D1/D7/D30 cohorts, retention by first-value action, source-to-practice conversion and paid conversion by acquisition channel.

---

# 47. Usage Metering

Meter:
- Source imports and pages processed.
- AI generations/evaluations.
- Input/output tokens.
- Voice minutes if launched.
- Storage consumed.
- Background job executions.
- Exports.

Usage records are append-only. Entitlement checks happen server-side. Provide a usage page showing current period, allowance, consumed units and reset date.

---

# 48. Billing and Payments

- Use a payment provider adapter so provider-specific events do not leak into business logic.
- Evaluate Stripe and a suitable India-capable provider for the launch geography and legal entity.
- Verify webhook signatures.
- Store provider customer/subscription IDs, plan, status and period dates.
- Maintain an internal entitlement table derived from verified provider events.
- Reconcile provider state periodically.
- Handle duplicate and out-of-order webhook events.
- Support cancellation, upgrade, downgrade, failed-payment grace period and refund records.
- Never grant paid entitlement from a frontend redirect alone.
- Display taxes and renewal terms clearly.

---

# 49. Admin and Operations Console

Internal-only console:
- User lookup by internal ID/email.
- Account status and subscription state.
- Usage and cost by feature.
- Source/job status.
- Failed job retry.
- AI provider health and model configuration.
- Prompt/rubric version visibility.
- Feature flags and quota configuration.
- User-reported evaluation issues.
- Account suspension and deletion status.

Support staff should not casually browse raw learning content. Access to user content requires a documented support reason and audited, time-limited privilege.

---

# 50. Audit Logging

Record:
- Login and session events.
- Password/email changes.
- Subscription and entitlement changes.
- Data export/deletion requests.
- Admin access to user records.
- Admin quota/provider changes.
- User memory edits/deletions.
- Security events.

Each event records actor, action, target, timestamp, result and request ID. Minimise PII and define retention.

---

# 51. Feature Flags and Experimentation

- Feature flags for new learning paths, voice practice, new assessment models and source types.
- Percentage rollout with kill switch.
- Experiment only on user-beneficial changes.
- Do not A/B test different grading standards without tracking rubric/model version and ensuring comparability.
- Log experiment assignment.
- Keep staging and production flags separate.

---

# 52. Notifications

MVP:
- Transactional email for verification, password reset, billing and account security.
- Optional review reminder with user-selected schedule.
- In-app notification for completed import/evaluation jobs.

No manipulative streak-loss messaging. Users control reminder frequency and can unsubscribe from non-essential notifications.

---

# 53. Infrastructure

**Initial deployment shape**
- Frontend: Vercel or equivalent managed Next.js hosting.
- API: managed container hosting such as Render/Railway or a small AWS deployment.
- Database: managed PostgreSQL with automated backups.
- Object storage: S3-compatible private bucket.
- Queue/cache: managed Redis only when asynchronous workload requires it.
- Monitoring: error tracking, structured logs, metrics and tracing.
- DNS/TLS/WAF: managed provider.

Choose based on operational simplicity and measured costs. Do not introduce Kubernetes at launch.

---

# 54. Networking

- Public traffic terminates at CDN/WAF.
- API service is not directly exposed to the database.
- Database accepts connections only from approved application/worker networks.
- Restrict outbound URL-fetching workers to prevent SSRF and data exfiltration.
- Use TLS for all service-to-service and provider connections.
- Separate production and staging credentials and networks.

---

# 55. Environment Strategy

Environments:
- Local: developer data and mock providers.
- Development: shared integration environment with synthetic data.
- Staging: production-like, isolated database and provider credentials.
- Production: real users and data.

Never copy production learner content into development. Use synthetic fixtures. Feature flags and secrets are environment-specific.

---

# 56. Secrets Management

- Secrets manager or protected deployment environment variables.
- No secrets in Git, frontend bundles, logs or issue trackers.
- Secret scanning in CI.
- Rotate provider keys and database credentials.
- Separate least-privilege credentials for API, workers and CI.
- Use short-lived cloud credentials where possible.

---

# 57. CI/CD

Pull request pipeline:
1. Formatting and lint.
2. Type checks.
3. Unit tests.
4. API contract tests.
5. Database migration validation.
6. Dependency and secret scanning.
7. Frontend build.
8. Backend build.
9. Integration tests against ephemeral services.

Deployment:
- Preview deployment per PR.
- Staging deploy after merge.
- Smoke tests.
- Production canary/gradual rollout where supported.
- Migration strategy must be backward-compatible.
- Rollback plan for application and database changes.
- Release tags and changelog.

---

# 58. Supply-Chain Security

- Commit lockfiles.
- Pin critical dependencies.
- Automated dependency scanning.
- License review.
- Secret scanning.
- Container image scanning if containerised.
- Generate SBOM for release artefacts when operationally feasible.
- Avoid unmaintained document parsers and browser extensions.
- Review transitive dependencies with access to uploaded files or URLs.

---

# 59. Observability

**Logs:** structured JSON, request ID, trace ID, module, error code, latency; redact PII and user content.

**Metrics:**
- API request rate, errors and latency.
- DB connections, query latency and slow queries.
- Queue depth, job age and retry count.
- Object storage errors.
- AI provider latency, errors and spend.
- Review and assessment completion.
- Billing webhook lag.

**Tracing:** API → DB → queue → worker → AI provider → result persistence.

Production failures should be diagnosable from central logs, metrics and traces without SSH access.

---

# 60. API Performance Budgets

Initial targets under expected launch load:
- Cached/read dashboard API: p95 < 400 ms.
- Standard authenticated API: p95 < 600 ms, excluding external providers.
- Search: p95 < 500 ms for normal personal datasets.
- Job submission acknowledgement: p95 < 300 ms.
- AI completion: asynchronous; show job status immediately and measure provider latency separately.

These are initial engineering budgets, not guarantees. Measure p50/p95/p99 and revise after load testing.

---

# 61. Frontend Performance

- Target good Core Web Vitals on public pages.
- Keep initial dashboard JS lean.
- Lazy-load graph visualisations and heavy editors.
- Virtualise long history/review lists.
- Optimise PDF previews and images.
- Avoid loading charting/graph libraries on every route.
- Track LCP, INP, CLS, TTFB and frontend errors.
- Use responsive images and CDN caching for public assets.

---

# 62. Scalability

**100 users:** one API deployment, managed Postgres, object storage, one worker process, basic metrics.

**1K users:** tune indexes and connection pooling, separate worker capacity, add Redis-backed quotas/cache if needed.

**10K users:** multiple stateless API instances, worker autoscaling, queue monitoring, partition high-volume event tables only if measured.

**100K users:** capacity planning, read replicas if read load warrants, dedicated ingestion/evaluation worker pools, improved search, cost-aware model routing.

**1M+ users:** redesign only from measured bottlenecks; evaluate partitioning, regional strategy, queue sharding and dedicated retrieval infrastructure. Do not build this architecture in the MVP.

---

# 63. Testing Strategy

- Unit: scheduler, skill state transitions, entitlement checks, memory provenance, error classification rules.
- Integration: database ownership boundaries, queue idempotency, object storage, billing webhooks, AI provider adapters.
- E2E: signup, onboarding, baseline, import, approve concepts, recall, practical task, progress, upgrade, export, deletion.
- AI regression: golden source extraction, tutor, question generation and grading datasets.
- Security: auth, IDOR, SSRF, prompt injection, file upload, quota bypass and cross-user retrieval.
- Load: review queue, dashboard, source import burst, assessment submission and queue backlog.
- Accessibility: keyboard, screen reader, contrast and reduced motion.
- Browser: Chrome, Safari, Firefox and Edge.

Prioritise coverage of security boundaries and core learner state transitions over an arbitrary coverage percentage.

---

# 64. Security Testing

- SAST and dependency scanning in CI.
- DAST against staging.
- Test horizontal and vertical privilege escalation.
- Attempt cross-user source/memory retrieval.
- Fuzz source URL and file inputs.
- Verify SSRF protections.
- Verify webhook signature and replay handling.
- Verify rate-limit enforcement.
- Test prompt injection in PDFs and webpages.
- Confirm user deletion removes active derived data.
- Conduct a pre-launch external security review if budget permits.

---

# 65. Data and API Quality

- Validate all external and AI-generated payloads.
- Contract-test frontend/API schemas.
- Test migration upgrade and rollback.
- Detect duplicate source ingestion.
- Validate graph edges do not cross users.
- Ensure rubric versions are immutable.
- Ensure attempt/evaluation lineage is complete.
- Verify cursor pagination does not skip or duplicate events.
- Validate timezone and daylight-saving behaviour for review schedules.

---

# 66. Data Privacy

- Maintain a data inventory and classification.
- Collect only data required for the learning workflow.
- Publish clear privacy and AI-processing policies.
- Explain what is sent to model providers.
- Offer export and deletion.
- Encrypt data in transit and at rest.
- Restrict employee access to user content.
- Do not sell learner data.
- Do not use private learning responses for model training without explicit consent.
- Determine applicable privacy and consumer obligations for each launch jurisdiction; obtain qualified legal review.
- Do not claim GDPR, SOC 2 or other compliance until implemented and independently verified where required.

---

# 67. Data Lifecycle

`Creation → Validation → Processing → Storage → Retrieval → Correction → Retention → Export/Deletion`

- Raw upload retained only as long as needed and as disclosed.
- User-authored notes and attempts follow account retention.
- Derived embeddings are deleted when their source/user record is deleted.
- Backups have documented expiry and restore controls.
- Export includes supported user-owned content and metadata in a portable format.
- Deletion job reports status and exceptions.

---

# 68. Disaster Recovery

Initial objectives:
- RPO target: 24 hours or better, depending on database backup capability.
- RTO target: 8 hours for initial consumer launch.
- Automated daily backups and point-in-time recovery if supported.
- Encrypt backups.
- Test restoration at least quarterly.
- Document database, object-storage and secret recovery.
- Ensure deletion tombstones prevent deleted data from reappearing after restore.
- Keep incident contacts and provider escalation paths documented.

---

# 69. SRE and Production Operations

Initial SLIs:
- API availability.
- Auth success rate.
- Job completion rate.
- Source ingestion success rate.
- Evaluation completion rate.
- p95 latency.
- Billing webhook processing delay.

Initial SLO hypotheses:
- 99.5% monthly API availability during early launch.
- 99% of valid asynchronous jobs complete or reach a visible terminal failure state within the defined job SLA.
- 99.9% of verified billing webhooks are processed or safely retried within 15 minutes.

Define error budgets and release freeze policy only after enough traffic exists to make them meaningful.

---

# 70. Alerting

Alert on:
- API 5xx rate and p95/p99 latency.
- Database connection saturation and storage.
- Queue backlog and oldest-job age.
- Source ingestion failures.
- AI provider outage and cost spike.
- Billing webhook processing delay.
- Failed backup or restore test.
- Suspicious login and quota abuse.
- Certificate expiry.

Each alert has severity, owner, runbook and expected response. Avoid alerts for every isolated transient error.

---

# 71. Third-Party Integrations

Launch dependencies:
- LLM provider(s).
- Object storage.
- Email provider.
- Payment provider.
- Error tracking/observability.
- Authentication provider if managed.

For each:
- Store credentials server-side.
- Define timeout, retry and fallback.
- Track latency, errors and cost.
- Review data-processing terms.
- Have a provider outage mode.
- Avoid making a non-essential integration a hard dependency for the core review workflow.

---

# 72. Webhooks

Billing webhooks:
- Verify signature and timestamp.
- Store provider event ID with unique constraint.
- Process asynchronously.
- Handle duplicate and out-of-order delivery.
- Reconcile subscription state against provider.
- Retry safely.
- Expose internal delivery status and manual replay to authorised operators.
- Never log payment secrets or full payment details.

---

# 73. Developer Experience

No public API or SDK is required for the consumer MVP. Maintain internal OpenAPI documentation, local setup instructions, architecture decision records, seed data and runbooks. Add public APIs only when integrations are validated as a customer need.

---

# 74. Enterprise Readiness

Not a launch requirement. Future evaluation only:
- Team skill paths.
- Cohort analytics.
- Admin controls.
- SSO/SAML and SCIM.
- Organisation billing.
- Audit logs.
- Data retention controls.
- Role-based access.
- LMS integration.

Do not divert initial engineering capacity into enterprise features.

---

# 75. Internationalisation

- Store timestamps in UTC and render in user timezone.
- Use locale-aware date, number and currency formatting.
- Design for Unicode from day one.
- Keep content language separate from UI locale.
- English is the initial content language.
- Additional languages require language-specific assessment rubrics and evaluation datasets; translation alone is insufficient.

---

# 76. Product Quality and UX States

Every major interaction must define:
- Loading and progress.
- Empty state.
- Active state.
- Success.
- Error.
- Retry.
- Partial success.
- Undo/correction where possible.
- Unsaved changes.
- Quota exhaustion.
- Provider outage.
- Offline/network interruption.
- Accessible announcement.

A failed AI evaluation must never erase the submitted response.

---

# 77. Performance and Load Testing

Test:
- 100 concurrent dashboard/review users.
- Bursts of source imports.
- Concurrent evaluation jobs.
- Large personal concept graphs.
- Long attempt histories.
- Queue outage and recovery.
- AI provider rate limits.
- Billing webhook bursts.

Measure p50/p95/p99, error rate, queue age, database connections, CPU/memory and cost per workflow. Load-test AI provider limits separately from application capacity.

---

# 78. Capacity Planning

Model:
- Active users and sessions per week.
- Average source imports/user/month.
- PDF pages processed.
- Recall and practice attempts/user/week.
- AI calls per workflow.
- Average tokens per call.
- Voice minutes if launched.
- Storage retained/user.
- Queue jobs and peak concurrency.

Use measured cohort data after beta. Set alerts on cost/user and cost/paid-user. Do not infer capacity from total registered accounts alone.

---

# 79. Cost Engineering

Cost buckets:
- Frontend/API hosting.
- PostgreSQL.
- Redis/queue.
- Object storage and egress.
- OCR/document parsing.
- Embeddings.
- LLM input/output tokens.
- Email.
- Payment processing.
- Observability.

Track unit cost per:
- Source imported.
- Concept approved.
- Recall session.
- Practical assessment.
- Weekly active learner.
- Paid subscriber.

Initial target: variable cost below 25% of subscription revenue at normal paid usage. If users exceed fair-use limits, apply transparent quotas or a higher tier rather than allowing unbounded AI spend.

---

# 80. Architecture Documentation

Maintain:
- System context and container diagram.
- Database ERD.
- API OpenAPI specification.
- Ingestion sequence diagram.
- Assessment/evaluation sequence diagram.
- Authentication and authorization flow.
- Data lifecycle diagram.
- AI retrieval and prompt flow.
- Deployment diagram.
- Threat model.
- Failure-mode table.
- Cost model.
- Backup and recovery runbook.

---

# 81. Architecture Decision Records

| Decision | Chosen direction | Alternatives | Reason / trade-off |
|---|---|---|---|
| Architecture | Modular monolith + workers | Microservices | Lower operating cost and easier iteration |
| Database | PostgreSQL | MongoDB, separate graph DB | Relational integrity for attempts, billing and ownership; graph relationships can be represented relationally initially |
| Vector search | pgvector only if validated | Dedicated vector DB | Avoid extra service and operational cost |
| Frontend | Next.js + TypeScript | SPA-only framework | SEO/public site and application in one stack |
| Backend | FastAPI modular API | All logic in Next.js, microservices | Clear AI/document-processing ecosystem and service boundaries |
| Queue | Managed queue or durable Redis-backed queue | Synchronous processing | Ingestion/evaluation can be slow and retryable |
| Auth | Managed or proven auth library | Custom auth | Reduce security implementation risk |
| AI | Provider adapter | Single hard-coded model | Allows evaluation-based model changes |
| Scheduling | Deterministic initial scheduler | LLM-selected review dates | Predictable, testable and explainable |

Record owner, date, alternatives, decision and revisit trigger for each ADR.

---

# 82. Security Threat Model

| Asset | Threat | Mitigation |
|---|---|---|
| Learner memory | Cross-user data exposure | User-scoped queries, authorization tests, optional RLS |
| Uploaded files | Malware or parser exploit | MIME validation, scanning, sandboxed parsing, size limits |
| URL ingestion | SSRF | Resolve/validate IPs, block private ranges, redirect limits, egress controls |
| AI prompts | Prompt injection | Treat source as untrusted, isolate tools, validate outputs |
| Practice responses | Privacy leak through logs/provider | Data minimisation, provider terms, redaction and access controls |
| Billing state | Forged webhook or replay | Signature verification, event ID uniqueness, reconciliation |
| Account | Credential stuffing | Rate limits, MFA option, suspicious-login controls |
| Admin console | Privilege abuse | MFA, least privilege, audit log, time-limited access |
| Deletion workflow | Data resurrected from backup | Tombstones, deletion replay after restore, backup expiry |

---

# 83. Admin and Control Plane

Provide safe controls for:
- Account suspension/reactivation.
- Usage and cost inspection.
- Queue/job retry.
- Provider health and kill switches.
- Prompt/rubric version inspection.
- Feature flag rollout.
- Plan and entitlement reconciliation.
- User deletion/export status.
- Security-event investigation.

Every privileged action is authorised and audited.

---

# 84. Production Maturity Model

| Level | Requirements | Mindtrace gate |
|---|---|---|
| 1 — MVP | Core learning loop, auth, database, deployment | Required before private beta |
| 2 — Production ready | Security, rate limits, backups, logs, analytics, CI/CD | Required before public paid launch |
| 3 — Scale ready | Queue isolation, caching, horizontal scaling, load tests, tracing | Triggered by measured traffic/queue load |
| 4 — Enterprise ready | Organisation tenancy, SSO, audit controls, retention policies | Not in initial roadmap |
| 5 — AI-native production | Prompt versioning, evaluation, tracing, cost controls, regression suite | Required for AI features at public launch; expanded continuously |

---

# 85. Launch Readiness Checklist

## Product
- [ ] First skill path and competency definitions reviewed by domain experts.
- [ ] Baseline assessment validated.
- [ ] Source ingestion handles supported formats and failures.
- [ ] User approves extracted concepts.
- [ ] Recall and applied-practice workflows complete.
- [ ] Error memory is inspectable and correctable.
- [ ] Progress claims are evidence-linked.
- [ ] Export and deletion work end to end.

## Frontend
- [ ] Responsive dashboard and practice.
- [ ] Accessible keyboard and screen-reader flows.
- [ ] Loading, empty, error and retry states.
- [ ] Cross-browser smoke tests.
- [ ] Performance budgets measured.

## Backend
- [ ] Authentication and ownership checks.
- [ ] Rate limits and quotas.
- [ ] Idempotent jobs and webhook handling.
- [ ] Structured errors and request IDs.
- [ ] Queue retry/dead-letter behaviour.

## Database and storage
- [ ] Schema and indexes reviewed.
- [ ] Migrations tested.
- [ ] Backups and restore tested.
- [ ] Private object storage.
- [ ] Deletion propagation verified.

## AI
- [ ] Prompt versions tracked.
- [ ] Golden datasets in CI or release process.
- [ ] Rubrics reviewed by experts.
- [ ] Citation/provenance validation.
- [ ] Prompt injection tests.
- [ ] Fallbacks and cost controls.
- [ ] Model regression tests.

## Security and privacy
- [ ] Secrets scan clean.
- [ ] SSRF and upload tests pass.
- [ ] Cross-user access tests pass.
- [ ] Privacy policy and AI data disclosure published.
- [ ] Admin access audited.
- [ ] Incident response contacts documented.

## Business and launch
- [ ] Pricing and entitlements verified.
- [ ] Payment webhooks tested.
- [ ] Terms, privacy and refund policy reviewed.
- [ ] Support process ready.
- [ ] Beta feedback mechanism ready.
- [ ] Rollback and incident runbooks ready.

---

# 86. Post-Launch Operations

Weekly:
- Review activation and retention cohorts.
- Review source ingestion and practice completion.
- Sample AI evaluations and user disputes.
- Inspect cost per active and paid user.
- Review support tickets and failed jobs.

Monthly:
- Revisit skill-path quality.
- Analyse repeated error patterns.
- Review churn and cancellation reasons.
- Run AI regression suite against current production model.
- Review security events and dependency updates.
- Prioritise product changes based on observed behaviour.

Quarterly:
- Conduct restore test.
- Review access controls and data retention.
- Revalidate rubrics with subject-matter experts.
- Review provider pricing and unit economics.

---

# 87. Roadmap

## Phase 0 — Foundation (2–3 weeks; planning estimate)
**Product:** user interviews, choose first skill track, define competency map and rubrics.  
**Design:** onboarding, dashboard, source and practice prototypes.  
**Engineering:** auth, schema, CI/CD, environments, telemetry.  
**AI:** golden dataset and baseline extraction/evaluation experiments.  
**Exit:** 15+ interviews completed; prototype usability tested; one track and core rubric approved.

## Phase 1 — Production MVP (6–10 weeks; planning estimate)
**Product:** goal setup, baseline, source import, concept approval, recall, practical text assessment, error memory and progress.  
**Engineering:** modular API, Postgres, object storage, queue, auth, quotas, billing foundation, export/deletion.  
**AI:** extraction, tutor, question generation and rubric evaluation with fallback.  
**Exit:** end-to-end core loop works; security and AI evaluations pass; 30–50 invited beta users complete at least two cycles.

## Phase 2 — V1 (following 6–8 weeks)
- Improve adaptive scheduling.
- Add additional skill path only after quality validation.
- Voice practice.
- Better source capture.
- Paid plan and usage dashboard.
- Skill Passport beta.
- Exit: retention and paid conversion show evidence of repeat value.

## Phase 3 — Growth
- More technical competency paths.
- Browser extension.
- GitHub/project evidence.
- Referral and content distribution.
- Improved personalised recommendations.
- Exit: repeatable acquisition channel and healthy unit economics.

## Phase 4 — Scale
- Worker pools by job type.
- Search/retrieval optimisation.
- Regional and capacity strategy.
- Optional team/education experiments only if demand is proven.
- Exit: system changes driven by measured bottlenecks and sustained retention.

Timelines are estimates for planning, not commitments. Scope should be reduced before quality gates are removed.

---

# 88. Risk Register

| Risk | Probability | Impact | Severity | Mitigation / contingency |
|---|---|---|---|---|
| Users see Mindtrace as another flashcard app | High | High | Critical | Lead with applied capability and longitudinal evidence |
| Users do not return after initial novelty | High | High | Critical | Validate recurring use with weekly practice loop before broad build |
| AI grading is unreliable | Medium-high | High | Critical | Expert rubrics, golden set, human review, confidence and appeals |
| Users do not want to import content | Medium | Medium | Medium | Start with curated paths and paste/upload as optional |
| Competitors add similar memory features | High | Medium | High | Build workflow quality, assessment data and trusted evidence |
| AI costs exceed subscription revenue | Medium | High | High | Quotas, model routing, async jobs, cost alerts |
| Copyright issues in source ingestion | Medium | High | High | User-provided content, metadata/provenance, terms review, takedown process |
| Privacy concern around learning history | Medium | High | High | Data minimisation, export/delete, transparent provider processing |
| Scope expands into LMS/course platform | High | Medium | High | Enforce out-of-scope list and narrow first track |
| Users game mastery scores | Medium | Medium | Medium | Varied tasks, delayed checks, evidence thresholds |
| Assessment rubrics become stale | Medium | Medium | Medium | Versioned rubrics and periodic expert review |
| Provider outage blocks learning | Medium | Medium | Medium | Keep review queue and existing content usable; provider fallback |

---

# 89. Definition of Done

A feature is done only when:
- Requirements and user story are implemented.
- Permission checks are enforced server-side.
- Input validation and edge cases are covered.
- Loading, empty, error, success and recovery states exist.
- Analytics events are instrumented without leaking content.
- Unit/integration/E2E tests cover critical behaviour.
- Accessibility and responsive behaviour are reviewed.
- Logs, metrics and alerts exist for operationally important paths.
- Security implications are reviewed.
- Documentation and runbooks are updated.
- Feature flag/rollback path exists where appropriate.

**AI feature DoD additionally requires:** prompt version, model version, schema validation, golden evaluation, cost attribution, timeout/fallback, injection testing and user-facing limitations.

---

# 90. Final Product Blueprint

1. **Vision:** turn learning into durable, demonstrable capability.
2. **Users:** independent software engineers, initially 3–10 years of experience.
3. **Problem:** fragmented learning and weak connection between content, recall and application.
4. **Solution:** integrated skill-development loop with source provenance, memory, practice and evidence.
5. **Advantage:** longitudinal, user-controlled learner model plus high-quality technical assessment.
6. **Moat hypothesis:** accumulated skill evidence and better personalised sequencing.
7. **Feature architecture:** goals, competency map, ingestion, concept graph, recall, practice, error memory, progress.
8. **Information architecture:** Today, My Skills, Learn, Practice, Memory, Progress, Settings.
9. **User journey:** goal → baseline → learn → recall → apply → feedback → review.
10. **Frontend:** Next.js + TypeScript.
11. **Backend:** FastAPI modular monolith plus workers.
12. **Database:** PostgreSQL; pgvector only if validated.
13. **API:** versioned REST, idempotency, cursor pagination.
14. **AI:** provider abstraction, source-grounded tutoring, structured evaluation.
15. **Security:** user-level isolation, secure auth, upload/SSRF protection, prompt-injection controls.
16. **Infrastructure:** managed hosting, Postgres, private object storage, queue, observability.
17. **Observability:** logs, metrics, traces, AI run and cost tracking.
18. **Analytics:** activation, retention, practice, demonstrated progress and paid conversion.
19. **Billing:** free + paid consumer subscription with server-side entitlements.
20. **Testing:** unit, integration, E2E, security, load, accessibility and AI regression.
21. **Scalability:** scale API and workers independently only as measured demand grows.
22. **Production maturity:** secure production MVP first; enterprise is not a launch gate.
23. **Launch readiness:** core loop, AI quality, security, privacy, billing and recovery verified.
24. **Roadmap:** foundation → production MVP → V1 → growth → scale.
25. **Risks:** retention, grading reliability, differentiation, cost and privacy.
26. **Technical decisions:** modular monolith, relational source of truth, asynchronous AI jobs, explicit rubrics.

---

# 91. Recommended High-Level Production Architecture

```text
Learner (Web / Mobile Web)
        │
        ▼
CDN + WAF + Bot Protection
        │
        ▼
Next.js Application
        │ HTTPS
        ▼
FastAPI Application API
  ├── Auth / Profile
  ├── Goals / Skill Paths
  ├── Sources / Concepts
  ├── Practice / Assessments
  ├── Memory / Recommendations
  ├── Billing / Entitlements
  └── Usage / Analytics
        │
        ├────────────── PostgreSQL
        ├────────────── Private Object Storage
        ├────────────── Queue / Redis
        │                    │
        │                    ▼
        │                Worker Pool
        │                ├── Extraction
        │                ├── OCR
        │                ├── Embeddings
        │                ├── AI Evaluation
        │                └── Export / Deletion
        │
        └────────────── AI Provider Adapter
                             │
                             ▼
                       LLM Provider(s)

Observability: Logs + Metrics + Traces + AI Cost + Alerts
Control Plane: Admin + Billing + Quotas + Feature Flags
```

Launch with one API deployment, one worker deployment and managed dependencies. Add more components only when a measurable bottleneck or isolation requirement appears.

---

# 92. AI Production Architecture

```text
User Action
    │
    ▼
Authenticated API
    ├── Ownership / Permission Check
    ├── Quota Check
    ├── Input Validation
    └── Usage Event
          │
          ▼
      AI Task Router
          ├── Prompt Version
          ├── Model Selection
          ├── Context Builder
          ├── Source Retrieval
          └── Cost / Token Budget
                 │
                 ▼
             LLM Provider
                 │
                 ▼
          Structured Output Validation
                 │
          ┌──────┴──────┐
          ▼             ▼
       Valid         Invalid
          │             │
          ▼             ▼
     Evaluation     Bounded Retry /
     + Provenance   Fallback / Failure
          │
          ▼
    Persist Result + Trace
          │
          ▼
    User-visible Feedback
```

AI does not directly change entitlements, delete data, or assign final mastery status without deterministic application rules.

---

# 93. Non-Negotiable Engineering Principles

1. Production over demo.
2. Product before AI.
3. Security by default.
4. Observable by default.
5. Assume dependencies fail.
6. Assume abuse will occur.
7. Scale deliberately.
8. Every interaction has complete states.
9. Every AI feature has safeguards and evaluation.
10. Every important architecture decision has a rationale.
11. Browser-accessible data is inspectable by the user.
12. Operational trust matters.
13. Progress claims require evidence.
14. User learning data remains user-controlled.

---

# 94. Final Review Questions

## Product
- Does the product help a user perform better, not just consume more?
- Is the first skill path narrow enough?
- Why will users return weekly?
- Why will users pay when free alternatives exist?
- Is the progress claim defensible?

## Security
- Can one user retrieve another user's sources, attempts or memory?
- Can a malicious PDF or URL reach internal infrastructure?
- Can a user bypass quotas?
- Are admin actions audited?
- Can data be exported and deleted?

## Performance and reliability
- What are p50/p95/p99 for core APIs?
- Can queue backlog be inspected?
- What happens when the LLM provider is unavailable?
- Can a failed evaluation be retried without losing the response?
- Are backups restorable?

## AI quality
- Are rubrics expert-reviewed?
- Can the system explain why a score was assigned?
- Are citations source-grounded?
- Can prompt/model regressions be detected?
- Is uncertainty visible?
- Can users challenge incorrect feedback?

## Business
- Is weekly demonstrated progress correlated with retention?
- Is paid conversion driven by real value?
- Is gross margin healthy at typical usage?
- Are cancellation reasons understood?

---

# 95. Output Format and Implementation Handoff

The PRD is the product source of truth. Implementation should be broken into small vertical slices.

Each engineering ticket must contain:
- User outcome.
- Scope and non-scope.
- API and data changes.
- UX states.
- Permission/security requirements.
- Analytics.
- Tests.
- Acceptance criteria.
- Rollback or feature-flag plan.

Do not ask an AI coding agent to implement the entire PRD in one pass. First generate architecture and repository plans, then implement a vertical slice, test it, review it and proceed.

---

# 96. Source Discipline

This PRD distinguishes:
- **Research-backed observations:** capabilities/prices published on competitor pages linked in Section 1.
- **Product decisions:** proposed Mindtrace behaviour and scope.
- **Technical recommendations:** proposed architecture and controls.
- **Assumptions:** target users, pricing, conversion and retention thresholds.
- **Open questions:** first track, willingness to pay, retention and assessment validity.

No primary research was conducted. Market size and demand are not established. Revalidate competitor pricing and capabilities before external publication.

---

# 97. Anti-Shortcut Rules

Do not:
- Compete as a generic AI tutor.
- Build a full note-taking workspace.
- Treat summaries as learning outcomes.
- Generate flashcards without review and user control.
- Claim mastery from a single AI score.
- Add agents, microservices, Kubernetes or a separate vector database without a concrete need.
- Ingest content by bypassing access controls.
- Log private learner responses indiscriminately.
- Add social features before core retention is proven.
- Expand to every profession before the first technical path works.
- Use AI output as the sole authority for high-stakes assessment.

---

# 98. Final Instruction and Open Decisions

## Completed in this PRD
- Product definition and initial positioning.
- Problem hypothesis and competitor landscape.
- MVP feature map and lifecycle.
- UX and information architecture.
- Frontend/backend/database/API recommendations.
- AI, memory, RAG, evaluation and cost controls.
- Security, privacy, reliability, observability and operations.
- Roadmap, launch checklist, risk register and Definition of Done.

## Assumptions to validate
1. Software engineers experience this problem frequently enough to adopt a separate product.
2. A narrow technical skill path is more compelling than a general learning assistant.
3. Users value longitudinal evidence and targeted practice enough to pay.
4. Users will import sources or use curated content as part of a recurring workflow.
5. Rubric-based practical assessment can be made reliable enough for coaching.

## Open decisions before implementation
1. Which launch track is first: System Design or Applied AI Engineering?
2. Which one concrete learner outcome should the first path promise?
3. Will the first release use curated content, user-imported sources, or both?
4. Which assessment types are reliable enough for launch?
5. Which launch geography and payment provider will be supported?
6. What is the first price test?
7. What data may be retained and sent to model providers under the chosen privacy policy?

## Final product principle

**Core feature = Skill development**  
**Memory + Retrieval + Practice + Evidence = The Product**  
**Security + Reliability + Observability + Scalability + Operations = The Engineering**  
**AI = The Advancement / Multiplier**

Mindtrace succeeds only if users become better at explaining, remembering and applying skills—not merely better at using Mindtrace.
