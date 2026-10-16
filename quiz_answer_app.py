#!/usr/bin/env python3
"""Quiz Answer App v2 - image-only, mode CEPAT (streaming).

Alur baru (tanpa ketik soal):
  1. Buka aplikasi -> box capture merah langsung muncul di layar.
  2. Geser box tepat di atas soal (drag border buat pindah,
     drag gagang kuning buat resize).
  3. Klik SATU tombol "Give Me The Answer" -> isi box di-screenshot
     dan langsung dikirim sebagai gambar ke CommandCode AI.
  4. Jawaban muncul per-potongan di Answer Log (huruf pilihan duluan),
     plus timing "huruf pertama X.Xs / total X.Xs".

Setelan kecepatan (.env): COMMANDCODE_STREAM, ANSWER_MAX_TOKENS,
ANSWER_REASONING_EFFORT (default 'off' = model nggak nalar dulu),
ANSWER_TEMPERATURE, COMMANDCODE_WARMUP (panaskan koneksi pas app dibuka).

.env tetap di sebelah .py / .exe (jangan di-bundle ke EXE).
Build: pyinstaller quiz_answer.spec
Tes offline: python test_speed.py
"""
import base64
import datetime
import io
import json
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import requests
from dotenv import load_dotenv
from PIL import Image, ImageGrab, ImageTk

load_dotenv()

BASE_URL = os.getenv("COMMANDCODE_BASE_URL", "https://api.commandcode.ai/provider/v1").rstrip("/")
DEFAULT_MODEL = os.getenv("COMMANDCODE_MODEL", "deepseek/deepseek-v4-flash")
API_KEY = os.getenv("COMMANDCODE_API_KEY", "")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a quiz answer bot. Look at the image, read the question and options, "
    "then reply with ONLY the final answer, as short as possible: "
    "option letter + short text (e.g. 'B) 42'). No explanation, no extra words, no markdown.",
)
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "90"))
CAPTURE_DIR = "quiz_captures"
TRANSPARENT_COLOR = "magenta"  # warna yg dilubangi di overlay Windows

MAX_IMG_W = 960   # resize sebelum kirim biar payload kecil & jawaban cepat
JPEG_QUALITY = 75

# ---- setelan kecepatan (buat cepat-cepatan) ----
# STREAM=1      : jawaban ditampilkan token per token (huruf pilihan muncul duluan)
# MAX_TOKENS    : batas token - jawaban pendek, sisanya dipotong biar nggak nge-generate basa-basi
# TEMPERATURE   : 0 = deterministik; kosongkan kalau model nolak parameter ini
# WARMUP=1      : sekali di awal app, koneksi (DNS+TCP+TLS+pool) dipanaskan dulu,
#                 jadi klik PERTAMA nggak kena biaya handshake
def _env_flag(name, default="1"):
    return os.getenv(name, default).strip().lower() not in ("0", "false", "no", "off")


STREAM = _env_flag("COMMANDCODE_STREAM")
# 128: dengan reasoning OFF model berhenti setelah jawaban pendek, jadi limit ini
# murni cadangan - naikin kalau ganti model ke tipe yang nge-generate reasoning sendiri.
MAX_TOKENS = int(os.getenv("ANSWER_MAX_TOKENS", "128"))
RETRY_MAX_TOKENS = int(os.getenv("ANSWER_RETRY_MAX_TOKENS", "512"))
TEMP_RAW = os.getenv("ANSWER_TEMPERATURE", "0").strip()
# 'off' bikin model tipe deepseek nggak buang token buat nalar dulu
# (terbukti: jawaban keluar ~2.1s vs ~4s versi lama, dan jawaban nggak pernah kosong).
# Kosongkan ("" ) kalau mau pakai default bawaan model.
REASONING_EFFORT = os.getenv("ANSWER_REASONING_EFFORT", "off").strip()
WARMUP = _env_flag("COMMANDCODE_WARMUP")

SESSION = requests.Session()  # keep-alive: TLS handshake cukup sekali, klik berikutnya tinggal pakai

# parameter opsional - aman dibuang kalau model nolak (HTTP 400)
OPTIONAL_PARAMS = ("reasoning_effort", "temperature")


