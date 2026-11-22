"""AA LAND Part 2: beat-synced cut list -> base video (+ impacts, ramps, blur band) -> timeline.json."""
import os, sys, json, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
SRC = "/root/.claude/uploads/ffb22ac1-847d-548f-85f3-a6d14c35e14b/a5e4fe0e-7482876689718565249.mov"
FPS, SR = 30, 48000
BEAT, GRID0 = 60 / 140, 0.55
def q(x): return round(x * FPS) / FPS
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(" ".join(cmd)); print(r.stderr[-2500:]); sys.exit(1)

# speech envelope for pause tightening
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-af", "highpass=f=250,lowpass=f=3500", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
X = np.frombuffer(raw, np.int16).astype(float) / 32768
ENV = 20 * np.log10(np.array([np.sqrt(np.mean(X[i:i + 320] ** 2)) for i in range(0, len(X) - 320, 160)]) + 1e-9)
THR = np.percentile(ENV[:int(27 * 100)], 50) - 8
def tighten(a, b):
    sp = lambda t: ENV[max(0, min(len(ENV) - 1, int(t * 100)))] > THR
    pieces, cur, rs, t = [], a, None, a
    while t < b:
        if not sp(t): rs = t if rs is None else rs
        else:
            if rs is not None and t - rs > 0.22: pieces.append((cur, rs + 0.05)); cur = t - 0.05
            rs = None
        t += 0.01
    pieces.append((cur, b)); return [(x, y) for x, y in pieces if y - x > 0.15]

# ---------------- plan ----------------
# piece: kind, src a, out dur, speed, z0, z1, impact, label, extra
P = []; T = [0.0]
def add(kind, a, d, speed=1.0, z0=1.0, z1=1.06, impact=False, seg=None, **kw):
    d = q(d); P.append(dict(kind=kind, a=a, d=d, speed=speed, z0=z0, z1=z1, impact=impact, seg=seg, t0=T[0], **kw)); T[0] += d
beat_at = lambda k: GRID0 + k * BEAT
# HOOK: 4 cuts on the beat grid
add("broll", 52.0, GRID0, speed=1.6, z0=1.10, z1=1.25, seg="hook", label="")
add("broll", 28.0, beat_at(2) - beat_at(0), z0=1.25, z1=1.10, impact=True, seg="hook")
add("broll", 33.5, beat_at(3) - beat_at(2), speed=1.3, z0=1.15, z1=1.25, impact=True, seg="hook")
add("broll", 41.0, 3.2 - beat_at(3), z0=1.05, z1=1.18, impact=True, seg="hook")
HOOK_VO = (25.70, 26.95, beat_at(3) + 0.05)       # "beres, kasi luncur" placed in the mix
add("card", 0, 2.5, seg="logo")
add("recap", 0.2, 2.2, z0=1.1, z1=1.18, seg="recap")
VO = [("v1", 1.25, 4.30, "Assalamualaikum. Hari ini kita sudah mula proses menambun."),
      ("v2", 4.85, 8.30, "Kita buat jalan untuk masuk sampai ke hujung sana."),
      ("v3", 8.80, 10.55, "Seperti yang kita lihat, inilah jalannya."),
      ("v4", 10.70, 13.75, "Kemudian di situ jalan utama, kereta lalu-lalang."),
      ("v5", 17.95, 19.65, "Jadi, tidak jauh."),
      ("v6", 21.35, 24.25, "Nanti kita tunjukkan footage kerja di tapak.")]
SUBS = {}
for key, a, b, sub in VO:
    t0 = T[0]
    for k, (pa, pb) in enumerate(tighten(a, b)):
        add("voice", pa, pb - pa, z0=1.0 if k % 2 == 0 else 1.1, z1=1.05 if k % 2 == 0 else 1.14, seg=key, src_b=pb)
    SUBS[key] = (t0, T[0], sub)
# LAND DETAIL (music only), starts on a beat
def snap():
    k = int(np.ceil((T[0] - GRID0) / BEAT - 1e-6)); pad = beat_at(k) - T[0]
    if pad > 0.02: P[-1]["d"] = q(P[-1]["d"] + pad); T[0] = P[-1]["t0"] + P[-1]["d"]
snap(); land0 = T[0]
add("broll", 14.4, 8 * BEAT, z0=1.0, z1=1.12, seg="tanah")
add("broll", 16.8, 6 * BEAT, z0=1.12, z1=1.02, seg="tanah")
land1 = T[0]
# MONTAGE (beat-synced; 2 beats per shot unless noted)
M = [(44.0, 2, 1.3, "LORI TANAH MERAH MASUK", False), (45.6, 2, 1.0, "", False), (48.5, 2, 1.2, "", False),
     (53.0, 3, 0.7, "PROSES TAMBUN", True), (29.4, 2, 1.0, "", False), (31.0, 2, 1.0, "TRAKTOR RATAKAN TANAH", False),
     (35.0, 2, 1.4, "", False), (39.2, 2, 1.0, "", False), (41.6, 2, 1.0, "MAMPATKAN JALAN", False)]
mont0 = T[0]
for i, (a, nb, sp, lab, slow) in enumerate(M):
    add("broll", a, nb * BEAT, speed=sp, z0=1.18, z1=1.04, impact=True, seg="montage", label=lab, slow=slow)
