"""Safe-ish PDF text extraction with size and page limits."""

from __future__ import annotations

import io

from pypdf import PdfReader

from app.core.errors import AppError


def extract_pdf_text(data: bytes, *, max_bytes: int, max_pages: int = 200) -> tuple[str, dict]:
    if len(data) > max_bytes:
        raise AppError("pdf_too_large", f"PDF exceeds {max_bytes} byte limit", 400)
    if not data.startswith(b"%PDF"):
        raise AppError("invalid_pdf", "File does not look like a PDF", 400)

    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
    except Exception as exc:  # noqa: BLE001
        raise AppError("pdf_parse_failed", "Could not parse PDF", 400) from exc

    if getattr(reader, "is_encrypted", False):
        raise AppError("pdf_encrypted", "Encrypted PDFs are not supported", 400)

    page_count = len(reader.pages)
    if page_count > max_pages:
        raise AppError("pdf_too_many_pages", f"PDF exceeds {max_pages} page limit", 400)

    chunks: list[str] = []
    for idx, page in enumerate(reader.pages):
        try:
            chunks.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            chunks.append("")
        if idx >= max_pages - 1:
            break

    text = "\n\n".join(c.strip() for c in chunks if c and c.strip())
    if not text:
        raise AppError("pdf_empty", "No extractable text found in PDF", 400)

    return text, {"page_count": page_count, "bytes": len(data)}
