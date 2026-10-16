"""Tes offline helper kecepatan quiz_answer_app.py (server lokal, TANPA panggil API).

Jalankan:  python test_speed.py
Meng-cover: parser SSE, fallback JSON, streaming bertahap, payload aplikasi
(stream/reasoning_effort/max_tokens), dan fallback parameter yang ditolak model.
"""
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quiz_answer_app as app  # noqa: E402

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + ("  | " + str(detail) if detail else ""))


# ---------- 1. parser SSE murni ----------
got = "".join(app._sse_text([
    'data: {"choices":[{"delta":{"content":"B"}}]}',
    "",
    'data: {"choices":[{"delta":{"content":") 42"}}]}',
    "data: [DONE]",
    'data: {"choices":[{"delta":{"content":"IGNORED"}}]}',
]))
check("_sse_text: delta + stop di [DONE]", got == "B) 42", repr(got))

got = "".join(app._sse_text([
    b'data: {"choices":[{"delta":{"content":"X"}}]}',
    b"data: [DONE]",
]))
check("_sse_text: input bytes", got == "X", repr(got))

got = "".join(app._sse_text(['data: {"choices":[{"message":{"content":"Y"}}]}']))
check("_sse_text: bentuk message (bukan delta)", got == "Y", repr(got))

got = "".join(app._sse_text([": ping comment", "data: bukan-json", 'data: {"choices":[]}']))
check("_sse_text: buang baris sampah tanpa crash", got == "", repr(got))


# ---------- 2. server lokal yang bisa SSE / JSON ----------
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):  # senyap
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        mode = body.get("_test_mode", "sse")   # dipakai buat tes, bukan dikirim ke AI
        if mode == "json":
            data = json.dumps({
                "choices": [{"message": {"content": "C) 7"}}]
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        # default: SSE sungguhan (perlahan biar kelihatan beda first-token vs total)
        ctype = "application/json" if mode == "sse_bad_ctype" else "text/event-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        for piece in ["B", ")", " 42"]:
            evt = json.dumps({"choices": [{"delta": {"content": piece}}]})
            self.wfile.write(f"data: {evt}\n\n".encode())
            self.wfile.flush()
            time.sleep(0.05)
        self.wfile.write(b"data: [DONE]\n\n")


srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_address[1]}/chat/completions"
HDR = {"Content-Type": "application/json"}


def call(mode, stream):
    body = {"model": "test", "messages": [{"role": "user", "content": "x"}],
            "_test_mode": mode}
    if stream:
        body["stream"] = True
    return app.SESSION.post(URL, headers=HDR, json=body, timeout=10, stream=stream)


# 2a. streaming sungguhan -> jawaban per potongan + waktu token pertama
pieces = []
t0 = time.perf_counter()
resp = call("sse", True)
answer, first = app._read_answer(resp, True, t0,
                                 on_piece=lambda p: pieces.append((p, time.perf_counter() - t0)))
check("stream: status 200 + content-type event-stream",
      resp.status_code == 200 and "event-stream" in resp.headers.get("Content-Type", ""))
check("stream: jawaban utuh", answer == "B) 42", repr(answer))
check("stream: on_piece dipanggil bertahap (3x)", len(pieces) == 3, len(pieces))
if len(pieces) >= 3:
    check("stream: potongan pertama jauh lebih awal dari total",
          pieces[0][1] < pieces[-1][1],
          f"pertama={pieces[0][1]:.3f}s, terakhir={pieces[-1][1]:.3f}s")
check("stream: first_dt terukur & <= total",
      first is not None and 0 < first <= time.perf_counter() - t0 + 1,
      f"{first:.3f}s" if first else first)

# 2b. server abaikan stream=true, balikin JSON biasa
resp = call("json", True)
answer, first = app._read_answer(resp, True, time.perf_counter(), on_piece=lambda p: None)
check("fallback JSON saat server balas application/json", answer == "C) 7", repr(answer))