def _post_chat(payload, stream, timeout):
    """POST /chat/completions dengan fallback parameter yang ditolak model.

    Beberapa model nolak reasoning_effort/temperature (HTTP 400) - kalau gitu
    param itu dibuang lalu dicoba sekali lagi, biar app tetap jalan walau model diganti.
    """
    last_body = ""
    for _ in range(2):
        resp = SESSION.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}",
                     "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
            stream=stream,
        )
        if resp.status_code != 400:
            return resp
        last_body = resp.text[:400]
        resp.close()
        dropped = [k for k in OPTIONAL_PARAMS if k in payload]
        if not dropped:
            break
        for k in dropped:
            payload.pop(k, None)
    raise RuntimeError(f"HTTP 400: {last_body}")


def _sse_text(lines):
    """Ambil potong teks (delta content) dari baris-baris response SSE chat/completions."""
    for raw in lines:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        line = (raw or "").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except ValueError:
            continue
        for ch in obj.get("choices") or ():
            chunk = ch.get("delta") or ch.get("message") or {}
            piece = chunk.get("content")
            if piece:
                yield piece


def _read_answer(resp, stream, t_start, on_piece=None):
    """Baca jawaban dari response API -> (answer, elapsed_ke_token_pertama).

    on_piece(dipanggil tiap potong teks) dipakai UI buat nulis jawaban
    sambil jalan, jadi huruf pilihan langsung kelihatan tanpa nunggu selesai.
    """
    ctype = resp.headers.get("Content-Type", "") or ""
    if stream and "event-stream" in ctype:
        parts, first = [], None
        for piece in _sse_text(resp.iter_lines(decode_unicode=True)):
            if first is None:
                first = time.perf_counter() - t_start
            parts.append(piece)
            if on_piece:
                on_piece(piece)
        return "".join(parts).strip(), first

    try:
        data = resp.json()
        ch = (data.get("choices") or [{}])[0]
        text = ((ch.get("message") or {}).get("content") or "").strip()
    except ValueError:
        # provider tetap ngirim SSE tapi content-type-nya bukan text/event-stream
        parts, first = [], None
        for piece in _sse_text(resp.text.splitlines()):
            if first is None:
                first = time.perf_counter() - t_start
            parts.append(piece)
            if on_piece:
                on_piece(piece)
        return "".join(parts).strip(), first

    if on_piece and text:
        on_piece(text)
    return text, (time.perf_counter() - t_start) if text else None


def warm_up():
    """Panaskan koneksi ke API sekali pas app dibuka (diam-diam, error diabaikan)."""
    if not WARMUP or not API_KEY or "isi_api_key" in API_KEY:
        return
    try:
        SESSION.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": DEFAULT_MODEL,
                  "messages": [{"role": "user", "content": "ping"}],
                  "max_tokens": 1},
            timeout=15,
        ).close()
    except Exception:  # noqa: BLE001
        pass


