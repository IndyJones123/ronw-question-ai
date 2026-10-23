"""Koneksi + migrasi database PostgreSQL (psycopg 3 sync)."""
from __future__ import annotations

import re
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from . import config

MIGRATIONS_DIR = config.BACKEND_DIR / "migrations"


@contextmanager
def get_conn():
    """Koneksi psycopg dengan row_factory dict_row; commit/rollback otomatis."""
    with psycopg.connect(**config.db_kwargs(), row_factory=dict_row) as conn:
        yield conn


def db_ok() -> bool:
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False


def _split_statements(sql: str) -> list[str]:
    """Pecah file .sql jadi statement (aman untuk file tanpa blok $$...$$)."""
    parts = [p.strip() for p in re.split(r";\s*(?:\r?\n|$)", sql)]
    return [p for p in parts if p and not p.startswith("--")]


def run_migrations() -> list[str]:
    """Jalankan backend/migrations/*.sql yang belum diterapkan.

    Terapkan lewat satu transaksi, catat di tabel schema_migrations.
    Return daftar migrasi yang baru dieksekusi.
    """
    applied_now: list[str] = []
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                name       text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        done = {
            r["name"]
            for r in conn.execute("SELECT name FROM schema_migrations").fetchall()
        }
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in done:
                continue
            sql = path.read_text(encoding="utf-8")
            try:
                conn.execute(sql)
            except psycopg.errors.SyntaxError:
                # multi-statement (psycopg pakai protocol terparameter) -> pecah
                for stmt in _split_statements(sql):
                    conn.execute(stmt)
            conn.execute(
                "INSERT INTO schema_migrations (name) VALUES (%s) "
                "ON CONFLICT (name) DO NOTHING",
                (path.name,),
            )
            applied_now.append(path.name)
        conn.commit()
    return applied_now
