"""SSRF-safe public URL fetching for learning source ingestion."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from app.core.errors import AppError

BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

MAX_REDIRECTS = 3
MAX_BYTES = 2_000_000
TIMEOUT = 8.0


def _is_blocked_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return any(addr in net for net in BLOCKED_NETWORKS)


def validate_public_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise AppError("invalid_url", "Only http/https URLs are supported", 400)
    if not parsed.hostname:
        raise AppError("invalid_url", "URL host is required", 400)
    host = parsed.hostname.lower()
    if host in {"localhost", "metadata.google.internal"}:
        raise AppError("ssrf_blocked", "Private or local hosts are not allowed", 400)

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise AppError("invalid_url", "Could not resolve host", 400) from exc

    for info in infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            raise AppError("ssrf_blocked", "URL resolves to a private network address", 400)

    return url.strip()


def fetch_public_text(url: str) -> str:
    current = validate_public_url(url)
    redirects = 0

    with httpx.Client(follow_redirects=False, timeout=TIMEOUT, headers={"User-Agent": "MindtraceBot/0.1"}) as client:
        while True:
            validate_public_url(current)
            response = client.get(current)
            if response.is_redirect:
                redirects += 1
                if redirects > MAX_REDIRECTS:
                    raise AppError("redirect_limit", "Too many redirects while fetching URL", 400)
                location = response.headers.get("location")
                if not location:
                    raise AppError("invalid_url", "Redirect without Location header", 400)
                current = str(httpx.URL(current).join(location))
                continue

            if response.status_code >= 400:
                raise AppError("fetch_failed", f"URL fetch failed with status {response.status_code}", 400)

            content_type = (response.headers.get("content-type") or "").lower()
            if "html" not in content_type and "text" not in content_type and "json" not in content_type:
                raise AppError("unsupported_content", "URL did not return readable text content", 400)

            raw = response.content[: MAX_BYTES + 1]
            if len(raw) > MAX_BYTES:
                raise AppError("content_too_large", "Fetched content exceeds size limit", 400)

            text = raw.decode(response.encoding or "utf-8", errors="replace")
            # Strip crude HTML tags for concept extraction; keep readable text.
            if "html" in content_type:
                import re

                text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
                text = re.sub(r"(?s)<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
            return text
