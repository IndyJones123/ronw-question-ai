"""Konfigurasi backend login.

Baca file backend/.env (kredensial DB + rahasia token). Env dari sistem
tidak di-override oleh .env (kalau sudah ada di environment, menang).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env", override=False)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "quiz_auth")
DB_USER = os.getenv("DB_USER", "quiz_auth")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "")
AUTH_TOKEN_TTL_HOURS = int(os.getenv("AUTH_TOKEN_TTL_HOURS", "12"))

# Host/port yang di-bind uvicorn (hanya lokal: login jangan terekspos ke LAN)
BIND_HOST = os.getenv("AUTH_BIND_HOST", "127.0.0.1")
BIND_PORT = int(os.getenv("AUTH_BIND_PORT", "8000"))


def db_kwargs() -> dict:
    """Parameter koneksi psycopg (dict - aman dari escaping URL)."""
    if not DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD kosong - isi backend/.env (lihat backend/.env.example)"
        )
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "connect_timeout": 5,
    }


def check_secret() -> None:
    if not AUTH_SECRET_KEY or len(AUTH_SECRET_KEY) < 16:
        raise RuntimeError(
            "AUTH_SECRET_KEY kosong/terlalu pendek - isi backend/.env "
            "(jalankan: python -m backend.seed_user --gen-secret)"
        )
