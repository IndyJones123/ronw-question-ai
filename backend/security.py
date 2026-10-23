"""Hash password (PBKDF2, stdlib) + token tanda tangan HMAC.

Tidak ada dependency tambahan: hashlib/hmac/secrets dari Python stdlib.
Format hash: pbkdf2_sha256$<iter>$<salt_b64>$<hash_b64>
Format token: <payload_b64url>.<sig_b64url>  (signed, exp-based)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from . import config

PBKDF2_ITERATIONS = 600_000  # rekomendasi OWASP untuk PBKDF2-HMAC-SHA256
_ALGO = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return (
        f"{_ALGO}${PBKDF2_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt_b64, hash_b64 = stored.split("$")
        if algo != _ALGO:
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except (ValueError, TypeError, AttributeError):
        return False


_DUMMY_HASH: str | None = None


def verify_password_dummy(password: str) -> bool:
    """Verifikasi terhadap hash palsu: samakan waktu respons saat user tak dikenal."""
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = hash_password(secrets.token_urlsafe(24))
    return verify_password(password, _DUMMY_HASH)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64url(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def make_token(payload: dict, ttl_hours: int | None = None) -> str:
    ttl = config.AUTH_TOKEN_TTL_HOURS if ttl_hours is None else ttl_hours
    body = dict(payload)
    body["exp"] = int(time.time()) + ttl * 3600
    raw = _b64url(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(config.AUTH_SECRET_KEY.encode("utf-8"), raw.encode("ascii"),
                   hashlib.sha256).digest()
    return f"{raw}.{_b64url(sig)}"


def read_token(token: str) -> dict | None:
    """Validasi token -> payload, atau None kalau rusak/kedaluwarsa/tanda tangan salah."""
    try:
        raw, sig = token.split(".", 1)
        expected = hmac.new(config.AUTH_SECRET_KEY.encode("utf-8"), raw.encode("ascii"),
                            hashlib.sha256).digest()
        if not hmac.compare_digest(_unb64url(sig), expected):
            return None
        payload = json.loads(_unb64url(raw))
        if not isinstance(payload, dict):
            return None
        if int(payload.get("exp", 0)) < time.time():
            return None
        return payload
    except (ValueError, TypeError, KeyError):
        return None