class CaptureBox:
    """Kotak overlay berlubang: drag border = pindah, drag gagang = resize."""

    MIN_W, MIN_H = 120, 80
    BORDER = 4

    def __init__(self, master, on_change=None):
        self.on_change = on_change
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        self.top.configure(bg=TRANSPARENT_COLOR)
        try:
            self.top.attributes("-transparentcolor", TRANSPARENT_COLOR)
        except tk.TclError:
            pass
        sw, sh = self.top.winfo_screenwidth(), self.top.winfo_screenheight()
        w, h = min(560, sw - 100), min(380, sh - 100)
        self.top.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//3}")

        b = self.BORDER
        # 4 sisi border merah (ini yg di-drag buat pindah)
        self.f_top = tk.Frame(self.top, bg="red", height=b, cursor="fleur")
        self.f_bottom = tk.Frame(self.top, bg="red", height=b, cursor="fleur")
        self.f_left = tk.Frame(self.top, bg="red", width=b, cursor="fleur")
        self.f_right = tk.Frame(self.top, bg="red", width=b, cursor="fleur")
        self.f_top.pack(side="top", fill="x")
        self.f_bottom.pack(side="bottom", fill="x")
        self.f_left.pack(side="left", fill="y")
        self.f_right.pack(side="right", fill="y")

        # label ukuran nempel di border atas
        self.size_label = tk.Label(self.f_top, text="", bg="red", fg="white",
                                   font=("Segoe UI", 8, "bold"))
        self.size_label.pack(side="left", padx=6)

        # gagang resize kuning di pojok kanan-bawah + sisi kanan/bawah
        self.grip_se = tk.Label(self.top, bg="yellow", width=2, height=1,
                                cursor="size_nw_se")
        self.grip_e = tk.Label(self.top, bg="yellow", width=1, height=4,
                               cursor="size_we")
        self.grip_s = tk.Label(self.top, bg="yellow", width=6, height=1,
                               cursor="size_ns")
        self.grip_se.place(relx=1.0, rely=1.0, anchor="se")
        self.grip_e.place(relx=1.0, rely=0.5, anchor="e")
        self.grip_s.place(relx=0.5, rely=1.0, anchor="s")

        for wdg in (self.f_top, self.f_bottom, self.f_left, self.f_right):
            wdg.bind("<ButtonPress-1>", self._move_press)
            wdg.bind("<B1-Motion>", self._move_drag)
        self.grip_se.bind("<ButtonPress-1>", self._rs_press)
        self.grip_se.bind("<B1-Motion>", lambda e: self._rs_drag(e, "se"))
        self.grip_e.bind("<ButtonPress-1>", self._rs_press)
        self.grip_e.bind("<B1-Motion>", lambda e: self._rs_drag(e, "e"))
        self.grip_s.bind("<ButtonPress-1>", self._rs_press)
        self.grip_s.bind("<B1-Motion>", lambda e: self._rs_drag(e, "s"))

        self.visible = True
        self._update_label()

    # -- pindah --
    def _move_press(self, e):
        self._mx, self._my = e.x_root, e.y_root
        self._gx, self._gy = self.top.winfo_x(), self.top.winfo_y()

    def _move_drag(self, e):
        self.top.geometry(f"+{self._gx + e.x_root - self._mx}+{self._gy + e.y_root - self._my}")
        self._changed()

    # -- resize --
    def _rs_press(self, e):
        self._rx, self._ry = e.x_root, e.y_root
        self._rw, self._rh = self.top.winfo_width(), self.top.winfo_height()

    def _rs_drag(self, e, mode):
        w, h = self._rw, self._rh
        if mode in ("se", "e"):
            w = max(self.MIN_W, self._rw + e.x_root - self._rx)
        if mode in ("se", "s"):
            h = max(self.MIN_H, self._rh + e.y_root - self._ry)
        self.top.geometry(f"{w}x{h}")
        self._changed()

    def _changed(self):
        self._update_label()
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass

    def _update_label(self):
        self.top.update_idletasks()
        self.size_label.config(
            text=f"  SOAL DI SINI  {self.top.winfo_width()}x{self.top.winfo_height()}")

    def bbox(self):
        self.top.update_idletasks()
        x, y = self.top.winfo_rootx(), self.top.winfo_rooty()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        b = self.BORDER
        return (x + b, y + b, x + w - b, y + h - b)  # buang border merah

    def show(self):
        self.top.deiconify()
        self.visible = True

    def hide(self):
        self.top.withdraw()
        self.visible = False

    def toggle(self):
        self.hide() if self.visible else self.show()


