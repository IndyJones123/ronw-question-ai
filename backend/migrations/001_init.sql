-- Skema auth: users + riwayat login (disimpan device apa saja)
-- Dijalankan otomatis saat backend start, dicatat di tabel schema_migrations.

CREATE TABLE IF NOT EXISTS users (
    id            bigserial PRIMARY KEY,
    username      text        NOT NULL UNIQUE,
    password_hash text        NOT NULL,
    full_name     text        NOT NULL DEFAULT '',
    is_active     boolean     NOT NULL DEFAULT true,
    created_at    timestamptz NOT NULL DEFAULT now(),
    last_login_at timestamptz
);

CREATE TABLE IF NOT EXISTS login_logs (
    id         bigserial PRIMARY KEY,
    user_id    bigint REFERENCES users (id) ON DELETE SET NULL,
    username   text        NOT NULL,
    success    boolean     NOT NULL,
    reason     text        NOT NULL DEFAULT '',
    -- info device dari client: hostname, os, user, python, layar, dll
    device     jsonb       NOT NULL DEFAULT '{}'::jsonb,
    ip         text        NOT NULL DEFAULT '',
    user_agent text        NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS login_logs_created_at_idx ON login_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS login_logs_username_idx ON login_logs (username);
