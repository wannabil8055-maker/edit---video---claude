"""AA LAND promo: cut list -> tightened pieces -> base video + voice -> timeline.json for overlay."""
import os, sys, json, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from env import env, IDS, U
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
FPS, SR = 30, 48000
def q(x): return round(x * FPS) / FPS
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(" ".join(cmd)); print(r.stderr[-2500:]); sys.exit(1)

# ---------------- cut list (source times from word timestamps) ----------------
# key, clip, a, b, zoom, subtitle (baku), extra
SEGS = [
 ("greet",  "C1",  0.70,  4.70, 1.00, "Assalamualaikum, sahabat, adik-adik, kakak dan abang semua."),
 ("tunjuk", "C1",  5.30,  8.55, 1.12, "Hari ini saya nak tunjuk kawasan baharu untuk bina rumah, di kawasan ini."),
 ("lokasi", "C1",  9.05, 14.95, 1.00, "Kalau nak tahu di mana, kawasan ini berdekatan jalan besar Neting."),
 ("pencawang","C1",15.40, 19.70, 1.10, "Untuk lebih jelas, boleh lihat pencawang elektrik di sana."),
 ("arah",   "C7",  6.60, 10.50, 1.12, "Ia dekat Neting. Dari sana, belok ke kiri dan terus masuk."),
 ("lorong", "C6",  1.75,  4.00, 1.00, "Itulah laluan yang akan masuk ke rumah ini."),
 ("lot",    "C2",  5.00, 11.32, 1.00, "Di sini ada lima lot tanah, lima buah rumah."),
 ("luasR",  "C2", 12.05, 16.20, 1.14, "Keluasan rumah 1,500 kaki persegi."),
 ("luasT",  "C3",  2.10,  6.30, 1.00, "Keluasan tanah 5,700 kaki persegi."),
 ("tanya",  "C3",  6.30,  8.40, 1.14, "Jadi, bagi yang berminat nak tahu harganya…"),
 ("harga",  "C4", 14.80, 18.05, 1.00, "Rumah ini kami tawarkan dengan harga RM420,000."),
 ("az",     "C4",  6.15,  7.95, 1.18, "Kami akan uruskan dari A hingga Z."),
 ("pening", "C4", 18.30, 19.98, 1.06, "Anda tidak perlu pening apa-apa lagi."),
 ("jangan", "C4", 22.75, 26.50, 1.20, "Jangan beli selepas rumah siap. Belilah sebelum siap."),
 ("beza",   "C4",  8.30, 12.35, 1.04, "Harganya akan berbeza apabila rumah sudah siap."),
 ("tapak",  "C4", 26.85, 29.55, 1.16, "Nanti selepas kami tambun tapak sedikit demi sedikit, bolehlah datang beli."),
 ("buyer",  "C6", 16.40, 17.98, 1.12, "Sekarang kami sedang mencari pembeli."),
 ("cta",    "C6", 18.10, 21.30, 1.00, "Jadi, sesiapa yang berminat untuk beli rumah di kawasan ini…"),
 ("pm",     "C7", 13.55, 16.08, 1.12, "…boleh PM kami di bawah."),
]
HOOK_VOICE = ("C4", 16.15, 18.05)   # "…dengan harga 420k"
HOOK_LEN, HOOK_VOICE_AT = 3.0, 0.80
LOGO_LEN, END_LEN = 2.5, 4.0

def speech_thr(c):
    d = env(c); return np.percentile(d, 50) - 8

def tighten(c, a, b):
    """snap edges to speech and squeeze internal pauses; returns list of (src_a, src_b)."""
    d = env(c); thr = speech_thr(c); hop = 0.01
    sp = d > thr
    # smooth: fill gaps < 60ms, drop blips < 40ms
    idx = lambda t: int(round(t / hop))
    def is_sp(t): i = idx(t); return bool(sp[max(0, min(len(sp) - 1, i))])
    # start: first speech in [a-0.25, a+0.2]
    s = a
    for t in np.arange(a - 0.10, a + 0.30, hop):
        if all(is_sp(t + k * hop) for k in range(4)): s = t; break
    s = max(0, s - 0.05)
    e = b
    for t in np.arange(b + 0.12, b - 0.30, -hop):
        if all(is_sp(t - k * hop) for k in range(4)): e = t; break
    e = e + 0.08
    # internal pauses
    pieces, cur, t, run_start = [], s, s, None
    while t < e:
        if not is_sp(t):
            if run_start is None: run_start = t
        else:
            if run_start is not None and t - run_start > 0.20:
                pieces.append((cur, run_start + 0.05)); cur = t - 0.05
            run_start = None
        t += hop
    pieces.append((cur, e))
    return [(round(x, 3), round(y, 3)) for x, y in pieces if y - x > 0.12]