class QuizApp:
    def __init__(self, root):
        self.root = root
        root.title("Quiz Answer - CommandCode AI (image mode)")
        root.geometry("560x640")
        root.minsize(480, 520)
        self.busy = False
        self.preview_img = None
        self.last_path = ""
        self._streaming = False
        self._t0 = 0.0

        self.box = CaptureBox(root, on_change=self._refresh_coords)

        self._build_ui()
        self._refresh_key_status()
        self._refresh_coords()
        # panaskan koneksi biar klik pertama nggak kena biaya TLS handshake
        threading.Thread(target=warm_up, daemon=True).start()

    # ---------- UI ----------
    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")

        self.btn_ask = ttk.Button(top, text="Give Me The Answer",
                                  command=self.ask_answer)
        self.btn_ask.pack(side="left", padx=4)

        self.btn_box = ttk.Button(top, text="Hide Box",
                                  command=self.toggle_box)
        self.btn_box.pack(side="left", padx=4)

        ttk.Button(top, text="Clear Log", command=self.clear_log).pack(side="left", padx=4)
        ttk.Button(top, text="Save Log", command=self.save_log).pack(side="left", padx=4)

        cfg = ttk.Frame(self.root, padding=(8, 0))
        cfg.pack(fill="x")
        ttk.Label(cfg, text="Model:").pack(side="left")
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        ttk.Entry(cfg, textvariable=self.model_var, width=30).pack(side="left", padx=4)
        self.key_label = ttk.Label(cfg, text="")
        self.key_label.pack(side="left", padx=8)

        info = ttk.Frame(self.root, padding=(8, 4))
        info.pack(fill="x")
        self.coord_label = ttk.Label(info, text="", foreground="#0b5ed7")
        self.coord_label.pack(side="left")
        self.time_label = ttk.Label(info, text="", foreground="#146c43")
        self.time_label.pack(side="right", padx=8)
        self.topmost_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(info, text="Always on top", variable=self.topmost_var,
                        command=self._apply_topmost).pack(side="right")
        self._apply_topmost()

        hint = ttk.Label(self.root, padding=(8, 0),
                         text="1. Geser box merah ke atas soal  2. Klik Give Me The Answer (F9)  "
                              "3. Jawaban muncul per huruf, langsung kepencet",
                         foreground="gray")
        hint.pack(fill="x")

        prev_frame = ttk.LabelFrame(self.root, text="Last capture", padding=6)
        prev_frame.pack(fill="x", padx=8, pady=(4, 0))
        self.preview_label = ttk.Label(prev_frame, text="Belum ada capture")
        self.preview_label.pack()

        lframe = ttk.LabelFrame(self.root, text="Answer Log", padding=6)
        lframe.pack(fill="both", expand=True, padx=8, pady=6)
        self.log = scrolledtext.ScrolledText(lframe, wrap="word",
                                             font=("Consolas", 10), state="disabled")
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("q", foreground="#0b5ed7")
        self.log.tag_config("a", foreground="#146c43")
        self.log.tag_config("err", foreground="#b02a37")

        self.status = ttk.Label(self.root, text="Ready", relief="sunken",
                                anchor="w", padding=4)
        self.status.pack(fill="x", side="bottom")
        self.root.bind("<F9>", lambda e: self.ask_answer())

    # ---------- helpers ----------
    def _apply_topmost(self):
        self.root.attributes("-topmost", self.topmost_var.get())

    def _set_status(self, msg):
        self.status.config(text=msg)
        self.root.update_idletasks()

    def _refresh_key_status(self):
        if API_KEY and "isi_api_key" not in API_KEY:
            self.key_label.config(text="key ****" + API_KEY[-4:])
        else:
            self.key_label.config(text="NO KEY - isi .env !", foreground="red")

    def _refresh_coords(self):
        try:
            x1, y1, x2, y2 = self.box.bbox()
            self.coord_label.config(text=f"Box: ({x1},{y1}) {x2-x1}x{y2-y1}")
        except Exception:
            pass

    def toggle_box(self):
        self.box.toggle()
        self.btn_box.config(text="Show Box" if not self.box.visible else "Hide Box")

    def _append_log(self, text, tag=None):
        self.log.config(state="normal")
        self.log.insert("end", text, tag or ())
        self.log.see("end")
        self.log.config(state="disabled")

    def _start_stream(self):
        """Bikin baris jawaban kosong di log -> jawaban ditulis nempel di situ."""
        self.log.config(state="normal")
        self.log.insert("end", "----- ANSWER -----\n", "a")
        self.log.see("end")
        self.log.config(state="disabled")
        self._streaming = True

    def _append_live(self, text):
        """Nulis potongan jawaban ke baris yang lagi streaming (dari thread -> dipanggil via after)."""
        if not self._streaming:
            return
        self.log.config(state="normal")
        self.log.insert("end", text, "a")
        self.log.see("end")
        self.log.config(state="disabled")

    def _stream_status(self):
        """Status "Jawaban keluar dalam X.Xs" - dipanggil saat token pertama masuk."""
        if not self._streaming:
            return
        self._set_status(f"Jawaban keluar dalam {time.perf_counter() - self._t0:.1f}s ...")

    # ---------- ask AI (image) ---------- ( fungsi utama yang lempar ke ai )
    def ask_answer(self):
        if self.busy:
            return
        if not API_KEY or "isi_api_key" in API_KEY:
            messagebox.showerror("No API key", "Isi COMMANDCODE_API_KEY di file .env dulu.")
            return
        if not self.box.visible:
            self.box.show()
            self.btn_box.config(text="Hide Box")
        self.busy = True
        self._t0 = time.perf_counter()  # timer mulai dari DETIK INI (klik), bukan dari mulai thread
        self.btn_ask.config(text="Thinking...", state="disabled")
        self._set_status("Capture + kirim gambar ke AI...")
        threading.Thread(target=self._ask_thread, daemon=True).start()

    def _ask_thread(self):
        model = self.model_var.get().strip() or DEFAULT_MODEL
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t0 = self._t0
        started = False  # udah bikin baris "ANSWER" di log belum (dipakai buat nutup di error)
        try:
            bbox = self.box.bbox()
            img = ImageGrab.grab(bbox=bbox).convert("RGB")
            if img.width > MAX_IMG_W:
                img = img.resize((MAX_IMG_W, int(img.height * MAX_IMG_W / img.width)))
            os.makedirs(CAPTURE_DIR, exist_ok=True)
            tsf = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(CAPTURE_DIR, f"capture_{tsf}.png")
            img.save(path)
            self.last_path = path

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=JPEG_QUALITY)
            b64 = base64.b64encode(buf.getvalue()).decode()

            thumb = img.copy()
            thumb.thumbnail((440, 150))
            self.root.after(0, self._show_preview, thumb, path)

            self.root.after(0, self._append_log,
                             f"\n[{ts}] IMAGE ({img.width}x{img.height}, {model}):\n{path}\n", "q")

            payload = self._build_payload(model, b64)

            self.root.after(0, self._start_stream)
            started = True
            # on_piece jalan di thread ini, tapi nulis ke Tk tetap lewat after()
            answer, first_dt = self._ask_api(payload, t0)
            if not answer:
                raise RuntimeError("AI tidak mengirim jawaban - cek model/base URL")
            total = time.perf_counter() - t0
            self.root.after(0, self._finish_answer, answer, first_dt, total)
        except Exception as e:  # noqa: BLE001
            if started:
                self.root.after(0, self._append_log, f"\n{'=' * 50}\n", "a")
                self.root.after(0, self._finish_stream_flag)
            self.root.after(0, self._append_log, f"!!! ERROR: {e}\n", "err")
            self.root.after(0, self._set_status, f"Error: {e}")
        finally:
            self.root.after(0, self._ask_done)

    # ---------- request ke AI ----------
    @staticmethod
    def _build_payload(model, b64):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text",
                     "text": "Answer the quiz question in this screenshot. "
                             "Reply with ONLY the final answer (option letter + short text), "
                             "no explanation, no reasoning."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{b64}"}},
                ]},
            ],
            "max_tokens": MAX_TOKENS,
            "stream": STREAM,
        }
        if REASONING_EFFORT:
            payload["reasoning_effort"] = REASONING_EFFORT
        if TEMP_RAW:
            try:
                payload["temperature"] = float(TEMP_RAW)
            except ValueError:
                pass  # bukan angka -> lepas, biar default model
        return payload

    @staticmethod
    def _request(payload, stream=None):
        if stream is None:
            stream = STREAM
        resp = _post_chat(payload, stream, TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        return resp

    def _ask_api(self, payload, t0):
        """-> (answer, elapsed_ke_huruf_pertama).

        Tarik jawaban (streaming). Kalau keluar KOSONG (biasanya reasoning kehabisan
        max_tokens di model tertentu), ulang sekali dengan budget token lebih besar.
        Tiap potong teks langsung dilempar ke log, jadi huruf pilihan cepat kelihatan.
        """
        seen_first = [False]

        def on_piece(piece):
            self.root.after(0, self._append_live, piece)
            if not seen_first[0]:
                seen_first[0] = True
                self.root.after(0, self._stream_status)

        answer, first_dt = _read_answer(self._request(payload), STREAM, t0, on_piece=on_piece)
        if answer:
            return answer, first_dt
        self.root.after(0, self._stream_status)
        retry = dict(payload, max_tokens=RETRY_MAX_TOKENS)
        return _read_answer(self._request(retry), STREAM, t0, on_piece=on_piece)

    def _show_preview(self, thumb, path):
        self.preview_img = ImageTk.PhotoImage(thumb)  # bikin PhotoImage di main thread
        self.preview_label.config(image=self.preview_img, text="")
        self._set_status(f"Captured -> {path}")

    def _finish_answer(self, answer, first_dt, total):
        """Tutup baris streaming + kasih ringkasan timing di log."""
        self.log.config(state="normal")
        self.log.insert("end", "\n", "a")
        note = f"\n⏱ total {total:.2f}s"
        if first_dt:
            note += f"  (huruf pertama keluar di {first_dt:.2f}s)"
        note += f"\n{'=' * 50}\n"
        self.log.insert("end", note, "a")
        self.log.see("end")
        self.log.config(state="disabled")
        self._streaming = False
        shown = first_dt if first_dt else total
        self._set_status(f"Jawaban diterima dalam {shown:.2f}s (total {total:.2f}s)")
        self.time_label.config(text=f"⏱ {shown:.2f}s")

    def _finish_stream_flag(self):
        self._streaming = False

    def _ask_done(self):
        self.busy = False
        self._streaming = False
        self.btn_ask.config(text="Give Me The Answer", state="normal")

    # ---------- log ----------
    def clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text", "*.txt")],
            initialfile=f"quiz_log_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.log.get("1.0", "end"))
        self._set_status(f"Log disimpan -> {path}")


def main():
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.25)
    except tk.TclError:
        pass
    QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
