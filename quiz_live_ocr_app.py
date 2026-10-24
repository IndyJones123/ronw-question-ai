#!/usr/bin/env python3
"""Quiz Live OCR App - live capture + OCR + jawaban langsung dari database (tanpa AI).

Beda sama quiz_answer_app.py (AI / CommandCode): app ini TIDAK connect AI sama
sekali. Cara kerja:

  1. Box merah (capture overlay) digeser ke atas soal, sama seperti app lama.
  2. Tiap LIVE_INTERVAL detik isi box di-screenshot -> OCR (Tesseract) -> teks.
  3. Teks dicocokkan ke database soal: quiz_databases/mode/sage.json atau hoppy.json.
  4. Kalau match, jawabannya langsung muncul di panel ANSWER + Answer Log.
     Panel ANSWER: teks MERAH, max 2 jawaban terakhir, terbaru di paling atas
     - jawaban ke-3 masuk -> jawaban paling lama otomatis kebuang.

Tombol cuma 2: SAGE dan HOPPY (pilih mode/database). Live jalan terus dari
app dibuka; tombol mode tinggal diklik buat ganti bank soal.

Hotkey (bukan tombol, biar UI tetap cuma 2 tombol):
  F9        = pause / resume live capture
  H         = hide / show box merah
  Ctrl+L    = clear log
  Ctrl+S    = save log ke .txt

Jalankan     : python quiz_live_ocr_app.py
Bench (CLI)  : python quiz_live_ocr_app.py --bench     # OCR capture lama + match

Config lewat env (opsional): LIVE_MODE, LIVE_INTERVAL, MATCH_THRESHOLD,
LIVE_PSM, LIVE_LANG, TESSERACT_CMD, TESSDATA_DIR, LIVE_SAVE_LAST.
"""
import argparse
import collections
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from difflib import SequenceMatcher
from tkinter import filedialog, scrolledtext, ttk

from dotenv import load_dotenv
from PIL import Image, ImageGrab

load_dotenv()

if getattr(sys, "frozen", False):
    # PyInstaller: data ter-bundle di _MEIPASS, file runtime (.env, captures,
    # quiz_databases) ditaruh di samping EXE.
    BASE_DIR = sys._MEIPASS
    _EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _EXE_DIR = BASE_DIR

# Console Windows default cp1252: karakter dari soal (mis. − U+2212) bikin
# UnicodeEncodeError pas print. Ganti jadi '?' supaya nggak crash.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

# DB soal: cari di samping EXE dulu (bisa diganti tanpa rebuild),
# kalau tidak ada pakai salinan ter-bundle di _MEIPASS.
_mode_dir_runtime = os.path.join(_EXE_DIR, "quiz_databases", "mode")
MODE_DIR = (_mode_dir_runtime if os.path.isdir(_mode_dir_runtime)
            else os.path.join(BASE_DIR, "quiz_databases", "mode"))
MODE_FILES = {"sage": "sage.json", "hoppy": "hoppy.json"}
CAPTURE_DIR = os.path.join(_EXE_DIR, "quiz_captures")
TRANSPARENT_COLOR = "magenta"  # warna yg dilubangi di overlay Windows

# ---- setelan live ----
def _env_flag(name, default="1"):
    return os.getenv(name, default).strip().lower() not in ("0", "false", "no", "off")


DEFAULT_MODE = os.getenv("LIVE_MODE", "sage").strip().lower()
LIVE_INTERVAL = float(os.getenv("LIVE_INTERVAL", "1.0"))          # detik antar cycle
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.65"))     # skor minimal match
OCR_LANG = os.getenv("LIVE_LANG", "eng")
OCR_PSM = int(os.getenv("LIVE_PSM", "11"))                        # 11 = sparse text (doang tanpa layout)
OCR_TIMEOUT = float(os.getenv("LIVE_OCR_TIMEOUT", "20"))
SAVE_LAST = _env_flag("LIVE_SAVE_LAST")                           # simpan live_last.png tiap cycle
MAX_CANDIDATE = 20                                                # kandidat yang di-refine pakai window ratio


