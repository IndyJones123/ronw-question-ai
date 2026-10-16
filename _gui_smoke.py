"""Smoke test: app GUI harus bisa init (window + capture box) tanpa error, lalu tutup sendiri."""
import tkinter as tk

import quiz_answer_app as q

root = tk.Tk()
try:
    root.tk.call("tk", "scaling", 1.25)
except tk.TclError:
    pass
app_inst = q.QuizApp(root)   # init penuh: UI + CaptureBox + thread warm-up
assert app_inst.box.visible, "capture box tidak muncul"
assert app_inst.time_label is not None, "label timing tidak ada"
assert str(app_inst.btn_ask.cget("state")) == "normal", "tombol ask tidak siap"
root.update()
root.after(4000, root.destroy)   # biarin warm-up jalan ~4 detik
root.mainloop()
print("GUI_OK: app init + jalan 4 detik tanpa error, box visible=True")