add("split", 59.0, 6 * BEAT, seg="split", before=21.0)
add("broll", 57.4, 6 * BEAT, z0=1.0, z1=1.14, impact=True, seg="siap", label="JALAN MASUK HAMPIR SIAP")
add("card", 0, 4.0, seg="end")
TOTAL = T[0]
segs = {}
for p in P: s = segs.setdefault(p["seg"], {"key": p["seg"], "t0": p["t0"], "t1": p["t0"] + p["d"]}); s["t1"] = p["t0"] + p["d"]
for k, (a, b, sub) in SUBS.items(): segs[k]["sub"] = sub
timeline = {"total": TOTAL, "beat": BEAT, "grid0": GRID0, "segs": list(segs.values()),
            "pieces": [{k: p[k] for k in ("seg", "t0", "d", "speed", "impact")} | {"label": p.get("label", ""), "slow": p.get("slow", False)} for p in P],
            "hookVO": HOOK_VO[2]}
json.dump(timeline, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
for s in segs.values(): print(f"{s['key']:8s} {s['t0']:6.2f}-{s['t1']:6.2f}")
print("TOTAL", round(TOTAL, 2), "pieces", len(P))
if "--plan" in sys.argv: sys.exit(0)

# ---------------- render ----------------
GRADE = "eq=contrast=1.12:saturation=1.28:gamma=0.96,colorbalance=rs=0.04:bs=-0.04:rh=0.03:bh=0.05,curves=master='0/0 0.25/0.22 0.75/0.80 1/0.97'"
BAND = "split[m][b];[b]crop=1080:420:0:1280,boxblur=22:3,eq=brightness=-0.08[bb];[m][bb]overlay=0:1280"
def render(i, p):
    out = os.path.join(OUT, f"p{i:03d}.mkv"); n = round(p["d"] * FPS); ns = n * SR // FPS
    if p["kind"] == "card":
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=0x1B5E20:s=1080x1920:r={FPS}", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo",
             "-frames:v", str(n), "-af", f"atrim=end_sample={ns}", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", out]); return out
    sp = p["speed"]; d = p["d"]; zs = f"({p['z0']}+({p['z1'] - p['z0']})*t/{d}" + (f"+0.14*exp(-t*12)" if p["impact"] else "") + ")"
    shake = f"+sin(t*95)*26*exp(-t*9)" if p["impact"] else ""
    vf = [f"setpts=(PTS-STARTPTS)/{sp}"]
    if p.get("slow"): vf.append("minterpolate=fps=60:mi_mode=blend,fps=30")
    vf += [f"fps={FPS}", "scale=1080:1920:flags=lanczos", "unsharp=5:5:0.9"]
    blur = p["a"] < 27.3
    chain = ",".join(vf)
    fc = f"[0:v]{chain}" + (f",{BAND}" if blur else "") + f",{GRADE}"
    if p["kind"] == "recap": fc += ",boxblur=18:2,eq=brightness=-0.18"
    fc += (f",scale=w='2*trunc(540*{zs})':h='2*trunc(960*{zs})':eval=frame:flags=lanczos,crop=1080:1920:x='(iw-1080)/2{shake}':y='(ih-1920)/2{shake.replace('95', '83')}'")
    if p["impact"]: fc += ",rgbashift=rh=10:bh=-10:gv=4:enable='lt(t,0.1)'"
    fc += f",trim=end_frame={n},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=2,trim=end_frame={n},format=yuv420p[v]"
    if p["kind"] == "split":
        n2 = n
        fc = (f"[0:v]setpts=PTS-STARTPTS,fps={FPS},scale=1080:1920:flags=lanczos,{BAND},{GRADE},crop=1080:960:0:640,trim=end_frame={n2},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=2[top];"
              f"[1:v]setpts=PTS-STARTPTS,fps={FPS},scale=1080:1920:flags=lanczos,{GRADE},crop=1080:960:0:640,trim=end_frame={n2},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=2[bot];"
              f"[top][bot]vstack,trim=end_frame={n},format=yuv420p[v]")
    vol = 1.0 if p["kind"] == "voice" else 0.22
    at = "" if abs(sp - 1) < 1e-3 else f",atempo={sp}"
    ain = 1 if p["kind"] == "split" else 0
    fc += (f";[{ain}:a]aresample={SR},aformat=channel_layouts=stereo{at},volume={vol},atrim=end_sample={round(d * SR)},asetpts=PTS-STARTPTS,"
           f"afade=t=in:d=0.02,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03,apad=whole_len={ns},atrim=end_sample={ns}[a]")
    inp = ["-ss", str(p["a"]), "-t", f"{d * sp + 1:.3f}", "-i", SRC]
    if p["kind"] == "split": inp = ["-ss", str(p["before"]), "-t", f"{d + 1:.3f}", "-i", SRC] + inp
    run(["ffmpeg", "-y", "-v", "error", *inp, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", out])
    return out
files = [render(i, p) for i, p in enumerate(P)]
with open(os.path.join(OUT, "list.txt"), "w") as f:
    for x in files: f.write(f"file '{x}'\n")
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "list.txt"), "-c", "copy", os.path.join(OUT, "base.mkv")])
# hook voice insert as separate wav
a, b, at = HOOK_VO
run(["ffmpeg", "-y", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", SRC, "-af", f"aresample={SR},afade=t=in:d=0.02,afade=t=out:st={b - a - 0.04}:d=0.04", "-ac", "1", os.path.join(OUT, "hookvo.wav")])
print("base done")
