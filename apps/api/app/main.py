import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import AppError, RequestIdMiddleware, app_error_handler, unhandled_error_handler
from app.core.logging_middleware import RequestLogMiddleware
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import me_router, router as auth_router
from app.modules.baseline.router import router as baseline_router
from app.modules.billing.router import router as billing_router
from app.modules.concepts.router import router as concepts_router
from app.modules.feedback.router import router as feedback_router
from app.modules.memory.router import router as memory_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.practice.router import router as practice_router
from app.modules.progress.router import router as progress_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.skills.router import router as skills_router
from app.modules.sources.router import router as sources_router
from app.modules.tutor.router import router as tutor_router
from app.modules.usage.router import router as usage_router

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="Mindtrace API — skill development through recall, practice, and evidence.",
)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

prefix = settings.api_prefix
app.include_router(auth_router, prefix=prefix)
app.include_router(me_router, prefix=prefix)
app.include_router(onboarding_router, prefix=prefix)
app.include_router(skills_router, prefix=prefix)
app.include_router(recommendations_router, prefix=prefix)
app.include_router(sources_router, prefix=prefix)
app.include_router(concepts_router, prefix=prefix)
app.include_router(practice_router, prefix=prefix)
app.include_router(baseline_router, prefix=prefix)
app.include_router(memory_router, prefix=prefix)
app.include_router(progress_router, prefix=prefix)
app.include_router(tutor_router, prefix=prefix)
app.include_router(usage_router, prefix=prefix)
app.include_router(billing_router, prefix=prefix)
app.include_router(feedback_router, prefix=prefix)
app.include_router(admin_router, prefix=prefix)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": "0.3.0"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    return {"status": "ready"}