# ---------------- build piece list ----------------
timeline, pieces, t = [], [], 0.0
timeline.append({"key": "hook", "t0": 0.0, "t1": HOOK_LEN}); t = HOOK_LEN
timeline.append({"key": "logo", "t0": t, "t1": t + LOGO_LEN}); t += LOGO_LEN
for si, (key, c, a, b, z, sub) in enumerate(SEGS):
    ps = tighten(c, a, b); seg = {"key": key, "clip": c, "t0": t, "sub": sub, "map": []}
    for k, (pa, pb) in enumerate(ps):
        d = q(pb - pa)
        if d < 1 / FPS: continue
        zz = z * (1.0 if k % 2 == 0 else 1.09)
        pieces.append({"clip": c, "a": pa, "d": d, "zoom": zz, "seg": key})
        seg["map"].append([pa, pa + d, t]); t += d
    seg["t1"] = t; timeline.append(seg)
    print(f"{key:9s} {c} src {a:.2f}-{b:.2f} -> {len(ps)} pieces, {seg['t1'] - seg['t0']:.2f}s (raw {b - a:.2f}s)")
timeline.append({"key": "end", "t0": t, "t1": t + END_LEN}); TOTAL = t + END_LEN
print("TOTAL", round(TOTAL, 2))

def src2out(key, st):
    seg = next(s for s in timeline if s["key"] == key)
    for pa, pb, o in seg["map"]:
        if pa - 0.05 <= st <= pb + 0.05: return round(o + max(0, min(st, pb) - pa), 3)
    # in a removed pause: snap to next piece
    for pa, pb, o in seg["map"]:
        if st < pa: return round(o, 3)
    return round(seg["t1"], 3)

# cue points (source word times -> output)
CUES = {
 "hook420": HOOK_VOICE_AT + (16.74 - 16.15),
 "houseLand": src2out("tunjuk", 7.12), "plateHouseIn": src2out("tunjuk", 6.70),
 "jalanBesar": src2out("lokasi", 11.96),
 "towerCut": src2out("pencawang", 17.80), "towerWord": src2out("pencawang", 18.76),
 "kiri": src2out("arah", 8.76),
 "lotPlate": src2out("lot", 6.30), "lot1": src2out("lot", 6.78), "lotLast": src2out("lot", 11.10),
 "r1500": src2out("luasR", 13.48), "t5700": src2out("luasT", 3.32),
 "price": src2out("harga", 16.36), "az": src2out("az", 6.60), "pening": src2out("pening", 18.72),
 "jangan": src2out("jangan", 22.82), "beza": src2out("beza", 9.82), "tapak": src2out("tapak", 27.48),
 "buyer": src2out("buyer", 17.16), "neting": src2out("cta", 21.78) if False else src2out("cta", 20.60), "pm": src2out("pm", 15.30),
}
json.dump({"total": TOTAL, "fps": FPS, "segs": timeline, "cues": CUES}, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
print(json.dumps(CUES))

if "--plan" in sys.argv: sys.exit(0)

# ---------------- render base pieces ----------------
GRADE = "eq=contrast=1.07:saturation=1.22:gamma=0.97,curves=master='0/0 0.25/0.23 0.75/0.78 1/0.96'"
files = []
def silent_black(path, dur):
    n = round(dur * FPS)
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=0x1B5E20:s=1080x1920:r={FPS}", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo",
         "-frames:v", str(n), "-af", f"atrim=end_sample={n * SR // FPS}", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", path])
    return path
def piece(path, c, a, d, zoom, pre=0.0, post=0.0):
    n = round((d + pre + post) * FPS); ns = n * SR // FPS
    w = 2 * round(540 * zoom); h = 2 * round(960 * zoom)
    fc = (f"[0:v]fps={FPS},scale={w}:{h}:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.35,{GRADE},trim=end_frame={max(1, n - round(pre * FPS))},setpts=PTS-STARTPTS,tpad=start_duration={pre}:start_mode=clone:stop_mode=clone:stop_duration=3,trim=end_frame={n},format=yuv420p[v];"
          f"[0:a]aresample={SR},aformat=channel_layouts=stereo,atrim=end_sample={round(d * SR)},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03,"
          f"adelay={int(pre * 1000)}|{int(pre * 1000)},apad=whole_len={ns},atrim=end_sample={ns}[a]")
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(max(0, a)), "-t", f"{d + 1:.3f}", "-i", f"{U}/{IDS[c]}-8640019636340790741.mov",
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", path])
    return path
hc, ha, hb = HOOK_VOICE
files.append(piece(os.path.join(OUT, "p000_hook.mkv"), hc, ha, hb - ha, 1.0, pre=HOOK_VOICE_AT, post=HOOK_LEN - HOOK_VOICE_AT - (hb - ha)))
files.append(silent_black(os.path.join(OUT, "p001_logo.mkv"), LOGO_LEN))
for i, p in enumerate(pieces):
    files.append(piece(os.path.join(OUT, f"p{i + 2:03d}_{p['seg']}.mkv"), p["clip"], p["a"], p["d"], p["zoom"]))
files.append(silent_black(os.path.join(OUT, "p999_end.mkv"), END_LEN))
with open(os.path.join(OUT, "list.txt"), "w") as f:
    for p in files: f.write(f"file '{p}'\n")
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "list.txt"), "-c", "copy", os.path.join(OUT, "base.mkv")])
print("base done")
