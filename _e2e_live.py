"""E2E live: tampilkan screenshot soal fullscreen -> app live OCR harus match.

Bukti pipeline penuh tanpa AI: ImageGrab -> Tesseract -> matcher -> panel ANSWER.
Juga tes tombol mode (HOPPY/SAGE) lewat invoke().
"""
import os
import sys
import tkinter as tk

from PIL import Image, ImageTk

IMG = sys.argv[1] if len(sys.argv) > 1 else \
    os.path.join("quiz_captures", "capture_20261016_190835.png")
EXPECT_ANSWER = sys.argv[2] if len(sys.argv) > 2 else "North"
EXPECT_QID = sys.argv[3] if len(sys.argv) > 3 else "283"

root = tk.Tk()
root.withdraw()  # jendela app disembunyiin biar teks UI-nya nggak ikut ke-OCR
try:
    root.tk.call("tk", "scaling", 1.25)
except tk.TclError:
    pass

sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

# --- layar penuh: screenshot soal di-fit ke tengah layar ---
im = Image.open(IMG).convert("RGB")
scale = min(sw / im.width, sh / im.height)
nw, nh = int(im.width * scale), int(im.height * scale)
im_big = im.resize((nw, nh), Image.LANCZOS)
photo = ImageTk.PhotoImage(im_big)

stage = tk.Toplevel(root)
stage.overrideredirect(True)
stage.attributes("-topmost", True)
stage.configure(bg="black")
stage.geometry(f"{sw}x{sh}+0+0")
lbl = tk.Label(stage, image=photo, bg="black")
lbl.place(x=(sw - nw) // 2, y=(sh - nh) // 2)

# box capture: 86% layar, ditengah -> soal di screenshot pasti ke-cover
os.environ["LIVE_BOX"] = (f"{int(sw * 0.86)}x{int(sh * 0.86)}"
                          f"+{int(sw * 0.07)}+{int(sh * 0.07)}")

import quiz_live_ocr_app as q  # noqa: E402  (env LIVE_BOX harus kepasang dulu)

app = q.LiveQuizApp(root)
root.update()
# box harus di atas gambar (stage jangan di-lower: bisa masuk belakang window lain)
app.box.top.lift()
app.box.top.attributes("-topmost", True)

results = {}


def check_match():
    results["answer"] = app.answer_label.cget("text")
    results["status"] = app.status.cget("text")
    results["ocr"] = app.ocr_text.get("1.0", "end").strip()[:120]
    ok = results["answer"] == EXPECT_ANSWER
    print(("PASS" if ok else "FAIL") + f" match: jawaban={results['answer']!r} "
          f"(harusnya {EXPECT_ANSWER!r})")
    print(f"  status: {results['status'][:120]}")
    if not ok:
        print(f"  ocr   : {results['ocr'].replace(chr(10), ' / ')}")

    # tes tombol mode beneran (invoke = klik)
    app.btn_hoppy.invoke()
    root.update()
    hop_ok = app.mode == "hoppy" and len(app.bank["questions"]) == 117
    print(("PASS" if hop_ok else "FAIL") +
          f" tombol HOPPY: mode={app.mode} soal={len(app.bank['questions'])}")
    app.btn_sage.invoke()
    root.update()
    sage_ok = app.mode == "sage" and len(app.bank["questions"]) == 376
    print(("PASS" if sage_ok else "FAIL") +
          f" tombol SAGE balik: mode={app.mode} soal={len(app.bank['questions'])}")

    app.shutdown()
    root.destroy()
    print("E2E_" + ("OK" if (ok and hop_ok and sage_ok) else "FAIL"))


root.after(8000, check_match)
root.mainloop()
