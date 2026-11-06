from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "local"
    app_name: str = "Mindtrace API"
    api_prefix: str = "/api/v1"
    app_origin: str = "http://localhost:3000"
    api_origin: str = "http://localhost:8000"

    # Local default is SQLite so the MVP runs without Docker. Use Postgres in staging/prod.
    database_url: str = "sqlite:///./mindtrace.db"
    redis_url: str = "redis://localhost:6379/0"

    session_secret: str = "dev-only-change-me-to-a-long-random-string"
    access_token_expire_minutes: int = 60 * 24 * 7
    cookie_name: str = "mindtrace_session"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "mindtrace"
    s3_secret_key: str = "mindtrace_secret"
    s3_bucket: str = "mindtrace-sources"
    s3_region: str = "us-east-1"
    storage_backend: str = "local"  # local | s3
    local_storage_dir: str = "./data/object_storage"
    sync_ingest: bool = True  # process extract inline when True; else rely on worker

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_enabled: bool = False

    # Quotas (free tier defaults)
    free_source_imports_per_hour: int = 10
    free_ai_evaluations_per_day: int = 20
    free_active_skill_paths: int = 1

    max_pdf_bytes: int = 25 * 1024 * 1024
    max_text_chars: int = 200_000

    # Email (ESP) — when empty, links are logged
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "Mindtrace <noreply@mindtrace.local>"

    # Razorpay (India payments) — optional
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # Admin
    admin_api_key: str = "dev-admin-key-change-me"

    # OAuth (optional — disabled when empty)
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    oauth_redirect_base: str = ""  # defaults to api_origin

    # MFA
    mfa_issuer: str = "Mindtrace"

    # Sandbox (implement tasks)
    sandbox_enabled: bool = True
    sandbox_timeout_seconds: int = 3
    sandbox_max_output_chars: int = 20_000

    # Account purge
    account_purge_grace_hours: int = 0  # 0 = purge ASAP via worker

    # Whisper / STT
    whisper_model: str = "whisper-1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
