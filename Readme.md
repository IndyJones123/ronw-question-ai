# Quiz Answer App (ronw-question-ai)

Aplikasi desktop Windows untuk menjawab soal kuis/ujian secara otomatis dari screenshot layar menggunakan AI (CommandCode API).

Cara kerja: aplikasi menampilkan box capture transparan (border merah) yang bisa digeser/diresize ke atas soal di layar. Sekali klik tombol "Give Me The Answer", isi box di-screenshot dan dikirim sebagai gambar ke AI, lalu jawabannya muncul di Answer Log.

## Fitur

- Box capture overlay: drag border merah untuk pindah, drag gagang kuning untuk resize
- Satu klik jawab: screenshot langsung dikirim ke CommandCode AI (vision model)
- Mode cepat (streaming): jawaban muncul per potongan di log - huruf pilihan kelihatan
  paling awal, tanpa nunggu model selesai nulis
- Timer kecepatan: status + label "huruf pertama X.Xs / total X.Xs" tiap jawaban
- Koneksi dipanaskan otomatis pas app dibuka (klik pertama juga cepat)
- Jawaban kosong otomatis diulang sekali dengan budget token lebih besar
- Model yang nolak parameter (reasoning_effort/temperature) otomatis dicoba ulang tanpa parameter itu
- Answer Log: riwayat tanya-jawab, bisa Clear dan Save ke .txt
- Preview capture terakhir + info koordinat/ukuran box
- Shortcut F9 = sama dengan klik "Give Me The Answer"
- Model AI bisa diganti lewat kolom teks di aplikasi
- Hasil capture tersimpan otomatis di folder `quiz_captures/`

### Kecepatan (terukur)

Benchmark 16 Okt 2026, model `deepseek/deepseek-v4-flash`, soal kuis 4 pilihan:

| Versi | Sampai huruf pilihan kelihatan | Total selesai |
| --- | --- | --- |
| Sebelum (tanpa streaming, minta penjelasan) | 4.08s (rata-rata) | 4.08s |
| Sesudah (streaming + reasoning off) | **1.2 - 2.2s** | **1.2 - 2.3s** |

Kunci kecepatan, dari yang paling berpengaruh:
1. `ANSWER_REASONING_EFFORT=off` - model tidak nalar dulu sebelum jawab (±1.9s hemat)
2. `COMMANDCODE_STREAM=1` - jawaban streaming, huruf muncul duluan
3. Prompt jawab saja, tanpa minta penjelasan + `ANSWER_MAX_TOKENS` pendek
4. `COMMANDCODE_WARMUP=1` - TLS handshake dipindah ke waktu app dibuka

## Struktur Project

```
ronw-question-ai/
├── quiz_answer_app.py   # aplikasi utama (tkinter)
├── test_speed.py        # tes offline (server lokal, tidak panggil API)
├── quiz_answer.spec     # config build PyInstaller -> QuizAnswer.exe
├── requirements.txt     # dependency Python
├── .env.example         # contoh config (copy jadi .env)
├── .env                 # config asli (jangan di-commit, ada API key)
├── Readme.md            # file ini
└── quiz_captures/       # hasil screenshot otomatis (dibuat saat running)
```

## Syarat

