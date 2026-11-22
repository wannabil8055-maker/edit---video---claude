"""Music (construction trap) + SFX on cues + ducked mix under cleaned voice."""
import os, json, wave, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
SR = 48000
TL = json.load(open(os.path.join(OUT, "timeline.json"))); C = TL["cues"]; SEG = {s["key"]: s for s in TL["segs"]}
TOTAL = TL["total"]; N = int(TOTAL * SR) + SR
rng = np.random.default_rng(3)
T = lambda d: np.arange(int(d * SR)) / SR
def env(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if lo: X *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X, len(x))

# ---------- instruments ----------
def kick(a=1.0):
    t = T(0.45); f = 45 + 120 * np.exp(-t / 0.035); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.16)
    return a * np.tanh(2.2 * s) * 0.8
def clap(a=0.6):
    n = int(0.25 * SR); x = rng.standard_normal(n); e = np.zeros(n)
    for o in (0, 0.011, 0.022): i = int(o * SR); e[i:] += env(n - i, 0.018 if o < 0.02 else 0.09)
    return a * fft_filter(x * e, 900, 6000) * 0.9
def hat(a=0.22, d=0.035):
    n = int(0.08 * SR); return a * fft_filter(rng.standard_normal(n), 7000) * env(n, d)
def bass808(freq, dur, a=0.7):
    t = T(dur); f = freq * (1 + 0.6 * np.exp(-t / 0.03)); s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    e = np.minimum(1, t / 0.005) * np.exp(-t / (dur * 0.8)); return a * np.tanh(1.8 * s * e)
def pluck(freq, a=0.18):
    t = T(0.5); s = sum(np.sin(2 * np.pi * freq * k * t) / k for k in (1, 2, 3)) * env(len(t), 0.12); return a * s
def anvil(a=0.35):
    t = T(0.9); s = sum(np.sin(2 * np.pi * f * t) * env(len(t), d) for f, d in ((1150, .25), (1780, .18), (2650, .12), (3920, .08)))
    return a * s / 2 + 0.2 * a * fft_filter(rng.standard_normal(len(t)), 3000) * env(len(t), 0.01)
def boom(a=1.0, d=1.6):
    t = T(d); f = 30 + 70 * np.exp(-t / 0.2); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), d / 3)
    nz = fft_filter(rng.standard_normal(len(t)), None, 900) * env(len(t), 0.25) * 0.6
    return a * np.tanh(1.6 * (s + nz)) * np.minimum(1, t / 0.003)
def whoosh(d=0.6, a=0.5, up=True):
    t = T(d); x = rng.standard_normal(len(t)); e = np.sin(np.pi * t / d) ** 2
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= np.exp(-((f - 1800) / 1500) ** 2); y = np.fft.irfft(X, len(x))
    return a * y / (np.abs(y).max() + 1e-9) * e
def riser(d=0.75, a=0.5):
    t = T(d); f = 200 * (6 ** (t / d)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    nz = fft_filter(rng.standard_normal(len(t)), 2000) * 0.5
    return a * (s + nz) * (t / d) ** 2
def debris(a=0.35):
    n = int(1.0 * SR); y = np.zeros(n)
    for _ in range(40): i = int(rng.uniform(0, 0.7) * SR); m = int(0.02 * SR); y[i:i + m] += rng.standard_normal(m) * env(m, 0.004) * rng.uniform(.3, 1)
    return a * fft_filter(y, 1500)
def ding(f=1760, a=0.3):
    t = T(0.8); return a * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.01 * t)) * env(len(t), 0.25)
def pop(a=0.35):
    t = T(0.12); f = 900 - 500 * t / 0.12; return a * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.03)
def chaching(a=0.45):
    y = np.zeros(int(0.9 * SR)); c = ding(2600, 0.25); y[:len(c)] += c; c2 = ding(3300, 0.3); i = int(0.12 * SR); y[i:i + len(c2)] += c2[:len(y) - i]
    m = anvil(0.2)[:len(y)]; y[:len(m)] += m; return a * y
def zap(a=0.3):
    t = T(0.5); s = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.4 + rng.standard_normal(len(t)) * 0.3
    return a * fft_filter(s, 300, 4000) * env(len(t), 0.12)
