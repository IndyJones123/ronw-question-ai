"""Backend login FastAPI - tanpa register, user dikelola via CLI seed_user.

Endpoint:
  GET  /api/health      -> cek koneksi DB
  POST /api/login       -> {username, password, device} -> token + info user
  GET  /api/me          -> profil user dari token (Bearer)
  GET  /api/login-logs  -> riwayat login + device (admin audit, butuh Bearer)
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, Request

from . import config, db, security
from .schemas import HealthOut, LoginLogOut, LoginRequest, LoginResponse, UserOut

config.check_secret()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # migrasi jalan sekali saat startup (idempotent)
    applied = db.run_migrations()
    if applied:
        print(f"[backend] migrasi diterapkan: {', '.join(applied)}")
    yield


app = FastAPI(title="Quiz Live OCR Auth", version="1.0.0", lifespan=lifespan)


# ---------------------------------------------------------------- helpers


def _client_ip(request: Request) -> str:
    if request.client:
        return request.client.host or ""
    return ""


def _clean_device(device: dict) -> dict:
    """Batas ukuran + buang nilai non-primitif biar jsonb aman."""
    clean: dict = {}
    for key, value in list(device.items())[:30]:
        k = str(key)[:64]
        if value is None or isinstance(value, (bool, int, float)):
            clean[k] = value
        elif isinstance(value, str):
            clean[k] = value[:300]
    return clean


def _user_out(row: dict) -> UserOut:
    return UserOut(id=row["id"], username=row["username"],
                   full_name=row["full_name"], is_active=row["is_active"])


def current_user(authorization: str = Header(default="")) -> dict:
    """Dependency: token Bearer -> baris user terbaru dari DB."""
    token = ""
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    payload = security.read_token(token) if token else None
    if payload is None:
        raise HTTPException(status_code=401, detail="Token tidak valid atau kedaluwarsa")
    try:
        with db.get_conn() as conn:
            row = conn.execute(
                "SELECT id, username, full_name, is_active FROM users WHERE id = %s",
                (payload.get("uid"),),
            ).fetchone()
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database tidak tersedia")
    if row is None or not row["is_active"]:
        raise HTTPException(status_code=401, detail="Akun tidak ditemukan/nonaktif")
    return dict(row)


# ---------------------------------------------------------------- endpoints


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    ok = db.db_ok()
    return HealthOut(status="ok" if ok else "error", db=ok)


@app.post("/api/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request) -> LoginResponse:
    device = _clean_device(body.device)
    ip = _client_ip(request)
    ua = (request.headers.get("user-agent") or "")[:300]
    username = body.username.strip()

    try:
        with db.get_conn() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash, full_name, is_active "
                "FROM users WHERE username = %s",
                (username,),
            ).fetchone()

            if row is None:
                # hash palsu -> waktu respons sama dengan user yang ada
                security.verify_password_dummy(body.password)
                success, reason = False, "unknown_user"
            elif not row["is_active"]:
                security.verify_password_dummy(body.password)
                success, reason = False, "inactive"
            elif not security.verify_password(body.password, row["password_hash"]):
                success, reason = False, "bad_password"
            else:
                success, reason = True, ""

            # --- audit log: siapa, kapan, device apa, berhasil/gagal
            conn.execute(
                "INSERT INTO login_logs "
                "(user_id, username, success, reason, device, ip, user_agent) "
                "VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)",
                (
                    row["id"] if row else None,
                    username,
                    success,
                    reason,
                    json.dumps(device, ensure_ascii=False),
                    ip,
                    ua,
                ),
            )
            if success:
                conn.execute(
                    "UPDATE users SET last_login_at = now() WHERE id = %s",
                    (row["id"],),
                )
            conn.commit()
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database tidak tersedia")

    if not success:
        raise HTTPException(
            status_code=401,
            detail="Username atau password salah"
            if reason != "inactive"
            else "Akun nonaktif, hubungi admin",
        )

    token = security.make_token({"uid": row["id"], "uname": row["username"]})
    return LoginResponse(
        access_token=token,
        expires_in=config.AUTH_TOKEN_TTL_HOURS * 3600,
        user=_user_out(dict(row)),
    )


@app.get("/api/me", response_model=UserOut)
def me(user: dict = Depends(current_user)) -> UserOut:
    return _user_out(user)


@app.get("/api/login-logs", response_model=list[LoginLogOut])
def login_logs(
    limit: int = 50,
    username: str | None = None,
    user: dict = Depends(current_user),
) -> list[LoginLogOut]:
    limit = max(1, min(limit, 200))
    sql = (
        "SELECT id, username, success, reason, device, ip, user_agent, "
        "to_char(created_at AT TIME ZONE 'Asia/Jakarta', "
        "'YYYY-MM-DD HH24:MI:SS') AS created_at "
        "FROM login_logs"
    )
    params: list = []
    if username:
        sql += " WHERE username = %s"
        params.append(username)
    sql += " ORDER BY id DESC LIMIT %s"
    params.append(limit)
    try:
        with db.get_conn() as conn:
            rows = conn.execute(sql, params).fetchall()
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database tidak tersedia")
    out = []
    for r in rows:
        item = dict(r)
        device = item["device"]
        if isinstance(device, str):  # psycopg kadang balikin jsonb sebagai str
            try:
                device = json.loads(device)
            except ValueError:
                device = {}
        out.append(LoginLogOut(device=device or {}, **{k: v for k, v in item.items()
                                                       if k != "device"}))
    return out
