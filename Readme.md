# Quiz Answer App (ronw-question-ai)

Aplikasi desktop Windows untuk menjawab soal kuis/ujian secara otomatis dari screenshot layar menggunakan AI (CommandCode API).

Cara kerja: aplikasi menampilkan box capture transparan (border merah) yang bisa digeser/diresize ke atas soal di layar. Sekali klik tombol "Give Me The Answer", isi box di-screenshot dan dikirim sebagai gambar ke AI, lalu jawabannya muncul di Answer Log.

## Fitur

- Box capture overlay: drag border merah untuk pindah, drag gagang kuning untuk resize
- Satu klik jawab: screenshot langsung dikirim ke CommandCode AI (vision model)
- Answer Log: riwayat tanya-jawab, bisa Clear dan Save ke .txt
- Preview capture terakhir + info koordinat/ukuran box
- Shortcut F9 = sama dengan klik "Give Me The Answer"
- Model AI bisa diganti lewat kolom teks di aplikasi
- Hasil capture tersimpan otomatis di folder `quiz_captures/`

## Struktur Project

```
ronw-question-ai/
├── quiz_answer_app.py   # aplikasi utama (tkinter)
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
4. Tunggu status "Thinking...", jawaban muncul di Answer Log.
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

| Variable             | Default                                | Keterangan                                   |
| -------------------- | -------------------------------------- | -------------------------------------------- |
| COMMANDCODE_API_KEY  | (wajib diisi)                          | API key CommandCode                          |
| COMMANDCODE_BASE_URL | https://api.commandcode.ai/provider/v1 | Base URL API                                 |
| COMMANDCODE_MODEL    | deepseek/deepseek-v4-flash             | Model vision yang dipakai                    |
| SYSTEM_PROMPT        | (lihat .env.example)                   | Instruksi ke AI, default: jawab singkat saja |
| REQUEST_TIMEOUT      | 60                                     | Timeout request ke AI (detik)                |

Gambar di-resize max lebar 960px, kualitas JPEG 75 sebelum dikirim, biar payload kecil dan respons cepat.

## Troubleshooting

- "No API key" saat klik jawab: isi COMMANDCODE_API_KEY di `.env`, pastikan file `.env` satu folder dengan `.py`/`.exe`.
- Jawaban lama / timeout: naikkan REQUEST_TIMEOUT, atau perkecil box capture.
- Box merah tidak transparan (kotak magenta): normal di sebagian environment non-Windows; aplikasi ini ditargetkan untuk Windows.
- EXE dibuka langsung tutup: build ulang dengan `console=True` untuk lihat pesan error.
- HTTP error dari API: cek API key, base URL, dan nama model masih valid.

## Catatan

- Repo: https://github.com/IndyJones123/ronw-question-ai
- Gunakan dengan bijak, untuk belajar/latihan. Jangan dipakai untuk curang di ujian resmi.

HANYA BERLAKU PAKAI COMMANDCODE API . JIKA MAU ADJUST BISA ADJUST CODE SENDIRI PAKAI LLM ATAU AI SENDIRI DI BASE URL + BODYNYA
