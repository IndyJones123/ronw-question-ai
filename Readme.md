# Quiz Live OCR

Aplikasi quiz answer dengan dua mode:
1. **Quiz Live OCR** (`quiz_live_ocr_app.py`) — capture layar → OCR (Tesseract) → cocokkan ke database soal lokal. Tanpa AI.
2. **Quiz Answer App** (`quiz_answer_app.py`) — capture layar → kirim gambar ke CommandCode AI → jawaban langsung.

Kedua app butuh login dulu (autentikasi ke backend FastAPI + PostgreSQL).

---

## Prasyarat

- Python 3.11+
- PostgreSQL 14+ (default: lokal port 5432)
- Tesseract OCR (untuk mode Live OCR) — install binary dari https://github.com/_ubt-fork/tesseract/wiki
- Virtual environment (`uv` atau `venv`)

---

## Setup Backend

### 1. Buat database + user PostgreSQL

```sql
CREATE USER quiz_auth WITH PASSWORD 'password_kamu';
CREATE DATABASE quiz_auth OWNER quiz_auth;
```

Default (dari `backend/.env.example`):

| Variable      | Default       |
|---------------|---------------|
| DB_HOST       | 127.0.0.1     |
| DB_PORT       | 5432          |
| DB_NAME       | quiz_auth     |
| DB_USER       | quiz_auth     |
| DB_PASSWORD   | (kosong, harus diisi) |

### 2. Install dependencies

```bash
uv venv .venv
uv pip install --python .venv/Scripts/python.exe fastapi uvicorn psycopg[binary] pydantic python-dotenv requests Pillow
```

Atau dengan pip (jika venv punya pip):

```bash
python -m venv .venv
.venv/Scripts/activate
pip install fastapi uvicorn psycopg[binary] pydantic python-dotenv requests Pillow
```

### 3. Konfigurasi backend/.env

```bash
cp backend/.env.example backend/.env
```

Isi `backend/.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=quiz_auth
DB_USER=quiz_auth
DB_PASSWORD=password_kamu

# Generate: python -m backend.seed_user --gen-secret
AUTH_SECRET_KEY=<hasil gen-secret, min 16 karakter>
AUTH_TOKEN_TTL_HOURS=12

AUTH_BIND_HOST=127.0.0.1
AUTH_BIND_PORT=8000
```

Generate secret key:

```bash
python -m backend.seed_user --gen-secret
```

### 4. Buat user login (TIDAK ada user default — harus dibuat manual)

Backend tidak punya endpoint register. User dibuat via CLI `seed_user`:

```bash
# Tambah user
python -m backend.seed_user add admin admin123 --full-name "Admin"

# Lihat daftar user
python -m backend.seed_user list

# Reset password
python -m backend.seed_user reset-password admin password_baru

# Aktifkan / nonaktifkan user
python -m backend.seed_user activate admin
python -m backend.seed_user deactivate admin

# Lihat riwayat login
python -m backend.seed_user logs
python -m backend.seed_user logs admin --limit 20
```

Password minimal 6 karakter.

### 5. Jalankan backend

Migrasi database berjalan otomatis saat startup (tabel `users` + `login_logs` dibuat jika belum ada).

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Atau pakai host/port dari config:

```bash
python -c "import uvicorn; from backend import config; uvicorn.run('backend.main:app', host=config.BIND_HOST, port=config.BIND_PORT)"
```

Cek kesehatan:

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok","db":true}
```

### API Endpoints

| Method | Path              | Auth  | Keterangan                          |
|--------|-------------------|-------|-------------------------------------|
| GET    | /api/health       | -     | Cek koneksi DB                      |
| POST   | /api/login        | -     | Login → token + info user           |
| GET    | /api/me           | Bearer | Profil user dari token             |
| GET    | /api/login-logs   | Bearer | Riwayat login + device (audit)     |

Contoh login:

```bash
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","device":{"app":"test"}}'
```

Token TTL default 12 jam. Setiap login (sukses/gagal) dicatat di `login_logs` beserta info device, IP, dan user-agent.

---

## Menjalankan App

### Quiz Live OCR (tanpa AI)

Butuh Tesseract terinstall. Set path binary di `.env` jika perlu:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

```bash
python quiz_live_ocr_app.py
```

Mode database soal (tombol SAGE / HOPPY) membaca dari `quiz_databases/mode/*.json`.

Hotkey: F9 = pause/resume, H = hide/show box, Ctrl+L = clear log, Ctrl+S = save log.

### Quiz Answer App (AI / CommandCode)

Copy `.env.example` → `.env`, isi API key CommandCode:

```bash
cp .env.example .env
```

```env
COMMANDCODE_API_KEY=isi_api_key_kamu
COMMANDCODE_BASE_URL=https://api.commandcode.ai/provider/v1
COMMANDCODE_MODEL=deepseek/deepseek-v4-flash
```

```bash
python quiz_answer_app.py
```

---

## Struktur Project

```
ronw-question-ai/
├── backend/
│   ├── main.py              # FastAPI app (login, health, me, login-logs)
│   ├── config.py            # Konfigurasi dari .env
│   ├── db.py                # Koneksi + migrasi PostgreSQL (psycopg 3)
│   ├── security.py          # Hash password PBKDF2 + HMAC token
│   ├── seed_user.py         # CLI manajemen user
│   ├── schemas.py           # Pydantic models
│   ├── .env.example         # Template config backend
│   └── migrations/
│       └── 001_init.sql     # Skema users + login_logs
├── auth_client.py           # Client login (dipanggil sebelum GUI)
├── quiz_live_ocr_app.py     # App: Live OCR + match database soal
├── quiz_answer_app.py       # App: AI answer via CommandCode
├── requirements.txt         # Dependencies (frontend)
├── .env.example             # Template config CommandCode AI
└── quiz_databases/          # Database soal JSON (sage.json, hoppy.json)
```

---

## Catatan

- Backend bind default `127.0.0.1` — hanya lokal, jangan terekspos ke LAN.
- Tidak ada endpoint register. User hanya bisa dibuat via `seed_user` CLI.
- Login gagal pun dicatat di audit log (alasan: `unknown_user`, `bad_password`, `inactive`).
- Respons login untuk user yang tidak ada / nonaktif sengaja dibuat sama waktunya dengan user yang ada (mencegah timing attack).