def glitch(a=0.35):
    y = np.zeros(int(0.35 * SR))
    for k in range(6): i = int(k * 0.05 * SR); m = int(0.03 * SR); y[i:i + m] += np.sign(np.sin(2 * np.pi * rng.uniform(200, 1200) * T(0.03))) * 0.5
    return a * y
def alert(a=0.3):
    t = T(0.5); return a * np.sign(np.sin(2 * np.pi * 880 * t)) * 0.3 * ((t * 8).astype(int) % 2) * env(len(t), 0.3)
def thud(a=0.5):
    t = T(0.3); return a * np.sin(2 * np.pi * np.cumsum(60 + 60 * np.exp(-t / 0.02)) / SR) * env(len(t), 0.06)
def drill(d=0.4, a=0.18):
    t = T(d); s = np.sign(np.sin(2 * np.pi * 95 * t)) + 0.5 * np.sign(np.sin(2 * np.pi * 190 * t)); return a * fft_filter(s, 150, 3000) * np.sin(np.pi * t / d)

def place(buf, sig, at, g=1.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    m = min(len(sig), len(buf) - i)
    if m > 0: buf[i:i + m] += g * sig[:m]

# ---------- music ----------
BPM = 140; BEAT = 60 / BPM; BAR = 4 * BEAT
mus = np.zeros(N)
notes = [41.2, 41.2, 49.0, 36.7]          # E1 E1 G1 D1 (bar roots)
arp = [329.6, 392.0, 493.9, 587.3, 493.9, 392.0, 329.6, 293.7]
start = 0.75                               # drop on the house impact
dropout = (C["price"] - 0.15, C["price"] - 0.15 + BAR * 0.5)
t = start; bar = 0
while t < TOTAL - 0.1:
    root = notes[bar % 4]
    for b in range(16):                    # 16th grid
        tt = t + b * BEAT / 4
        if dropout[0] <= tt < dropout[1] or tt >= TOTAL: continue
        if b in (0, 6, 10) or (bar % 2 == 1 and b == 14): place(mus, kick(), tt)
        if b in (4, 12): place(mus, clap(), tt)
        if b % 2 == 0 or (bar % 4 == 3 and b >= 12): place(mus, hat(0.2 if b % 4 == 0 else 0.13), tt)
        if b in (0, 6, 10): place(mus, bass808(root, BEAT * (1.5 if b == 0 else 1.0)), tt)
        if b % 2 == 0: place(mus, pluck(arp[(b // 2 + bar) % 8]), tt, 0.8)
    if bar % 2 == 1: place(mus, anvil(0.25), t + 3 * BEAT)
    t += BAR; bar += 1
place(mus, boom(0.9), dropout[1])          # re-entry hit after the price
# music gain automation: louder when no voice (logo, end card)
gain = np.full(N, 0.32)
def gseg(a, b, g):
    i0, i1 = int(a * SR), int(b * SR); gain[i0:i1] = g
gseg(SEG["logo"]["t0"], SEG["logo"]["t1"], 0.85); gseg(SEG["end"]["t0"], TOTAL + 1, 0.8)
gain = np.convolve(gain, np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
mus *= gain

# ---------- SFX ----------
sfx = np.zeros(N)
place(sfx, riser(0.75, 0.45), 0.0); place(sfx, whoosh(0.45, 0.5), 0.3)
place(sfx, boom(1.0), 0.75); place(sfx, debris(0.4), 0.76); place(sfx, anvil(0.45), C["hook420"] - 0.02)
L0 = SEG["logo"]["t0"]
place(sfx, anvil(0.35), L0 + 0.05); place(sfx, anvil(0.3), L0 + 0.3); place(sfx, drill(0.4), L0 + 0.32)
place(sfx, whoosh(0.4, 0.4), L0 + 0.55); place(sfx, boom(1.0), L0 + 0.95); place(sfx, anvil(0.4), L0 + 0.97)
place(sfx, ding(2400, 0.2), L0 + 1.5); place(sfx, whoosh(0.35, 0.45), SEG["logo"]["t1"] - 0.2)
place(sfx, whoosh(0.4, 0.3), SEG["greet"]["t0"] + 0.3)
place(sfx, whoosh(0.4, 0.45), C["plateHouseIn"]); place(sfx, boom(0.95), C["houseLand"]); place(sfx, debris(0.35), C["houseLand"])
place(sfx, pop(0.35), C["jalanBesar"] - 0.1)
place(sfx, whoosh(0.4, 0.4), C["towerCut"] - 0.1); place(sfx, zap(0.3), C["towerCut"] + 0.15); place(sfx, pop(0.3), C["towerCut"] + 0.1)
place(sfx, whoosh(0.4, 0.4), C["kiri"] - 0.1); place(sfx, pop(0.3), C["kiri"])
place(sfx, whoosh(0.5, 0.4), SEG["lorong"]["t0"] - 0.1); place(sfx, riser(0.9, 0.18), SEG["lorong"]["t0"] + 0.1)
place(sfx, whoosh(0.4, 0.4), C["lotPlate"] - 0.1)
t1 = C["lot1"]; t5 = min(C["lotLast"] - 0.5, SEG["lot"]["t1"] - 0.9)
for i in range(5): tl = t1 + (t5 - t1) * i / 4 + 0.05; place(sfx, boom(0.35 + 0.1 * i, 0.8), tl); place(sfx, debris(0.15), tl)
for k in ("r1500", "t5700"): place(sfx, pop(0.35), C[k] - 0.15); place(sfx, ding(1760, 0.22), C[k] - 0.05)
place(sfx, whoosh(0.4, 0.35), SEG["tanya"]["t0"] + 0.15)
place(sfx, chaching(0.5), C["price"]); place(sfx, boom(0.6), C["price"] - 0.1)
for k in range(10): place(sfx, pop(0.12), C["price"] + k * 0.07)
place(sfx, ding(2093, 0.25), C["az"] - 0.1); place(sfx, ding(2349, 0.25), C["pening"] - 0.1)
place(sfx, glitch(0.35), C["jangan"] - 0.05); place(sfx, boom(0.5, 0.8), C["jangan"] - 0.05)
place(sfx, alert(0.25), C["beza"] - 0.3)
for i in range(3): place(sfx, thud(0.5), C["tapak"] - 0.2 + i * 0.35)
place(sfx, boom(0.7), SEG["buyer"]["t0"] + 0.05); place(sfx, anvil(0.3), SEG["buyer"]["t0"] + 0.05)
place(sfx, pop(0.3), SEG["cta"]["t0"] + 0.5); place(sfx, pop(0.3), C["pm"] - 0.4)
E0 = SEG["end"]["t0"]
place(sfx, whoosh(0.4, 0.45), E0 - 0.15); place(sfx, boom(1.0, 2.0), E0 + 0.35); place(sfx, debris(0.35), E0 + 0.36)
place(sfx, ding(2637, 0.25), E0 + 0.9); place(sfx, pop(0.3), E0 + 1.1); place(sfx, pop(0.3), E0 + 1.25)

# ---------- voice clean + ducked mix ----------
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(OUT, "base.mkv"), "-vn", "-af",
                "highpass=f=90,afftdn=nf=-28:nr=14,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,"
                f"aresample={SR}", "-ac", "1", os.path.join(OUT, "voice_clean.wav")], check=True)
w = wave.open(os.path.join(OUT, "voice_clean.wav")); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
voice = np.zeros(N); voice[:len(v)] = v[:N]
h = int(0.02 * SR); e = np.sqrt(np.convolve(voice ** 2, np.ones(h) / h, mode="same"))
act = np.clip((20 * np.log10(e + 1e-9) + 42) / 10, 0, 1)
act = np.convolve(act, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - 0.55 * np.clip(act * 1.5, 0, 1)
mix = voice * 1.0 + mus * duck * 0.55 + sfx * 0.6
mix[int(TOTAL * SR):] = 0
fo = int(0.4 * SR); i1 = int(TOTAL * SR); mix[i1 - fo:i1] *= np.linspace(1, 0, fo)
mix /= max(1.0, np.abs(mix).max() / 0.95)
st = np.stack([mix, mix], 1)
with wave.open(os.path.join(OUT, "mix.wav"), "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((st * 32767).astype(np.int16).tobytes())
print("mix written", TOTAL)
