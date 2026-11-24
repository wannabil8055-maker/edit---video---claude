"""Upbeat 120 bpm track for the AA Land brand video (hf_brand), cut to its scene timings.

Usage: python3 music_brand.py [out.wav]   (default: hf_brand/assets/music_brand.wav)

Timeline: hook 0-2.5 (snare roll), logo reveal 2.5 (impact), steps 5 / 7.25 / 9.5 / 11.75,
project 14 (finished houses land at 16), why-us 19-23 (ticks 19.4 / 20.4 / 21.4), CTA 23-27.
"""
import os
import sys
import wave

import numpy as np

SR = 44100
DUR = 27.0
N = int(SR * DUR)
DROP = 2.5                         # logo lands
BEAT = 0.5                         # 120 bpm
PHASE = DROP % BEAT                # every beat sits on this grid
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def add(t0, sig, g=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    i1 = min(N, i0 + len(sig))
    s = sig[: i1 - i0] * g
    L[i0:i1] += s * (1 - max(0, pan))
    R[i0:i1] += s * (1 + min(0, pan))


def env(n, a=0.003, d=8.0):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t * d)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    body = np.sin(2 * np.pi * (50 * t + 140 * (1 - np.exp(-t * 40)) / 40)) * np.exp(-t * 7)
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.4
    return np.tanh((body + click) * 1.6)


def clap():
    t = np.arange(int(0.22 * SR)) / SR
    nz = rng.standard_normal(len(t))
    nz -= np.convolve(nz, np.ones(5) / 5, mode="same")
    e = np.exp(-t * 25) + sum(0.7 * np.exp(-((t - d) * 500) ** 2) for d in (0.0, 0.011, 0.022))
    return nz * e


def hat(open_=False):
    t = np.arange(int((0.18 if open_ else 0.05) * SR)) / SR
    nz = rng.standard_normal(len(t))
    nz = nz - np.convolve(nz, np.ones(2) / 2, mode="same")
    return nz * np.exp(-t * (18 if open_ else 90))


