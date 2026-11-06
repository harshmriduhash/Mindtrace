# P1 Plan — Skill Passport · Browser Extension · Voice Practice

| # | Workstream | Deliverable | Exit criteria |
|---|---|---|---|
| 1 | Skill Passport | Evidence summary of competencies (API + UI + JSON export) | User can view/print/export a non-mastery, evidence-linked passport |
| 2 | Browser extension | MV3 “Save to Mindtrace” capture | Selected text/URL imports as a source into Learn |
| 3 | Voice practice | Record → transcript → evaluate | User can complete a spoken explain task; audio optional |
| 4 | Vercel prep | Frontend deploy config + docs | `apps/web` deploys to Vercel; API URL via env |

**Deployment note:** Vercel hosts the Next.js web app. FastAPI stays on a container host (Railway/Render/Fly). Browser extension talks to the public API origin.