def _find_tesseract():
    """Cari binary Tesseract: env -> PATH -> lokasi umum (install di home)."""
    cmd = os.getenv("TESSERACT_CMD", "").strip()
    if cmd and os.path.isfile(cmd):
        return cmd
    which = shutil.which("tesseract")
    if which:
        return which
    for cand in (
        os.path.expandvars(r"%USERPROFILE%\tesseract.exe"),
        r"C:\Users\alfia\tesseract.exe",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if os.path.isfile(cand):
            return cand
    return ""


TESSERACT_CMD = _find_tesseract()
TESSDATA_DIR = os.getenv("TESSDATA_DIR", "").strip()
if not TESSDATA_DIR and TESSERACT_CMD:
    _td = os.path.join(os.path.dirname(TESSERACT_CMD), "tessdata")
    if os.path.isdir(_td):
        TESSDATA_DIR = _td


# ---------------------------------------------------------------------------
# Database soal
# ---------------------------------------------------------------------------
class Q:
    """Satu soal dari bank, plus turunan teks buat matching (di-precompute)."""

    __slots__ = ("id", "question", "answer", "category", "qc", "q3", "qtok")

    def __init__(self, row, fallback_id=None):
        self.id = row.get("id", fallback_id)
        self.question = (row.get("question") or "").strip()
        self.answer = (row.get("answer") or "").strip()
        cats = row.get("categoryNames") or []
        self.category = row.get("categoryName") or (cats[0] if cats else "")
        self.qc = _compact(self.question)
        self.q3 = _trigrams(self.qc)
        self.qtok = _tokens(self.question)


def load_bank(mode):
    path = os.path.join(MODE_DIR, MODE_FILES[mode])
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    qs = [Q(row, i + 1) for i, row in enumerate(data.get("questions") or [])]
    if not qs:
        raise RuntimeError(f"database kosong: {path}")
    return {"mode": mode, "title": data.get("title", mode), "path": path, "questions": qs}


def _compact(s):
    """lowercase + buang semua non-alnum -> teks padat, tahan beda spasi/OCR."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _tokens(s):
    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if t]


def _trigrams(s):
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}


# ---------------------------------------------------------------------------
# Matching: trigram coverage (kandidat) -> window ratio / token coverage (skor)
# ---------------------------------------------------------------------------
def _best_window_ratio(qc, oc):
    """Skor terbaik potongan `oc` (sepanjang qc) vs qc, 0..1.

    Tahan sisipan junk di tengah soal (mis. opsi jawaban "18.5" nyelip di
    tengah kalimat hasil OCR): SequenceMatcher tetap nemu blok cocoknya.
    """
    if not qc or not oc:
        return 0.0
    if qc in oc:
        return 1.0
    m, n = len(qc), len(oc)
    if n <= m:
        return SequenceMatcher(None, qc, oc, autojunk=False).ratio()
    sm = SequenceMatcher(None, None, autojunk=False)
    best = 0.0
    step = max(1, m // 8)
    for i in range(0, n - m + 1, step):
        sm.set_seqs(qc, oc[i:i + m])
        if sm.real_quick_ratio() <= best:
            continue
        if sm.quick_ratio() <= best:
            continue
        r = sm.ratio()
        if r > best:
            best = r
            if best >= 0.99:
                break
    tail = SequenceMatcher(None, qc, oc[n - m:], autojunk=False).ratio()  # jendela terakhir
    return max(best, tail)


def _token_coverage(qtok, ocr_counter):
    """Coverage token pakai multiset: tiap token di soal harus ada di OCR
    sebanyak kemunculannya (soal '3/5 - 3/10' nggak bisa menang cuma karena
    angka 3/5/10 kebetulan nongol di layar)."""
    if not qtok:
        return 0.0
    need = collections.Counter(qtok)
    hit = sum(min(n, ocr_counter.get(t, 0)) for t, n in need.items())
    return hit / len(qtok)


def find_match(bank, ocr_text, threshold=None, want=3):
    """-> (best_Q or None, best_score, margin_ke_runner_up, top_list)

    top_list = [(score, Q), ...] urut menurun (buat debug/bench).
    """
    threshold = MATCH_THRESHOLD if threshold is None else threshold
    oc = _compact(ocr_text)
    if len(oc) < 3:
        return None, 0.0, 0.0, []
    o3 = _trigrams(oc)
    ocr_counter = collections.Counter(_tokens(ocr_text))

    pre = []
    for q in bank["questions"]:
        cov3 = (len(q.q3 & o3) / len(q.q3)) if q.q3 else 0.0
        tc = _token_coverage(q.qtok, ocr_counter)
        score0 = max(cov3, tc)
        if score0 >= 0.3:
            pre.append((score0, cov3, tc, q))
    pre.sort(key=lambda x: -x[0])

    scored = []
    for score0, cov3, tc, q in pre[:MAX_CANDIDATE]:
        wr = _best_window_ratio(q.qc, oc)
        # skor akhir: window ratio utama (urutan kata beneran);
        # token coverage cuma nolong kalau OCR nyisip junk di tengah soal
        # tapi semua katanya kebaca utuh (butuh >=4 token & coverage >=0.8).
        tc_ok = tc if (len(q.qtok) >= 4 and tc >= 0.8) else 0.0
        score = max(wr, tc_ok)
        scored.append((score, q, wr, cov3, tc))
    # tie-break: skor sama -> pilih soal plg panjang (lebih spesifik).
    # Penting buat pasangan terkandung, mis. "Which ... is not a Life Job?"
    # (Q23) jadi substring dari "Which ... is NOT a Life Job skill?" (Q70):
    # layar nunjukin Q70 -> dua-duanya 100%, jawaban bener = yg plg panjang.
    scored.sort(key=lambda x: (-x[0], -len(x[1].qc)))
    if not scored or scored[0][0] < threshold:
        top = [(s, q) for s, q, *_ in scored[:want]]
        best = scored[0] if scored else None
        margin = (scored[0][0] - scored[1][0]) if len(scored) > 1 else 0.0
        return (None, best[0] if best else 0.0, margin, top)
    margin = scored[0][0] - scored[1][0] if len(scored) > 1 else 0.0
    return scored[0][1], scored[0][0], margin, [(s, q) for s, q, *_ in scored[:want]]


# ---------------------------------------------------------------------------
# OCR (Tesseract CLI - tanpa pytesseract, tanpa AI)
# ---------------------------------------------------------------------------
def ocr_png(png_bytes):
    """PNG bytes -> teks hasil OCR."""
    if not TESSERACT_CMD:
        raise RuntimeError("Tesseract tidak ditemukan - set env TESSERACT_CMD")
    cmd = [TESSERACT_CMD, "stdin", "stdout", "-l", OCR_LANG, "--psm", str(OCR_PSM)]
    if TESSDATA_DIR:
        cmd += ["--tessdata-dir", TESSDATA_DIR]
    proc = subprocess.run(cmd, input=png_bytes, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, timeout=OCR_TIMEOUT)
    return proc.stdout.decode("utf-8", "replace")


# ---------------------------------------------------------------------------
# Capture box overlay (sama persis perilakunya dgn app lama:
# drag border = pindah, drag gagang kuning = resize)
# ---------------------------------------------------------------------------
class CaptureBox:
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
        self.f_top = tk.Frame(self.top, bg="red", height=b, cursor="fleur")
        self.f_bottom = tk.Frame(self.top, bg="red", height=b, cursor="fleur")
        self.f_left = tk.Frame(self.top, bg="red", width=b, cursor="fleur")
        self.f_right = tk.Frame(self.top, bg="red", width=b, cursor="fleur")
        self.f_top.pack(side="top", fill="x")
        self.f_bottom.pack(side="bottom", fill="x")
        self.f_left.pack(side="left", fill="y")
        self.f_right.pack(side="right", fill="y")

        self.size_label = tk.Label(self.f_top, text="", bg="red", fg="white",
                                   font=("Segoe UI", 8, "bold"))
        self.size_label.pack(side="left", padx=6)

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

    def _move_press(self, e):
        self._mx, self._my = e.x_root, e.y_root
        self._gx, self._gy = self.top.winfo_x(), self.top.winfo_y()

    def _move_drag(self, e):
        self.top.geometry(f"+{self._gx + e.x_root - self._mx}+{self._gy + e.y_root - self._my}")
        self._changed()

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
        """Area di dalam border merah (border nggak ikut ke-capture)."""
        self.top.update_idletasks()
        x, y = self.top.winfo_rootx(), self.top.winfo_rooty()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        b = self.BORDER
        return (x + b, y + b, x + w - b, y + h - b)

    def show(self):
        self.top.deiconify()
        self.visible = True

    def hide(self):
        self.top.withdraw()
        self.visible = False

    def toggle(self):
        self.hide() if self.visible else self.show()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class LiveQuizApp:
    def __init__(self, root):
        self.root = root
        root.title("Quiz Live OCR - sage / hoppy (tanpa AI)")
        root.geometry("640x760")
        root.minsize(520, 600)

        self.banks = {}
        self.bank = None
        self.mode = ""
        self._last_match_id = None
        self._answers = []            # jawaban terakhir, terbaru di index 0 (max 2)
        self._bbox = None
        self._stop_evt = threading.Event()     # set = app minta berhenti
        self._run_evt = threading.Event()      # set = live jalan (di-clear saat pause)
        self._run_evt.set()
        self._thread = None

        self.box = CaptureBox(root, on_change=self._refresh_coords)
        # LIVE_BOX="WxH+X+Y" -> set posisi/ukuran box awal (berguna buat test)
        live_box = os.getenv("LIVE_BOX", "").strip()
        if live_box:
            try:
                self.box.top.geometry(live_box)
                self.box._update_label()
            except tk.TclError:
                pass
        self._build_ui()
        self._set_mode(DEFAULT_MODE if DEFAULT_MODE in MODE_FILES else "sage",
                       initial=True)
        self._poll_bbox()

        if not TESSERACT_CMD:
            self._set_status("ERROR: Tesseract tidak ditemukan - set env TESSERACT_CMD")
            self.live_label.config(text="  TIDAK ADA OCR  ", fg="#b02a37")
        else:
            self._thread = threading.Thread(target=self._live_loop, daemon=True)
            self._thread.start()

    # ---------------- UI ----------------
    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")

        # CUMA 2 tombol di app ini: SAGE dan HOPPY
        self.btn_sage = tk.Button(top, text="SAGE", font=("Segoe UI", 12, "bold"),
                                  width=10, relief="raised", bd=2,
                                  command=lambda: self._set_mode("sage"))
        self.btn_sage.pack(side="left", padx=(0, 6))
        self.btn_hoppy = tk.Button(top, text="HOPPY", font=("Segoe UI", 12, "bold"),
                                   width=10, relief="raised", bd=2,
                                   command=lambda: self._set_mode("hoppy"))
        self.btn_hoppy.pack(side="left")

        self.live_label = tk.Label(top, text="  ● LIVE  ", font=("Segoe UI", 10, "bold"),
                                   fg="#0f5132", bg="#d1e7dd", padx=6, pady=4)
        self.live_label.pack(side="right")

        info = ttk.Frame(self.root, padding=(8, 0))
        info.pack(fill="x")
        self.mode_label = ttk.Label(info, text="", foreground="#475569")
        self.mode_label.pack(side="left")
        self.time_label = ttk.Label(info, text="", foreground="#146c43")
        self.time_label.pack(side="right")
        self.topmost_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(info, text="Always on top", variable=self.topmost_var,
                        command=self._apply_topmost).pack(side="right", padx=8)
        self._apply_topmost()

        hint = ttk.Label(
            self.root, padding=(8, 2),
            text="Live: box merah digeser ke soal, capture jalan terus tiap "
                 f"{LIVE_INTERVAL:g}s. F9 pause/resume - H hide box - "
                 "Ctrl+L clear log - Ctrl+S save log",
            foreground="#475569", wraplength=600, justify="left")
        hint.pack(fill="x")

        ans_frame = ttk.LabelFrame(self.root, text="ANSWER (2 terakhir - terbaru di atas)",
                                   padding=8)
        ans_frame.pack(fill="x", padx=8, pady=(4, 0))
        # 2 slot jawaban, urut terbaru di paling atas. Isi ke-3 masuk ->
        # jawaban paling lama otomatis kebuang (lihat _render_answers).
        slots = ttk.Frame(ans_frame)
        slots.pack(fill="x")
        self.answer_label = tk.Label(slots, text="—", font=("Segoe UI", 22, "bold"),
                                     fg="#cc0000", bg="#fff5f5", anchor="w",
                                     justify="left", wraplength=600, padx=6, pady=6)
        self.answer_label.pack(fill="x")
        self.prev_answer_label = tk.Label(slots, text="", font=("Segoe UI", 14),
                                          fg="#cc0000", bg="#fff5f5", anchor="w",
                                          justify="left", wraplength=600, padx=6, pady=6)
        # prev_answer_label di-pack lazily (cuma kalau ada jawaban ke-2)
        self.match_label = ttk.Label(ans_frame, text="Belum ada match", wraplength=600,
                                     justify="left", foreground="#475569")
        self.match_label.pack(fill="x", pady=(6, 0))
        self.score_label = ttk.Label(ans_frame, text="", foreground="#475569")
        self.score_label.pack(fill="x")

        ocr_frame = ttk.LabelFrame(self.root, text="OCR TEXT (terakhir)", padding=6)
        ocr_frame.pack(fill="x", padx=8, pady=4)
        self.ocr_text = scrolledtext.ScrolledText(ocr_frame, wrap="word", height=4,
                                                  font=("Consolas", 9), state="disabled")
        self.ocr_text.pack(fill="x")

        lframe = ttk.LabelFrame(self.root, text="Match Log", padding=6)
        lframe.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        self.log = scrolledtext.ScrolledText(lframe, wrap="word",
                                             font=("Consolas", 10), state="disabled")
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("q", foreground="#0b5ed7")
        self.log.tag_config("a", foreground="#cc0000")   # jawaban = merah
        self.log.tag_config("warn", foreground="#475569")
        self.log.tag_config("err", foreground="#b02a37")

        self.status = ttk.Label(self.root, text="Ready", relief="sunken",
                                anchor="w", padding=4)
        self.status.pack(fill="x", side="bottom")

        self.root.bind("<F9>", lambda e: self.toggle_live())
        self.root.bind("<h>", lambda e: self.toggle_box())
        self.root.bind("<H>", lambda e: self.toggle_box())
        self.root.bind("<Control-l>", lambda e: self.clear_log())
        self.root.bind("<Control-s>", lambda e: self.save_log())

    # ---------------- helpers ----------------
    def _apply_topmost(self):
        self.root.attributes("-topmost", self.topmost_var.get())

    def _set_status(self, msg):
        self.status.config(text=msg)

    def _refresh_coords(self):
        try:
            self._bbox = self.box.bbox()
            x1, y1, x2, y2 = self._bbox
            self.coord_text = f"Box: ({x1},{y1}) {x2-x1}x{y2-y1}"
        except Exception:
            pass

    def _poll_bbox(self):
        """Ambil bbox dari main thread (aman), tiap 300ms - dipakai worker live."""
        self._refresh_coords()
        self.root.after(300, self._poll_bbox)

    def _append_log(self, text, tag=None):
        self.log.config(state="normal")
        self.log.insert("end", text, tag or ())
        self.log.see("end")
        self.log.config(state="disabled")

    def _push_answer(self, answer, meta=""):
        """Catat 1 jawaban baru: terbaru di paling atas, max 2.

        Tiap output baru masuk, jawaban paling lama otomatis kebuang.
        meta = keterangan jawaban lama (Q + jam), tampil di baris kecil.
        """
        self._answers.insert(0, (answer, meta))
        del self._answers[2:]
        self._render_answers()

    def _clear_answers(self):
        self._answers = []
        self._render_answers()

    def _render_answers(self):
        """Gambar ulang 2 slot: terbaru (22pt) di atas, lama (14pt) di bawah."""
        newest = self._answers[0][0] if self._answers else "—"
        # answer_label cuma boleh bawa teks jawaban murni (dipakai test e2e)
        self.answer_label.config(text=newest)
        if len(self._answers) > 1:
            old, meta = self._answers[1]
            self.prev_answer_label.config(text=f"{old}   {meta}".rstrip())
            if not self.prev_answer_label.winfo_ismapped():
                self.prev_answer_label.pack(fill="x")
        else:
            self.prev_answer_label.pack_forget()

    def toggle_box(self):
        self.box.toggle()

    def toggle_live(self):
        if self._run_evt.is_set():
            self._run_evt.clear()
            self.live_label.config(text="  ❚❚ PAUSED (F9)  ", fg="#585656", bg="#e9ecef")
            self._set_status("Live di-pause - tekan F9 buat lanjut")
        else:
            self._resume_live()
            self.live_label.config(text="  ● LIVE  ", fg="#0f5132", bg="#d1e7dd")
            self._set_status("Live lanjut")

    def _resume_live(self):
        self._run_evt.set()

    # ---------------- mode (2 tombol) ----------------
    def _set_mode(self, mode, initial=False):
        if mode == self.mode and not initial:
            return
        if mode not in self.banks:
            try:
                self.banks[mode] = load_bank(mode)
            except Exception as e:  # noqa: BLE001
                messagebox_error = str(e)
                self._append_log(f"!!! Gagal load {mode}: {messagebox_error}\n", "err")
                self._set_status(f"Error load {mode}: {messagebox_error}")
                return
        self.mode = mode
        bank = self.banks[mode]
        self.bank = bank
        self._last_match_id = None

        # status tombol (aktif = warna solid)
        if mode == "sage":
            self.btn_sage.config(bg="#6f42c1", fg="white", relief="sunken")
            self.btn_hoppy.config(bg="#f0f0f0", fg="#212529", relief="raised")
        else:
            self.btn_hoppy.config(bg="#fd7e14", fg="#212529", relief="sunken")
            self.btn_sage.config(bg="#f0f0f0", fg="#212529", relief="raised")

        self.mode_label.config(text=f"Mode: {mode.upper()} | {bank['title']} | "
                                    f"{len(bank['questions'])} soal")
        self._clear_answers()
        self.match_label.config(text=f"Belum ada match ({mode.upper()})")
        self.score_label.config(text="")
        if not initial:
            self._append_log(f"\n>>> MODE {mode.upper()} - {len(bank['questions'])} soal "
                             f"({bank['title']})\n", "q")
            self._set_status(f"Mode {mode} aktif")

    # ---------------- live loop (worker thread) ----------------
    def _live_loop(self):
        os.makedirs(CAPTURE_DIR, exist_ok=True)
        while not self._stop_evt.is_set():
            if not self._run_evt.wait(timeout=0.2):
                continue  # paused
            t0 = time.perf_counter()
            try:
                bank = self.bank
                if bank is None:
                    self._stop_evt.wait(0.2)
                    continue
                bbox = self._bbox
                if not bbox:
                    self._stop_evt.wait(0.2)
                    continue
                img = ImageGrab.grab(bbox=bbox).convert("RGB")
                buf_png = _png_bytes(img)
                if SAVE_LAST:
                    with open(os.path.join(CAPTURE_DIR, "live_last.png"), "wb") as f:
                        f.write(buf_png)
                t_ocr0 = time.perf_counter()
                text = ocr_png(buf_png)
                t_ocr = time.perf_counter() - t_ocr0
                t_match0 = time.perf_counter()
                q, score, margin, top = find_match(bank, text)
                t_match = time.perf_counter() - t_match0
                total = time.perf_counter() - t0
                self.root.after(0, self._on_cycle, text, q, score, margin, top,
                                t_ocr, t_match, total, None)
            except Exception as e:  # noqa: BLE001
                self.root.after(0, self._on_cycle, "", None, 0.0, 0.0, [],
                                0.0, 0.0, time.perf_counter() - t0, str(e))
            # sisanya tunggu sampe interval penuh (bisa dipotong stop/pause)
            rest = LIVE_INTERVAL - (time.perf_counter() - t0)
            if rest > 0:
                if not self._run_evt.wait(timeout=rest):
                    continue

    # ---------------- hasil 1 cycle (main thread) ----------------
    def _on_cycle(self, text, q, score, margin, top, t_ocr, t_match, total, error):
        if error:
            self._append_log(f"!!! {error}\n", "err")
            self._set_status(f"Error: {error}")
            return

        self.ocr_text.config(state="normal")
        self.ocr_text.delete("1.0", "end")
        self.ocr_text.insert("1.0", (text.strip() or "(OCR kosong)"))
        self.ocr_text.config(state="disabled")

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if q is None:
            hint = ""
            if top:
                s, tq = top[0]
                hint = f" | best: {s*100:.0f}% {tq.question[:50]!r}"
            self._set_status(f"{ts} belum match (best {score*100:.0f}%){hint} | "
                             f"ocr {t_ocr:.2f}s match {t_match:.2f}s")
        else:
            if q.id != self._last_match_id:
                self._last_match_id = q.id
                cat = f" [{q.category}]" if q.category else ""
                # jawaban baru -> paling atas; ke-3 masuk -> yg paling lama hilang
                self._push_answer(q.answer, f"(Q{q.id}{cat} {ts})")
                self.match_label.config(text=f"Q{q.id}: {q.question}")
                self._append_log(f"\n[{ts}] Q{q.id}{cat} "
                                 f"{score*100:.0f}% (margin {margin*100:.0f}%)\n", "q")
                self._append_log(f"  {q.question}\n", "warn")
                self._append_log(f"  -> {q.answer}\n", "a")
            self.score_label.config(
                text=f"match {score*100:.0f}% (margin {margin*100:.0f}%) | "
                     f"soal Q{q.id}" + (f" | {q.category}" if q.category else ""))
            self._set_status(f"{ts} MATCH Q{q.id} {score*100:.0f}% | "
                             f"ocr {t_ocr:.2f}s match {t_match:.2f}s "
                             f"| total {total:.2f}s")

        self.time_label.config(text=f"⏱ {total:.2f}s")
        self._refresh_coords()

    # ---------------- log ----------------
    def clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text", "*.txt")],
            initialfile=f"quiz_live_log_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.log.get("1.0", "end"))
        self._set_status(f"Log disimpan -> {path}")

    def shutdown(self):
        self._stop_evt.set()
        self._run_evt.set()


def _png_bytes(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Bench: OCR semua capture lama + cocokkan ke 2 bank (tanpa GUI)
# ---------------------------------------------------------------------------
def bench(folder, limit=0, psm=None):
    global OCR_PSM
    if psm:
        OCR_PSM = psm
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    if limit:
        files = files[:limit]
    banks = {m: load_bank(m) for m in MODE_FILES}
    print(f"tesseract = {TESSERACT_CMD or 'TIDAK KETEMU'} | psm={OCR_PSM} | "
          f"threshold={MATCH_THRESHOLD} | {len(files)} gambar\n")
    hdr = f"{'file':<30} {'ocr(s)':>6} {'mode':<5} {'score':>5} {'id':>4} {'ans':<26} question"
    print(hdr)
    print("-" * len(hdr))
    for fn in files:
        path = os.path.join(folder, fn)
        with open(path, "rb") as f:
            raw = f.read()
        t0 = time.perf_counter()
        try:
            text = ocr_png(raw)
        except Exception as e:  # noqa: BLE001
            print(f"{fn:<30} OCR ERROR {e}")
            continue
        dt = time.perf_counter() - t0
        best = None
        for mode, bank in banks.items():
            q, score, margin, top = find_match(bank, text)
            if q is not None and (best is None or score > best[2]):
                best = (mode, q, score, margin, top)
        if best:
            mode, q, score, margin, top = best
            runner = f"+{margin*100:.0f}"
            print(f"{fn:<30} {dt:>6.2f} {mode:<5} {score*100:>4.0f}% Q{q.id:<4} "
                  f"{q.answer[:24]:<26} {q.question[:60]} (margin {runner}%)")
        else:
            # tanpa match -> tunjukin kandidat teratas biar keliatan skornya
            q2, s2, _, _ = find_match(banks["sage"], text, threshold=0.0)
            q3, s3, _, _ = find_match(banks["hoppy"], text, threshold=0.0)
            print(f"{fn:<30} {dt:>6.2f} {'-':<5} {'':>5} {'':>4} "
                  f"{'NO MATCH':<26} best sage {s2*100:.0f}%"
                  f"{' ' + q2.question[:36] if q2 else ''} | hoppy {s3*100:.0f}%")


def selftest():
    """Tiap soal di-DB dijadiin 'teks layar' -> matcher harus nemu soal itu sendiri.

    Versi noisy nyimulasi OCR (hapus 6% huruf acak, seed tetap) biar keliatan
    soal mana yg gampang nyasar ke soal lain.
    """
    import random
    rng = random.Random(7)
    total = ok = 0
    misses = []
    for mode in MODE_FILES:
        bank = load_bank(mode)
        for q in bank["questions"]:
            for noisy in (False, True):
                text = q.question
                if noisy:
                    text = "".join(c for c in text
                                   if not (c.isalnum() and rng.random() < 0.06))
                total += 1
                got, score, margin, top = find_match(bank, text)
                # sah: id sama, atau jawaban sama (teks duplikat di DB)
                if got is not None and (got.id == q.id or got.answer == q.answer):
                    ok += 1
                else:
                    alt = f"-> Q{got.id} ({score*100:.0f}%)" if got else "-> NO MATCH"
                    misses.append(f"{mode} Q{q.id}{'/noisy' if noisy else '':<8} "
                                  f"{alt} margin {margin*100:.0f}% | {q.question[:60]}")
    print(f"selftest: {ok}/{total} benar (id sama atau jawaban sama)")
    for m in misses:
        print("  MISS:", m)
    print(f"  (sisanya {total - ok} MISS = match ke soal lain dgn jawaban beda / no match)")
    return 0 if ok == total else 1


def _login_dialog() -> tuple[bool, dict]:
    """Tampilkan dialog login/daftar Tkinter. Return (success, user_data).

    user_data: {access_token, user:{...}, expires_in} kalau sukses.
    Mode "Daftar" memanggil POST /api/register; akun langsung aktif dan
    token dari respons dipakai langsung (tanpa perlu login ulang).
    """
    import auth_client

    win = tk.Tk()
    win.title("Login - Quiz Live OCR")
    win.geometry("380x280")
    win.resizable(False, False)
    try:
        win.tk.call("tk", "scaling", 1.25)
    except tk.TclError:
        pass
    win.attributes("-topmost", True)

    title_var = tk.StringVar(value="Quiz Live OCR - Login")
    ttk.Label(win, textvariable=title_var,
              font=("Segoe UI", 14, "bold")).pack(pady=(18, 10))

    form = ttk.Frame(win, padding=12)
    form.pack(fill="x")

    # field daftar (hanya tampil di mode register)
    lbl_name = ttk.Label(form, text="Nama lengkap (opsional):")
    entry_name = ttk.Entry(form, font=("Segoe UI", 11))

    lbl_user = ttk.Label(form, text="Username:")
    lbl_user.pack(anchor="w")
    entry_user = ttk.Entry(form, font=("Segoe UI", 11))
    entry_user.pack(fill="x", pady=(0, 8))
    ttk.Label(form, text="Password:").pack(anchor="w")
    entry_pw = ttk.Entry(form, show="*", font=("Segoe UI", 11))
    entry_pw.pack(fill="x", pady=(0, 8))

    lbl_pw2 = ttk.Label(form, text="Ulangi password:")
    entry_pw2 = ttk.Entry(form, show="*", font=("Segoe UI", 11))

    status_var = tk.StringVar(value="")
    status_lbl = ttk.Label(win, textvariable=status_var, foreground="#cc0000",
                          wraplength=340, justify="left")
    status_lbl.pack(pady=(0, 4))

    # cek backend hidup
    if not auth_client.check_health(None):
        status_var.set("Backend login tidak jalan. Start: .venv/Scripts/python -m uvicorn backend.main:app")

    result: dict = {}
    state = {"register": False}

    def set_register_mode(on: bool):
        state["register"] = on
        status_var.set("")
        if on:
            title_var.set("Quiz Live OCR - Daftar Akun")
            lbl_name.pack(anchor="w", before=lbl_user)
            entry_name.pack(fill="x", pady=(0, 8), before=lbl_user)
            lbl_pw2.pack(anchor="w", after=entry_pw)
            entry_pw2.pack(fill="x", pady=(0, 8), after=lbl_pw2)
            btn.configure(text="Daftar & Masuk")
            toggle_btn.configure(text="Sudah punya akun? Login")
        else:
            title_var.set("Quiz Live OCR - Login")
            lbl_name.pack_forget()
            entry_name.pack_forget()
            lbl_pw2.pack_forget()
            entry_pw2.pack_forget()
            entry_pw2.delete(0, "end")
            btn.configure(text="Login")
            toggle_btn.configure(text="Belum punya akun? Daftar")
        win.geometry("380x380" if on else "380x280")
        entry_user.focus_set()

    def toggle_mode():
        set_register_mode(not state["register"])

    def fail(msg: str):
        status_var.set(msg)
        entry_pw.delete(0, "end")
        entry_pw2.delete(0, "end")
        entry_pw.focus_set()

    def do_login(event=None):
        username = entry_user.get().strip()
        password = entry_pw.get()
        if not username or not password:
            status_var.set("Isi username dan password")
            return
        status_var.set("Memproses...")
        win.update_idletasks()
        ok, msg, data = auth_client.login(None, username, password)
        if ok:
            result.update(data)
            win.destroy()
        else:
            fail(msg)

    def do_register(event=None):
        username = entry_user.get().strip()
        password = entry_pw.get()
        password2 = entry_pw2.get()
        full_name = entry_name.get().strip()
        if not username or not password:
            status_var.set("Isi username dan password")
            return
        if len(username) < 3:
            status_var.set("Username minimal 3 karakter")
            return
        if len(password) < 6:
            status_var.set("Password minimal 6 karakter")
            return
        if password != password2:
            status_var.set("Ulangi password tidak sama")
            entry_pw2.delete(0, "end")
            entry_pw2.focus_set()
            return
        status_var.set("Mendaftarkan akun...")
        win.update_idletasks()
        ok, msg, data = auth_client.register(None, username, password, full_name)
        if ok:
            # akun sudah aktif + token dari server -> langsung masuk
            result.update(data)
            win.destroy()
        else:
            fail(msg)

    def submit(event=None):
        if state["register"]:
            do_register()
        else:
            do_login()

    btn = ttk.Button(win, text="Login", command=submit)
    btn.pack(pady=4)
    toggle_btn = ttk.Button(win, text="Belum punya akun? Daftar", command=toggle_mode)
    toggle_btn.pack(pady=2)
    win.bind("<Return>", submit)
    win.bind("<Escape>", lambda e: win.destroy())

    entry_user.focus_set()
    win.mainloop()

    return bool(result), result


def main():
    global LIVE_INTERVAL, MATCH_THRESHOLD, OCR_PSM
    ap = argparse.ArgumentParser(description="Quiz Live OCR (tanpa AI)")
    ap.add_argument("--bench", action="store_true",
                    help="OCR semua png di quiz_captures + cocokkan (tanpa GUI)")
    ap.add_argument("--selftest", action="store_true",
                    help="tiap soal di-DB di-fed balik ke matcher (akurasi murni)")
    ap.add_argument("--folder", default=CAPTURE_DIR, help="folder png untuk --bench")
    ap.add_argument("--limit", type=int, default=0, help="batasi jumlah gambar bench")
    ap.add_argument("--psm", type=int, default=None, help="override OCR PSM")
    ap.add_argument("--interval", type=float, default=None, help="detik antar capture")
    ap.add_argument("--threshold", type=float, default=None, help="skor minimal match")
    ap.add_argument("--skip-login", action="store_true",
                    help="lewati dialog login (debug/testing)")
    args = ap.parse_args()

    if args.bench:
        bench(args.folder, args.limit, args.psm)
        return
    if args.selftest:
        sys.exit(selftest())
    if args.interval:
        LIVE_INTERVAL = args.interval
    if args.threshold:
        MATCH_THRESHOLD = args.threshold
    if args.psm:
        OCR_PSM = args.psm

    # ---- gate login ----
    if not args.skip_login:
        ok, user_data = _login_dialog()
        if not ok:
            print("Login gagal atau dibatalkan. Aplikasi tidak dibuka.")
            return

    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.25)
    except tk.TclError:
        pass
    app = LiveQuizApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.shutdown(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