- Windows 10/11
- Python 3.11+ (untuk jalan dari source)
- API key CommandCode (https://commandcode.ai) yang support vision/image input

## Install (dari source)

```bash
cd Quiz/ronw-question-ai

# 1. Buat virtual environment
python -m venv .venv
.venv/Scripts/activate

# 2. Install dependency
pip install -r requirements.txt

# 3. Siapkan config
copy .env.example .env
```

Lalu edit file `.env` dan isi API key:

```
COMMANDCODE_API_KEY=isi_api_key_kamu_di_sini
```

## Running (dari source)

```bash
# pastikan venv aktif
.venv/Scripts/activate

python quiz_answer_app.py
```

Tanpa venv juga bisa selama `requests`, `python-dotenv`, `Pillow` sudah terinstall di Python global.

## Cara Pakai

1. Jalankan aplikasi, box merah otomatis muncul di tengah layar.
2. Buka soal (browser/LMS/aplikasi lain), geser box merah tepat di atas soal + pilihan jawabannya.
3. Klik "Give Me The Answer" (atau tekan F9).
4. Tunggu status "Thinking...", jawaban muncul per potongan di Answer Log
   (huruf pilihan kelihatan duluan), lalu lihat timing "huruf pertama X.Xs".
5. Ulangi untuk soal berikutnya, cukup geser box-nya saja.

Tombol lain:

- Hide/Show Box: sembunyikan atau tampilkan box merah
- Clear Log: hapus isi Answer Log
- Save Log: simpan Answer Log ke file .txt
- Always on top: jendela aplikasi selalu di depan (default on)

## Build EXE (opsional)

EXE dibuat dengan PyInstaller, jadi user lain bisa jalan tanpa install Python.

```bash
pip install pyinstaller
pyinstaller quiz_answer.spec
```

Hasil: `dist/QuizAnswer.exe`

PENTING: file `.env` jangan di-bundle, tapi taruh SEBELAH `QuizAnswer.exe`:

```
dist/
├── QuizAnswer.exe
└── .env
```

Kalau EXE crash saat dibuka, ubah `console=False` jadi `console=True` di `quiz_answer.spec`, build ulang, lalu jalankan dari cmd untuk lihat errornya.

## Konfigurasi (.env)

| Variable                 | Default                                | Keterangan                                                        |
| ------------------------ | -------------------------------------- | ----------------------------------------------------------------- |
| COMMANDCODE_API_KEY      | (wajib diisi)                          | API key CommandCode                                               |
| COMMANDCODE_BASE_URL     | https://api.commandcode.ai/provider/v1 | Base URL API                                                      |
| COMMANDCODE_MODEL        | deepseek/deepseek-v4-flash             | Model vision yang dipakai                                         |
| SYSTEM_PROMPT            | (lihat .env.example)                   | Instruksi ke AI, default: jawab singkat saja                      |
| REQUEST_TIMEOUT          | 90                                     | Timeout request ke AI (detik)                                     |
| **COMMANDCODE_STREAM**   | 1                                      | Streaming: jawaban muncul per potongan (huruf duluan). 0 = mati   |
| **COMMANDCODE_WARMUP**   | 1                                      | Panaskan koneksi pas app dibuka. 0 = mati                         |
| **ANSWER_REASONING_EFFORT** | off                                 | `off` = model nggak nalar dulu (paling ngefek ke kecepatan).      |
|                          |                                        | Kosongkan kalau model nolak param ini                             |
| **ANSWER_MAX_TOKENS**    | 128                                    | Batas token jawaban. Naikkan (512) untuk model tipe reasoning     |
| **ANSWER_RETRY_MAX_TOKENS** | 512                                 | Budget token kalau jawaban kosong -> auto ulang 1x                |
| **ANSWER_TEMPERATURE**   | 0                                      | 0 = deterministik. Kosongkan kalau model nolak temperature        |

Gambar di-resize max lebar 960px, kualitas JPEG 75 sebelum dikirim, biar payload kecil dan respons cepat.

### Tes tanpa buka aplikasi

```bash
python test_speed.py
```

Server lokal, tidak memanggil API, tidak butuh API key. Berguna buat cek perubahan kode
sebelum di-build jadi EXE.

## Troubleshooting

- "No API key" saat klik jawab: isi COMMANDCODE_API_KEY di `.env`, pastikan file `.env` satu folder dengan `.py`/`.exe`.
- Jawaban lama / timeout: naikkan REQUEST_TIMEOUT, atau perkecil box capture.
- Jawaban terasa lambat: cek `.env` isi `ANSWER_REASONING_EFFORT=off` dan `COMMANDCODE_STREAM=1`
  (dua ini yang paling ngefek), lalu baca angka "huruf pertama X.Xs" di status bar buat bandingkan.
- "Jawaban kosong" / log bertanda `finish=length`: `ANSWER_MAX_TOKENS` kekecilan buat model yang
  nge-generate reasoning sendiri -> naikkan ke 512. App juga otomatis ulang 1x dengan budget besar.
- HTTP 400 soal `reasoning_effort` / `temperature`: model yang dipilih nolak parameter itu.
  App otomatis buang param lalu ulang; kalau mau permanen, kosongkan `ANSWER_REASONING_EFFORT`
  / `ANSWER_TEMPERATURE` di `.env`. Catatan: tanpa `reasoning_effort=off` model tipe deepseek
  jadi lebih lambat karena nalar dulu.
- Box merah tidak transparan (kotak magenta): normal di sebagian environment non-Windows; aplikasi ini ditargetkan untuk Windows.
- EXE dibuka langsung tutup: build ulang dengan `console=True` untuk lihat pesan error.
- HTTP error dari API: cek API key, base URL, dan nama model masih valid.
- Mau ganti model: cek daftar lewat `GET {COMMANDCODE_BASE_URL}/models`. Model harus bisa dipanggil
  via `/chat/completions` (bukan tipe Anthropic `/messages`).

## Catatan

- Repo: https://github.com/IndyJones123/ronw-question-ai
- Gunakan dengan bijak, untuk belajar/latihan. Jangan dipakai untuk curang di ujian resmi.

HANYA BERLAKU PAKAI COMMANDCODE API . JIKA MAU ADJUST BISA ADJUST CODE SENDIRI PAKAI LLM ATAU AI SENDIRI DI BASE URL + BODYNYA