# 2c. body SSE tapi content-type salah (application/json)
resp = call("sse_bad_ctype", True)
pieces = []
answer, first = app._read_answer(resp, True, time.perf_counter(),
                                 on_piece=lambda p: pieces.append(p))
check("fallback: parse manual saat content-type salah", answer == "B) 42", repr(answer))

# 2d. mode non-stream (COMMANDCODE_STREAM=0)
resp = call("json", False)
answer, first = app._read_answer(resp, False, time.perf_counter())
check("non-stream: JSON path jalan", answer == "C) 7", repr(answer))

# ---------- 3. warm_up dimatikan tidak nyentuh jaringan ----------
app.WARMUP = False
check("warm_up(): skip saat WARMUP=0", app.warm_up() is None)

# ---------- 4. payload yang dipakai aplikasi ----------
p = app.QuizApp._build_payload("deepseek/deepseek-v4-flash", "AAAA")
check("_build_payload: streaming on", p.get("stream") is True, p.get("stream"))
check("_build_payload: reasoning dimatikan", p.get("reasoning_effort") == "off",
      p.get("reasoning_effort"))
check("_build_payload: ada batas token", isinstance(p.get("max_tokens"), int)
      and p["max_tokens"] >= 64, p.get("max_tokens"))
check("_build_payload: temperature 0", p.get("temperature") == 0.0, p.get("temperature"))
check("_build_payload: teks user tidak lagi minta penjelasan",
      "brief explanation" not in p["messages"][1]["content"][0]["text"].lower()
      and "no explanation" in p["messages"][1]["content"][0]["text"].lower(),
      p["messages"][1]["content"][0]["text"][:80])


# ---------- 5. _post_chat: 400 karena param -> drop param, retry ----------
class RejectHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        bad = [k for k in ("reasoning_effort", "temperature") if k in body]
        if body.get("model") == "always-fail":
            bad = ["model"]
        if bad:
            data = json.dumps({"error": {"message": f"Unsupported parameter: {bad[0]}"}}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        data = json.dumps({"choices": [{"message": {"content": "D) 9"}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


srv2 = ThreadingHTTPServer(("127.0.0.1", 0), RejectHandler)
threading.Thread(target=srv2.serve_forever, daemon=True).start()
app.BASE_URL = f"http://127.0.0.1:{srv2.server_address[1]}"

payload = {"model": "t", "messages": [{"role": "user", "content": "x"}],
           "reasoning_effort": "off", "temperature": 0, "max_tokens": 128, "stream": False}
try:
    resp = app._post_chat(payload, stream=False, timeout=10)
    ans, _ = app._read_answer(resp, False, time.perf_counter())
    check("_post_chat: 400 -> drop param -> retry sukses",
          resp.status_code == 200 and ans == "D) 9", (resp.status_code, ans))
    check("_post_chat: param nolak udah dibuang",
          "reasoning_effort" not in payload and "temperature" not in payload,
          sorted(k for k in payload if k in ("reasoning_effort", "temperature")))
except Exception as e:  # noqa: BLE001
    check("_post_chat: 400 -> drop param -> retry sukses", False, e)

# kalau TIDAK ada param opsional, 400 harus langsung jadi error (tanpa loop)
payload2 = {"model": "always-fail", "messages": [], "max_tokens": 8}
try:
    app._post_chat(payload2, stream=False, timeout=10)
    check("_post_chat: 400 tanpa param opsional -> raise", False, "tidak raise")
except RuntimeError as e:
    check("_post_chat: 400 tanpa param opsional -> raise", "HTTP 400" in str(e), str(e)[:60])
except Exception as e:  # noqa: BLE001
    check("_post_chat: 400 tanpa param opsional -> raise", False, repr(e))

srv2.shutdown()

srv.shutdown()

# ---------- ringkasan ----------
bad = [r for r in results if not r[1]]
print("\n=== %d/%d lulus ===" % (len(results) - len(bad), len(results)))
sys.exit(1 if bad else 0)
