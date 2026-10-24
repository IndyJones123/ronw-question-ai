#!/usr/bin/env python3
"""Client login untuk Quiz Live OCR App.

Dipanggil oleh quiz_live_ocr_app.py sebelum GUI dibuka:
  1. Kumpulkan info device (hostname, os, user, dll)
  2. POST /api/login ke backend (atau POST /api/register untuk akun baru)
  3. Kalau valid -> simpan token, return True
  4. Kalau gagal -> return False + pesan error

Tidak ada dependency selain requests + stdlib.
"""
from __future__ import annotations

import getpass
import json
import os
import platform
import socket
import sys

import requests

# URL backend (default lokal). Bisa override lewat env AUTH_API_URL.
DEFAULT_API_URL = os.getenv("AUTH_API_URL", "http://127.0.0.1:8000")
# Timeout koneksi + baca (detik). Login harus cepat.
TIMEOUT = 8


def collect_device_info() -> dict:
    """Kumpulkan info device buat audit login (disimpan di login_logs.device)."""
    info: dict = {
        "hostname": socket.gethostname() or "",
        "os": platform.platform() or "",
        "user": getpass.getuser() or "",
        "python": sys.version.split()[0] or "",
    }
    # resolusi layar (best-effort; tkinter belum tentu siap saat dipanggil)
    try:
        import tkinter
        _root = tkinter.Tk()
        _root.withdraw()
        info["screen"] = f"{_root.winfo_screenwidth()}x{_root.winfo_screenheight()}"
        _root.destroy()
    except Exception:
        pass
    # versi app
    try:
        info["app"] = "quiz-live-ocr-1.0"
    except Exception:
        pass
    return info


def login(base_url: str | None, username: str, password: str) -> tuple[bool, str, dict]:
    """POST /api/login -> (success, message, data).

    data berisi: access_token, expires_in, user{...}
    Kalau gagal, message = pesan error buat ditampilkan ke user.
    """
    url = (base_url or DEFAULT_API_URL).rstrip("/") + "/api/login"
    payload = {
        "username": username,
        "password": password,
        "device": collect_device_info(),
    }
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
    except requests.ConnectionError:
        return False, "Tidak bisa connect ke server login. Pastikan backend jalan.", {}
    except requests.Timeout:
        return False, "Server login tidak merespons (timeout).", {}
    except Exception as e:
        return False, f"Error koneksi: {e}", {}

    if resp.status_code == 401:
        return False, _error_detail(resp, "Login gagal"), {}

    if resp.status_code != 200:
        return False, f"Server error (HTTP {resp.status_code})", {}

    try:
        data = resp.json()
    except (ValueError, KeyError):
        return False, "Respons server tidak valid", {}

    token = data.get("access_token", "")
    if not token:
        return False, "Token tidak diterima dari server", {}

    return True, "Login berhasil", data


def register(base_url: str | None, username: str, password: str,
             full_name: str = "") -> tuple[bool, str, dict]:
    """POST /api/register -> (success, message, data).

    Akun langsung aktif dan respons berisi token, jadi user langsung login.
    Kalau gagal, message = pesan error buat ditampilkan ke user.
    """
    url = (base_url or DEFAULT_API_URL).rstrip("/") + "/api/register"
    payload = {
        "username": username,
        "password": password,
        "full_name": full_name,
        "device": collect_device_info(),
    }
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
    except requests.ConnectionError:
        return False, "Tidak bisa connect ke server login. Pastikan backend jalan.", {}
    except requests.Timeout:
        return False, "Server login tidak merespons (timeout).", {}
    except Exception as e:
        return False, f"Error koneksi: {e}", {}

    if resp.status_code in (400, 409, 422):
        return False, _error_detail(resp, "Pendaftaran gagal"), {}

    if resp.status_code not in (200, 201):
        return False, f"Server error (HTTP {resp.status_code})", {}

    try:
        data = resp.json()
    except ValueError:
        return False, "Respons server tidak valid", {}

    if not data.get("access_token"):
        return False, "Token tidak diterima dari server", {}

    return True, "Pendaftaran berhasil", data


def _error_detail(resp: requests.Response, default: str) -> str:
    """Ambil pesan 'detail' dari respons error FastAPI (string, atau list validasi)."""
    try:
        detail = resp.json().get("detail", default)
    except (ValueError, AttributeError):
        return default
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, dict) and first.get("msg"):
            return str(first["msg"])
    return default


def check_health(base_url: str | None) -> bool:
    """Cek apakah backend hidup (GET /api/health)."""
    url = (base_url or DEFAULT_API_URL).rstrip("/") + "/api/health"
    try:
        resp = requests.get(url, timeout=3)
        return resp.status_code == 200
    except Exception:
        return False