def saw(f, dur, harm_max=4000, detune=(0.0,), decay=6.0, a=0.004):
    """Band-limited saw by additive harmonics (the cap doubles as a low-pass)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for dt in detune:
        ff = f * (1 + dt)
        k = 1
        while k * ff < harm_max and k < 40:
            out += np.sin(2 * np.pi * k * ff * t) / k
            k += 1
    return out / len(detune) * env(n, a, decay)


def square(f, dur, decay=3.0, vib=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + vib * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.15)
    out = sum(np.sin(k * ph) / k for k in (1, 3, 5, 7, 9))
    return out * env(n, 0.005, decay)


def drum_tone(f, dur=0.18, drop=0.5):
    """Short pitched hand drum (gendang-ish)."""
    t = np.arange(int(dur * SR)) / SR
    fr = f * (1 + drop * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 22)


def riser(dur):
    t = np.arange(int(dur * SR)) / SR
    nz = np.convolve(rng.standard_normal(len(t)), np.ones(6) / 6, mode="same")
    sweep = np.sin(2 * np.pi * (300 * t + 900 * t ** 2 / dur))
    return (nz * 0.7 + sweep * 0.35) * (t / dur) ** 2


def impact():
    t = np.arange(int(1.8 * SR)) / SR
    sub = np.sin(2 * np.pi * (34 * t + 90 * (1 - np.exp(-t * 5)) / 5)) * np.exp(-t * 2.0)
    nz = np.convolve(rng.standard_normal(len(t)) * np.exp(-t * 5), np.ones(4) / 4, mode="same")
    return np.tanh(sub * 1.4 + nz * 0.35)


def whoosh(dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    return np.convolve(rng.standard_normal(len(t)), np.ones(14) / 14, mode="same") * np.sin(np.pi * t / dur) ** 2


def chime(f):
    t = np.arange(int(1.0 * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 4)


# A minor: Am - F - C - G, one chord per bar (2 s)
CHORDS = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 196.0, 261.63), (196.0, 246.94, 293.66)]
ROOTS = [110.0, 87.31, 130.81, 98.0]
# catchy lead, one bar per chord, 8 eighth-note slots (0 = rest), A minor pentatonic
LEAD = [
    [880.0, 0, 783.99, 880.0, 0, 659.25, 783.99, 0],
    [698.46, 0, 659.25, 587.33, 0, 523.25, 587.33, 0],
    [659.25, 0, 783.99, 659.25, 0, 523.25, 587.33, 659.25],
    [587.33, 0, 493.88, 587.33, 0, 783.99, 783.99, 0],
]


def bar_index(t):
    return int(np.floor((t - DROP) / (BEAT * 4)))


beats = [PHASE + k * BEAT for k in range(int(DUR / BEAT) + 1)]

# sections: (start, end, level) — 0 off, 1 light, 2 groove, 3 full
SECT = [(0.0, 0.5, 1), (0.5, 2.5, 0), (2.5, 5.0, 2), (5.0, 19.0, 3), (19.0, 23.0, 2), (23.0, 26.5, 3)]


def level(t):
    for a, b, lv in SECT:
        if a <= t < b:
            return lv
    return 0


# --- drums
for i, bt in enumerate(beats):
    lv = level(bt)
    if bt > DUR - 0.6:
        break
    if lv >= 1:
        add(bt, kick(), 0.75)
    if lv >= 2 or (lv == 1 and i % 2 == 1):
        if i % 2 == 1:
            add(bt, clap(), 0.32, pan=0.1)
    if lv >= 2:
        add(bt + BEAT / 2, hat(True), 0.13, pan=-0.3)          # off-beat open hat
        for s in (0.25, 0.75):
            add(bt + BEAT * s, hat(), 0.07, pan=0.35)
    if lv >= 3:
        add(bt, hat(), 0.06, pan=0.35)
        # gendang pattern for a local, lively feel
        pat = [(0.0, 330, -0.4), (0.5, 220, 0.4), (0.75, 330, -0.4)]
        if i % 2 == 1:
            pat = [(0.25, 330, -0.4), (0.5, 440, 0.4)]
        for off, f, p in pat:
            add(bt + BEAT * off, drum_tone(f), 0.13, pan=p)

# --- bass (off-beat house bass) and chord stabs
for i, bt in enumerate(beats):
    lv = level(bt)
    if lv < 2 or bt > DUR - 0.8:
        continue
    b = bar_index(bt + 0.01) % 4
    root = ROOTS[b]
    add(bt + BEAT / 2, saw(root, 0.22, 900, (0, 0.004), decay=10), 0.30)
    add(bt, saw(root / 2, 0.12, 400, decay=18), 0.25)
    # syncopated stabs: on the "and" of beats 2 and 4 of each bar, plus beat 1 when full
    pos = int(round((bt - DROP) / BEAT)) % 4
    if pos in (1, 3) or (lv >= 3 and pos == 0):
        st = bt + (BEAT / 2 if pos in (1, 3) else 0)
        for f in CHORDS[b]:
            add(st, saw(f * 2, 0.2, 5000, (-0.006, 0, 0.006), decay=9), 0.055, pan=0.0)

# --- light pad under the hook and build so it never feels empty
for i, bt in enumerate(beats):
    pos = int(round((bt - DROP) / BEAT)) % 4
    if pos != 0 or not (19.0 <= bt < 23.0):
        continue
    b = bar_index(bt + 0.01) % 4
    n = int(2.0 * SR)
    tt = np.arange(n) / SR
    e = np.minimum(1, tt / 0.3) * np.minimum(1, (2.0 - tt) / 0.3)
    for f in CHORDS[b]:
        add(bt, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt)) * e, 0.035)

# --- lead melody in the full sections
for i, bt in enumerate(beats):
    pos = int(round((bt - DROP) / BEAT)) % 4
    if pos != 0:
        continue
    for a, b_, lv in SECT:
        if lv == 3 and a <= bt < b_:
            break
    else:
        continue
    bar = bar_index(bt + 0.01) % 4
    for k, f in enumerate(LEAD[bar]):
        t0 = bt + k * BEAT / 2
        if f and t0 < 26.4:
            add(t0, square(f, 0.26, decay=6, vib=0.02), 0.06, pan=0.15)
            add(t0 + 0.18, square(f, 0.2, decay=9), 0.02, pan=-0.4)   # echo

# --- hits that follow the picture
add(0.0, impact(), 0.9)

# construction thuds while the walls rise
for bt in beats:
    if False:
        t = np.arange(int(0.25 * SR)) / SR
        add(bt, np.sin(2 * np.pi * (70 + 50 * np.exp(-t * 25)) * t) * np.exp(-t * 14), 0.35)
# build-up: riser + snare roll accelerating into the drop
add(DROP - 2.0, riser(2.0), 0.4)
st = DROP - 2.0
while st < DROP - 0.03:
    add(st, clap(), 0.12 + 0.2 * (st - (DROP - 2.0)) / 2.0)
    rem = DROP - st
    st += BEAT / 2 if rem > 1.0 else (BEAT / 4 if rem > 0.5 else BEAT / 8)
add(DROP, impact(), 1.0)
for st in (5.0, 7.25, 9.5, 11.75):          # each step card
    add(st, drum_tone(110, 0.3, 1.0), 0.45)
for ct in (5.0, 7.25, 9.5, 11.75, 14.0, 19.0, 23.0):
    add(ct - 0.25, whoosh(), 0.3)
add(16.0, impact(), 0.75)                   # finished houses land on the site photo     # price struck out
for tk in (19.4, 20.4, 21.4):
    add(tk, chime(1318.5), 0.1)              # rebate
for j, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
    add(23.5 + j * 0.07, chime(f), 0.09)     # final price
add(26.5, impact(), 0.6)            # last hit before the fade

# --- mix: sidechain pump on the kick, glue, normalise
duck = np.ones(N)
for bt in beats:
    if level(bt) >= 2:
        i0 = int(bt * SR)
        seg = 1 - 0.4 * np.exp(-(np.arange(int(0.3 * SR)) / SR) * 10)
        j1 = min(N, i0 + len(seg))
        duck[i0:j1] = np.minimum(duck[i0:j1], seg[: j1 - i0])
t = np.arange(N) / SR
fade = np.minimum(1, t / 0.02) * np.clip((DUR - t) / 0.6, 0, 1)
out = np.stack([L, R], 1) * duck[:, None] * fade[:, None]
out = np.tanh(out * 1.5) / np.tanh(1.5)
out = out / np.abs(out).max() * 0.9

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                          "hf_brand", "assets", "music_brand.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
print("wrote", path, f"{DUR:.2f}s")
