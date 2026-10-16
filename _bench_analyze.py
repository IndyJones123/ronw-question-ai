"""Analisa hasil `quiz_live_ocr_app.py --bench` (bench_out.txt)."""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "bench_out.txt"
lines = [l.rstrip("\n") for l in open(path, encoding="utf-8") if l.startswith("capture_")]
print("lines:", len(lines))
hist, low, nm, mode_count = {}, [], [], {}
for l in lines:
    if "NO MATCH" in l:
        nm.append(l)
        continue
    for mode in ("sage", "hoppy"):
        if re.search(rf"\s{mode}\s", l):
            mode_count[mode] = mode_count.get(mode, 0) + 1
    m = re.search(r"\s(\d+)%\s", l)
    if m:
        s = int(m.group(1))
        hist[s // 10 * 10] = hist.get(s // 10 * 10, 0) + 1
        if s < 95:
            low.append(l)
print("mode count:", mode_count)
print("hist (bucket->n):", dict(sorted(hist.items())))
print("--- score <95% ---")
for l in low:
    print(l)
print("--- NO MATCH ---")
for l in nm:
    print(l)
