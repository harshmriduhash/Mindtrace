# Deployment guide

## Architecture for production

| Surface | Host | Notes |
|---|---|---|
| Web (`apps/web`) | **Vercel** | Next.js App Router |
| API (`apps/api`) | Railway / Render / Fly.io | FastAPI + worker process |
| Database | Managed Postgres | Set `DATABASE_URL` |
| Objects | S3 / R2 / MinIO | Set `STORAGE_BACKEND=s3` |

The browser extension talks to the **public API origin** with a Bearer token (not Vercel rewrites).

---

## 1) Deploy API first

```bash
cd apps/api
# provision Postgres, then:
export DATABASE_URL=postgresql+psycopg://...
alembic upgrade head
python scripts/seed_system_design.py
python scripts/seed_applied_ai.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
# optional worker:
PYTHONPATH=. python -m app.workers.process_jobs
```

Required env (API):

- `DATABASE_URL`
- `SESSION_SECRET` (long random)
- `APP_ORIGIN` = `https://your-app.vercel.app`
- `API_ORIGIN` = `https://api.your-domain.com`
- `COOKIE_SECURE=true`
- `ENVIRONMENT=production`
- Optional: `OPENAI_API_KEY`, `RAZORPAY_*`, `SMTP_*`, `S3_*`, `GOOGLE_OAUTH_*`, `GITHUB_OAUTH_*`

CORS already allows `APP_ORIGIN` and `chrome-extension://*`.

---

## 2) Deploy web on Vercel

### Option A — Vercel CLI

```bash
cd apps/web
npm i -g vercel
vercel link
vercel env add API_ORIGIN production   # https://api.your-domain.com
vercel env add NEXT_PUBLIC_API_URL production   # https://api.your-domain.com/api/v1
# For cookie sessions via same-site proxy, prefer:
# NEXT_PUBLIC_API_URL=/api/v1
# API_ORIGIN=https://api.your-domain.com
vercel --prod
```

### Option B — GitHub integration

1. Import `harshmriduhash/Mindtrace` in Vercel  
2. **Root Directory:** `apps/web`  
3. Framework: Next.js  
4. Environment variables:

| Name | Value |
|---|---|
| `API_ORIGIN` | `https://<your-api-host>` |
| `NEXT_PUBLIC_API_URL` | `/api/v1` (recommended) **or** full `https://<api>/api/v1` |

With `NEXT_PUBLIC_API_URL=/api/v1`, Next.js rewrites proxy to `API_ORIGIN`, so HttpOnly cookies work on the Vercel domain.

### Cookie note

If the browser calls the API on a **different** domain without the rewrite proxy, set:

- `COOKIE_SAMESITE=none`
- `COOKIE_SECURE=true`

Prefer the rewrite proxy instead.

---

## 3) Load the browser extension

1. Open Chrome → Extensions → Developer mode  
2. Load unpacked → `extensions/mindtrace-capture`  
3. In Mindtrace Settings, generate an extension token  
4. Paste token + API base (`https://api.../api/v1`) into extension options  

---

## 4) Smoke checklist

- [ ] `https://your-app.vercel.app` loads  
- [ ] Signup / login works (cookie set)  
- [ ] `/app/passport` renders  
- [ ] Voice practice requests mic (HTTPS required)  
- [ ] Extension capture creates a source  
- [ ] `/healthz` on API returns `0.4.0`  
