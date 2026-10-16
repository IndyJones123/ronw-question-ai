"""Smoke test app live OCR: init window + box + 2 tombol mode + ganti mode, tanpa error."""
import tkinter as tk

import quiz_live_ocr_app as q

root = tk.Tk()
try:
    root.tk.call("tk", "scaling", 1.25)
except tk.TclError:
    pass
app = q.LiveQuizApp(root)
root.update()

assert app.box.visible, "capture box tidak muncul"
assert app.mode == "sage", f"mode awal harus sage, bukan {app.mode}"
assert len(app.bank["questions"]) == 376, "bank sage harus 376 soal"
assert app.btn_sage is not None and app.btn_hoppy is not None, "2 tombol mode harus ada"

# ganti mode lewat TOMBOL (invoke = klik beneran)
app.btn_hoppy.invoke()
root.update()
assert app.mode == "hoppy", f"tombol HOPPY gagal pindah mode ({app.mode})"
assert len(app.bank["questions"]) == 117, "bank hoppy harus 117 soal"
assert app.answer_label.cget("text") == "—", "jawaban harus direset pas ganti mode"

# toggle live (F9) bolak-balik
app.toggle_live()
assert not app._run_evt.is_set(), "F9 harus nge-pause live"
app.toggle_live()
assert app._run_evt.is_set(), "F9 kedua harus nge-resume live"

# --- panel ANSWER: max 2, terbaru di atas, jawaban lama auto-hapus ---
app._push_answer("Jawaban-1", "(Q1 00:00:01)")
assert app.answer_label.cget("text") == "Jawaban-1", "jawaban 1 harus jadi terbaru"
assert not app.prev_answer_label.winfo_ismapped(), "slot ke-2 belum boleh tampil"
app._push_answer("Jawaban-2", "(Q2 00:00:02)")
root.update()
assert app.answer_label.cget("text") == "Jawaban-2", "terbaru harus di paling atas"
assert app.prev_answer_label.winfo_ismapped(), "jawaban lama harus tetap tampil"
assert app.prev_answer_label.cget("text").startswith("Jawaban-1"), "urutan salah"
app._push_answer("Jawaban-3", "(Q3 00:00:03)")
root.update()
assert len(app._answers) == 2, f"harus dibatasi 2, bukan {len(app._answers)}"
assert app.answer_label.cget("text") == "Jawaban-3", "terbaru harus di atas"
assert app.prev_answer_label.cget("text").startswith("Jawaban-2"), "Jawaban-2 harus jadi lama"
assert "Jawaban-1" not in app._answers, "jawaban paling lama harus auto-hapus"
assert app.answer_label.cget("fg") == "#cc0000", "jawaban harus merah"
app._clear_answers()
assert app.answer_label.cget("text") == "—", "clear harus balikin placeholder"
assert not app.prev_answer_label.winfo_ismapped(), "clear harus sembunyikan slot ke-2"
print("  ANSWER_PANEL_OK (max 2, terbaru di atas, merah, auto-hapus)")

# balikin ke sage lewat tombol
app.btn_sage.invoke()
root.update()
assert app.mode == "sage", "tombol SAGE gagal balikin mode"


def finish():
    # biarin live loop jalan ~5 detik: capture + OCR + match beneran di layar ini
    status = app.status.cget("text")
    ocr = app.ocr_text.get("1.0", "end").strip()
    app.shutdown()
    root.destroy()
    print(f"GUI_OK mode={app.mode} soal={len(app.bank['questions'])} "
          f"live={'ON' if app._run_evt.is_set() else 'PAUSED'}")
    print(f"  status : {status[:110]}")
    print(f"  ocr    : {ocr[:110].replace(chr(10), ' / ') or '(kosong)'}")


root.after(5000, finish)
root.mainloop()
