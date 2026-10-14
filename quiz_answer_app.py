#!/usr/bin/env python3
"""Quiz Answer App v2 - image-only.

Alur baru (tanpa ketik soal):
  1. Buka aplikasi -> box capture merah langsung muncul di layar.
  2. Geser box tepat di atas soal (drag border buat pindah,
     drag gagang kuning buat resize).
  3. Klik SATU tombol "Give Me The Answer" -> isi box di-screenshot
     dan langsung dikirim sebagai gambar ke CommandCode AI.
  4. Jawaban muncul di Answer Log.

.env tetap di sebelah .py / .exe (jangan di-bundle ke EXE).
Build: pyinstaller quiz_answer.spec
"""
import base64
import datetime
import io
import os
import threading
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

        self.box = CaptureBox(root, on_change=self._refresh_coords)

        self._build_ui()
        self._refresh_key_status()
        self._refresh_coords()

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
        self.topmost_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(info, text="Always on top", variable=self.topmost_var,
                        command=self._apply_topmost).pack(side="right")
        self._apply_topmost()

        hint = ttk.Label(self.root, padding=(8, 0),
                         text="1. Geser box merah ke atas soal  2. Klik Give Me The Answer",
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
        self.btn_ask.config(text="Thinking...", state="disabled")
        self._set_status("Capture + kirim gambar ke AI...")
        threading.Thread(target=self._ask_thread, daemon=True).start()

    def _ask_thread(self):
        model = self.model_var.get().strip() or DEFAULT_MODEL
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            photo = ImageTk.PhotoImage(thumb)
            self.root.after(0, self._show_preview, photo, path)

            self.root.after(0, self._append_log,
                             f"\n[{ts}] IMAGE ({img.width}x{img.height}, {model}):\n{path}\n", "q")
            resp = requests.post(
                f"{BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json"},
                json={"model": model, "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text",
                         "text": "Answer the quiz question in this screenshot. "
                                 "Give the correct option/answer first, then a brief explanation."},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}"}},
                    ]},
                ]},
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
            answer = resp.json()["choices"][0]["message"]["content"].strip()
            self.root.after(0, self._append_log,
                             f"----- ANSWER -----\n{answer}\n{'='*50}\n", "a")
            self.root.after(0, self._set_status, "Jawaban diterima.")
        except Exception as e:  # noqa: BLE001
            self.root.after(0, self._append_log, f"!!! ERROR: {e}\n", "err")
            self.root.after(0, self._set_status, f"Error: {e}")
        finally:
            self.root.after(0, self._ask_done)

    def _show_preview(self, photo, path):
        self.preview_img = photo  # tahan referensi
        self.preview_label.config(image=self.preview_img, text="")
        self._set_status(f"Captured -> {path}")

    def _ask_done(self):
        self.busy = False
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
