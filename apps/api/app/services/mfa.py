"""TOTP MFA helpers (RFC 6238) using pyotp when available, else stdlib HMAC."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

from app.core.config import get_settings


def _b32_secret(nbytes: int = 20) -> str:
    return base64.b32encode(secrets.token_bytes(nbytes)).decode("ascii").rstrip("=")


def generate_totp_secret() -> str:
    try:
        import pyotp

        return pyotp.random_base32()
    except ImportError:
        return _b32_secret()


def provisioning_uri(*, secret: str, email: str) -> str:
    settings = get_settings()
    try:
        import pyotp

        return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=settings.mfa_issuer)
    except ImportError:
        label = quote(f"{settings.mfa_issuer}:{email}")
        return f"otpauth://totp/{label}?secret={secret}&issuer={quote(settings.mfa_issuer)}&algorithm=SHA1&digits=6&period=30"


def _hotp(secret_b32: str, counter: int, digits: int = 6) -> str:
    pad = "=" * ((8 - len(secret_b32) % 8) % 8)
    key = base64.b32decode(secret_b32.upper() + pad, casefold=True)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)


def verify_totp(secret: str, code: str, *, window: int = 1) -> bool:
    code = (code or "").strip().replace(" ", "")
    if not code.isdigit():
        return False
    try:
        import pyotp

        return bool(pyotp.TOTP(secret).verify(code, valid_window=window))
    except ImportError:
        timestep = int(time.time() // 30)
        for drift in range(-window, window + 1):
            if hmac.compare_digest(_hotp(secret, timestep + drift), code):
                return True
        return False


def generate_recovery_codes(n: int = 8) -> list[str]:
    return [secrets.token_hex(4) for _ in range(n)]


def hash_recovery_code(code: str) -> str:
    return hashlib.sha256(code.strip().lower().encode()).hexdigest()
