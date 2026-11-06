#!/usr/bin/env python3
"""Process queued jobs (source extraction). Run: python -m app.workers.process_jobs"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Job, Source
from app.modules.sources.service import extract_and_attach_concepts
from app.services.pdf_extract import extract_pdf_text
from app.services.storage import object_storage
from app.core.config import get_settings


def process_one(db) -> bool:
    job = db.scalar(select(Job).where(Job.status == "queued").order_by(Job.created_at).limit(1))
    if not job:
        return False
    job.status = "running"
    job.attempts += 1
    db.commit()

    try:
        if job.type == "source_extract":
            source_id = job.payload_json.get("source_id")
            source = db.get(Source, source_id)
            if not source:
                raise RuntimeError("source_missing")
            text = source.raw_text or ""
            if source.object_key and not text:
                data = object_storage.get_bytes(source.object_key)
                settings = get_settings()
                text, meta = extract_pdf_text(data, max_bytes=settings.max_pdf_bytes)
                source.metadata_json = {**(source.metadata_json or {}), **meta}
            extract_and_attach_concepts(db, source=source, text=text, user_id=source.user_id, create_job=False)
            job.status = "completed"
            job.result_json = {"ok": True}
        else:
            job.status = "failed"
            job.error_code = "unknown_job_type"
        db.commit()
    except Exception as exc:  # noqa: BLE001
        job.status = "failed"
        job.error_code = type(exc).__name__[:64]
        job.result_json = {"error": str(exc)[:500]}
        if job.payload_json.get("source_id"):
            source = db.get(Source, job.payload_json["source_id"])
            if source:
                source.status = "failed"
                source.error_code = job.error_code
        db.commit()
    return True


def main() -> None:
    print("Mindtrace worker started")
    while True:
        db = SessionLocal()
        try:
            worked = process_one(db)
        finally:
            db.close()
        if not worked:
            time.sleep(2)


if __name__ == "__main__":
    main()
