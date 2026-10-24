"""CLI manajemen user (user juga bisa daftar lewat POST /api/register).

Pakai:
    python -m backend.seed_user add <username> <password> [--full-name "Nama"]
    python -m backend.seed_user list
    python -m backend.seed_user activate <username>
    python -m backend.seed_user deactivate <username>
    python -m backend.seed_user reset-password <username> <password_baru>
    python -m backend.seed_user --gen-secret            # generate AUTH_SECRET_KEY
    python -m backend.seed_user logs [username] [--limit 50]

Semua operasi langsung ke DB (tanpa melalui API).
"""
from __future__ import annotations

import argparse
import sys

from . import config, db, security


def cmd_add(args):
    pw = args.password
    if len(pw) < 6:
        print("ERROR: password minimal 6 karakter", file=sys.stderr)
        return 1
    h = security.hash_password(pw)
    try:
        with db.get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, full_name) "
                "VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING",
                (args.username, h, args.full_name or ""),
            )
            row = conn.execute(
                "SELECT id, username, full_name, is_active FROM users WHERE username = %s",
                (args.username,),
            ).fetchone()
            conn.commit()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"User '{row['username']}' (id={row['id']}) "
          f"active={row['is_active']} name='{row['full_name']}'")
    return 0


def cmd_list(args):
    try:
        with db.get_conn() as conn:
            rows = conn.execute(
                "SELECT id, username, full_name, is_active, "
                "to_char(created_at, 'YYYY-MM-DD HH24:MI') AS created, "
                "to_char(last_login_at, 'YYYY-MM-DD HH24:MI:SS') AS last_login "
                "FROM users ORDER BY id"
            ).fetchall()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if not rows:
        print("(tidak ada user)")
        return 0
    print(f"{'id':>4} {'username':<20} {'active':<7} {'full_name':<20} "
          f"{'created':<20} {'last_login':<20}")
    print("-" * 95)
    for r in rows:
        print(f"{r['id']:>4} {r['username']:<20} "
              f"{'ya' if r['is_active'] else 'tidak':<7} "
              f"{r['full_name'] or '':<20} {r['created']:<20} "
              f"{r['last_login'] or '-':<20}")
    return 0


def cmd_activate(args, active: bool):
    try:
        with db.get_conn() as conn:
            row = conn.execute(
                "UPDATE users SET is_active = %s WHERE username = %s "
                "RETURNING id, username",
                (active, args.username),
            ).fetchone()
            conn.commit()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if row is None:
        print(f"User '{args.username}' tidak ditemukan", file=sys.stderr)
        return 1
    print(f"User '{row['username']}' {'aktif' if active else 'nonaktif'}")
    return 0


def cmd_reset_password(args):
    if len(args.password) < 6:
        print("ERROR: password minimal 6 karakter", file=sys.stderr)
        return 1
    h = security.hash_password(args.password)
    try:
        with db.get_conn() as conn:
            row = conn.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s "
                "RETURNING id, username",
                (h, args.username),
            ).fetchone()
            conn.commit()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if row is None:
        print(f"User '{args.username}' tidak ditemukan", file=sys.stderr)
        return 1
    print(f"Password '{row['username']}' direset")
    return 0


def cmd_logs(args):
    import json
    limit = args.limit
    sql = (
        "SELECT id, username, success, reason, device, ip, user_agent, "
        "to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at "
        "FROM login_logs"
    )
    params: list = []
    if args.username:
        sql += " WHERE username = %s"
        params.append(args.username)
    sql += " ORDER BY id DESC LIMIT %s"
    params.append(limit)
    try:
        with db.get_conn() as conn:
            rows = conn.execute(sql, params).fetchall()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if not rows:
        print("(tidak ada log login)")
        return 0
    for r in rows:
        dev = r["device"]
        if isinstance(dev, str):
            try:
                dev = json.loads(dev)
            except (ValueError, TypeError):
                dev = {}
        dev_str = " ".join(f"{k}={v}" for k, v in (dev or {}).items())
        status = "OK" if r["success"] else f"FAIL({r['reason']})"
        print(f"[{r['created_at']}] {r['username']:<20} {status:<16} "
              f"ip={r['ip']:<15} {dev_str}")
    return 0


def cmd_gen_secret(args):
    import secrets as _s
    print(_s.token_urlsafe(32))
    return 0


def main():
    ap = argparse.ArgumentParser(
        prog="backend.seed_user",
        description="Manajemen user login",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("add", help="tambah user")
    sp.add_argument("username")
    sp.add_argument("password")
    sp.add_argument("--full-name", default="")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("list", help="daftar user")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("activate", help="aktifkan user")
    sp.add_argument("username")
    sp.set_defaults(func=lambda a: cmd_activate(a, True))

    sp = sub.add_parser("deactivate", help="nonaktifkan user")
    sp.add_argument("username")
    sp.set_defaults(func=lambda a: cmd_activate(a, False))

    sp = sub.add_parser("reset-password", help="reset password user")
    sp.add_argument("username")
    sp.add_argument("password")
    sp.set_defaults(func=cmd_reset_password)

    sp = sub.add_parser("logs", help="riwayat login")
    sp.add_argument("username", nargs="?", default=None)
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_logs)

    sp = sub.add_parser("--gen-secret", help="generate AUTH_SECRET_KEY")
    sp.set_defaults(func=cmd_gen_secret)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
