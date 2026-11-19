"""Synthesised soundtrack (BGM + SFX + cartoon crowd laughter) for 'Satu Masjid Gelak'.
Writes music_sfx.wav (stereo 44.1k, 55s). Voice-over slots are left with ducked music.
Usage: python3 audio.py out.wav
"""
import sys, wave
import numpy as np

SR = 44100
DUR = 55.0
N = int(SR * DUR)
rng = np.random.default_rng(1)
mus = np.zeros((N, 2))   # music bus
sfx = np.zeros((N, 2))   # sfx bus

def T(n): return np.arange(n) / SR
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(bus, start, sig, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N: return
    if sig.ndim == 1:
        l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
        sig = np.stack([sig * l, sig * r], 1) * np.sqrt(2)
    j = min(N, i + len(sig))
    bus[i:j] += sig[: j - i] * gain

def env(n, a=0.005, d=None, rel=0.05):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if d: e *= np.exp(-T(n) / d)
    nr = max(1, int(rel * SR)); e[-nr:] *= np.linspace(1, 0, nr)
    return e

def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip((f - lo) / (lo * .3 + 1), 0, 1) * np.clip((hi - f) / (hi * .3 + 1), 0, 1)
    return np.fft.irfft(X * m, len(x))

def noise(n): return rng.standard_normal(n)

# ---------------- instruments ----------------
def pluck(f, dur=0.9):
    n = int(dur * SR); t = T(n); s = np.zeros(n)
    for k in range(1, 9):
        s += (0.9 ** k) / k * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + k * 2.2))
    return s * env(n, .002, None, .05)

def piano(f, dur=2.5, vel=1.0):
    n = int(dur * SR); t = T(n); s = np.zeros(n)
    for k, a in enumerate([1, .55, .3, .18, .1, .06, .04], 1):
        s += a * np.sin(2 * np.pi * f * k * 1.0008 ** k * t) * np.exp(-t * (1.1 + k * .7))
    s += .15 * np.sin(2 * np.pi * f * t) * np.exp(-t * 18)   # hammer
    return s * env(n, .004, None, .2) * vel

def pad(freqs, dur, att=1.2, rel=1.5, bright=4):
    n = int(dur * SR); t = T(n); s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.13):
            for k in range(1, bright + 1):
                s += np.sin(2 * np.pi * (f * k + det * k) * t + rng.random() * 6) / (k * k)
    e = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel).clip(0, 1)
    return s * e / (len(freqs) * 3)

def strings(freqs, dur, att=1.6):
    n = int(dur * SR); t = T(n); s = np.zeros(n)
    vib = 1 + .004 * np.sin(2 * np.pi * 5.2 * t)
    for f in freqs:
        for det in (-0.6, 0.4, 1.1):
            ph = 2 * np.pi * np.cumsum((f + det) * vib) / SR
            for k in range(1, 10):
                s += np.sin(k * ph) / k * (0.85 ** k)
    e = np.minimum(1, t / att) * np.clip((dur - t) / 1.2, 0, 1)
    return s * e / (len(freqs) * 6)

def kick():
    n = int(.35 * SR); t = T(n); f = 45 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def snap(): n = int(.12 * SR); return bandpass(noise(n), 1800, 7000) * np.exp(-T(n) * 45)
def hat(): n = int(.06 * SR); return bandpass(noise(n), 6000, 15000) * np.exp(-T(n) * 70)
def snare(): n = int(.25 * SR); t = T(n); return (bandpass(noise(n), 900, 6000) * .7 + np.sin(2 * np.pi * 190 * t) * .4) * np.exp(-t * 18)

# ---------------- SFX ----------------
def tick(): n = int(.04 * SR); return np.sin(2 * np.pi * 2400 * T(n)) * np.exp(-T(n) * 160) + bandpass(noise(n), 3000, 9000) * np.exp(-T(n) * 200) * .5

def riser(d):
    n = int(d * SR); t = T(n); f = 200 * (8 ** (t / d))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .4 + bandpass(noise(n), 800, 9000) * .5 * (t / d)
    return s * (t / d) ** 2

def impact():
    n = int(1.6 * SR); t = T(n); f = 30 + 80 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5)
    s += bandpass(noise(n), 40, 900) * np.exp(-t * 12) * .8
    return np.tanh(s * 1.6)

def pfft():
    n = int(.4 * SR); t = T(n)
    s = bandpass(noise(n), 300, 3500) * np.exp(-t * 9) * (1 - np.exp(-t * 300))
    s += np.sin(2 * np.pi * (180 - 120 * t) * t) * np.exp(-t * 14) * .5 * (np.sin(2 * np.pi * 38 * t) > 0)  # lip buzz
    return s

def whoosh(d, lo=300, hi=5000, up=True):
    n = int(d * SR); t = T(n); x = noise(n); out = np.zeros(n)
    bands = 6
    for b in range(bands):
        f0 = lo * (hi / lo) ** (b / bands); f1 = lo * (hi / lo) ** ((b + 1) / bands)
        w = np.exp(-((t / d - (b + .5) / bands) if up else (1 - t / d - (b + .5) / bands)) ** 2 / .05)
        out += bandpass(x, f0, f1) * w
    return out * np.sin(np.pi * t / d) ** 1.5

def popfx(f0=600):
    n = int(.12 * SR); t = T(n); f = f0 + 900 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)

def chime(f=1318.5, d=2.5):
    n = int(d * SR); t = T(n); s = np.zeros(n)
    for r, a in [(1, 1), (2.76, .5), (5.4, .25), (8.9, .12)]:
        s += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * (1.5 + r * .8))
    return s * env(n, .002, None, .1)

def ding(): return chime(1760, 1.2) * .8

def flutter(d):
    n = int(d * SR); t = T(n)
    return bandpass(noise(n), 1500, 6000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 22 * t))) * np.sin(np.pi * t / d)

def swipe(): n = int(.35 * SR); t = T(n); return bandpass(noise(n), 2000, 8000) * np.sin(np.pi * t / .35) * .6

def shimmer(d=1.5):
    s = np.zeros(int(d * SR))
    for i in range(14):
        c = chime(mtof(84 + [0, 2, 4, 7, 9, 12][i % 6]), .8) * .2
        st = int(i * d / 16 * SR); s[st:st + len(c)] += c[: len(s) - st]
    return s

def bass_swell(d=3):
    n = int(d * SR); t = T(n)
    return np.sin(2 * np.pi * 55 * t) * np.sin(np.pi * t / d) ** 2

# ---------------- cartoon laughter ----------------
def formant_amp(f, F):
    return sum(a * np.exp(-((f - fc) / bw) ** 2) for fc, bw, a in F)

VOWELS = {'a': [(800, 140, 1), (1250, 180, .6), (2600, 300, .25)],
          'e': [(500, 120, 1), (1900, 200, .5), (2600, 300, .25)]}

def laugh_voice(f0, dur, rate, vowel='a', seed=0):
    r = np.random.default_rng(seed); n = int(dur * SR); t = T(n)
    f0t = f0 * (1.15 - .3 * t / dur) * (1 + .03 * np.sin(2 * np.pi * rate * t))
    ph = 2 * np.pi * np.cumsum(f0t) / SR
    s = np.zeros(n); F = VOWELS[vowel]
    for k in range(1, int(4000 / f0) + 1):
        s += formant_amp(k * f0, F) * np.sin(k * ph) / np.sqrt(k)
    # "ha ha ha" syllable gate
    syl = (t * rate + r.random()) % 1.0
    gate = np.where(syl < .55, np.clip(np.sin(np.pi * syl / .55), 0, 1) ** .7, 0)
    asp = bandpass(r.standard_normal(n), 1200, 5000) * np.where(syl < .12, 1, 0) * .25
    e = np.clip(t / .05, 0, 1) * np.clip((dur - t) / (dur * .5), 0, 1)
    return (s * gate + asp) * e

def crowd_laugh(dur, voices=10, seed=0):
    r = np.random.default_rng(seed); n = int(dur * SR); out = np.zeros((n, 2))
    for v in range(voices):
        kid = r.random() < .3
        f0 = r.uniform(300, 420) if kid else r.uniform(110, 210)
        d = dur * r.uniform(.55, .95); st = r.uniform(0, dur - d)
        sig = laugh_voice(f0, d, r.uniform(4.2, 6.5), 'a' if r.random() < .7 else 'e', seed * 100 + v)
        sig /= (np.abs(sig).max() + 1e-9)
        pan = r.uniform(-.8, .8); i = int(st * SR)
        out[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2) * r.uniform(.5, 1)
        out[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2) * r.uniform(.5, 1)
    return out / voices * 2.2

# ---------------- MUSIC ----------------
# Section A: playful (3.2 -> 15.2), 100 BPM, C G Am F
bpmA = 100; beatA = 60 / bpmA; barA = beatA * 4
chA = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
t0 = 3.2
for b in range(5):
    ch = chA[b % 4]; bs = t0 + b * barA
    add(mus, bs, pluck(mtof(ch[0] - 24), barA) * .9, .35)
    arp = [ch[0], ch[1], ch[2], ch[1] + 12 if False else ch[0] + 12, ch[2], ch[1], ch[2] + 0, ch[0] + 12]
    for i, m in enumerate(arp):
        add(mus, bs + i * beatA / 2, pluck(mtof(m + 12), .6), .16, pan=(-.3 if i % 2 else .3))
    for k in (1, 3): add(mus, bs + k * beatA, snap(), .12, pan=.2)
    # little melody hook
    mel = [(0, 76, .5), (.5, 74, .5), (1, 72, .5), (2, 74, 1), (3, 76, .5)] if b % 2 == 0 else [(0, 74, .5), (1, 72, .5), (1.5, 71, .5), (2, 72, 1.5)]
    for off, m, ln in mel:
        add(mus, bs + off * beatA, pluck(mtof(m), ln * beatA + .4), .11, pan=-.1)

# Section B: emotional piano (15.2 -> 41.0), 84 BPM, Am F C G
bpmB = 84; beatB = 60 / bpmB; barB = beatB * 4
chB = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
t0 = 15.2; nbB = 9
melB = [[(0, 76), (1, 72), (2, 74), (3, 76)], [(0, 77), (2, 76), (3, 72)], [(0, 72), (1, 74), (2, 76), (3, 79)], [(0, 79), (2, 77), (3, 74)]]
for b in range(nbB):
    ch = chB[b % 4]; bs = t0 + b * barB
    add(mus, bs, piano(mtof(ch[0] - 12), barB + 1, .9), .22)
    add(mus, bs, piano(mtof(ch[0] - 24), barB + 1, .7), .16)
    for i in range(4):
        add(mus, bs + i * beatB, piano(mtof(ch[i % 3] + 12), 1.6, .6), .07, pan=(.25 if i % 2 else -.25))
    if b >= 2:
        for off, m in melB[b % 4]:
            add(mus, bs + off * beatB, piano(mtof(m), 2.0, .8), .1)
    add(mus, bs, pad([mtof(x) for x in ch], barB + .5, .8, .8), .12)
    if bs >= 33.0:   # lo-fi beat joins with the montage
        for k in range(4):
            if k in (0, 2): add(mus, bs + k * beatB, kick(), .28)
            if k in (1, 3): add(mus, bs + k * beatB, snare(), .07, pan=.1)
            add(mus, bs + k * beatB, hat(), .04, pan=.3); add(mus, bs + (k + .5) * beatB, hat(), .025, pan=.3)
endB = t0 + nbB * barB   # ~40.9

# Section C: climax (endB -> ~49.5) strings + piano
t0 = endB; chC = [[53, 57, 60], [55, 59, 62], [57, 60, 64], [60, 64, 67]]
for b in range(3):
    ch = chC[b % 4]; bs = t0 + b * barB
    add(mus, bs, strings([mtof(x) for x in ch] + [mtof(ch[0] - 12)], barB + .8, 1.4 if b == 0 else .6), .2)
    add(mus, bs, piano(mtof(ch[0] - 12), barB + 1), .22)
    for i in range(8):
        add(mus, bs + i * beatB / 2, piano(mtof(ch[i % 3] + 12 + (12 if i % 4 == 3 else 0)), 1.2, .55), .06, pan=(.3 if i % 2 else -.3))
    add(mus, bs, piano(mtof([79, 79, 76][b]), 2.5), .12)
    add(mus, bs + 2 * beatB, piano(mtof([77, 74, 72][b]), 2.5), .11)

# Outro (49.5 -> 55): piano resolve on C, fade
t0 = endB + 3 * barB
for i, m in enumerate([72, 76, 79, 84]):
    add(mus, t0 + i * .35, piano(mtof(m), 4.5, .7), .1, pan=(-.2 + i * .13))
add(mus, t0, piano(mtof(48), 5.5), .22); add(mus, t0, pad([mtof(x) for x in (60, 64, 67)], 5.5, .6, 2.5), .14)
add(mus, t0 + 2.9, piano(mtof(74), 3), .08); add(mus, t0 + 3.3, piano(mtof(72), 3), .09)

# music automation: duck under VO slots, fade-in/out
tt = T(N)
g = np.ones(N)
def ramp(a, b, v0, v1):
    m = (tt >= a) & (tt < b); g[m] = v0 + (v1 - v0) * (tt[m] - a) / (b - a)
g[tt < 3.2] = 0
for a, b in [(4.6, 9.0), (9.0, 12.0), (17.6, 41.0), (42.0, 49.0)]:  # VO slots: leave room for the ustaz's voice
    m = (tt >= a) & (tt < b); g[m] = .62
ramp(4.4, 4.6, 1, .62); ramp(12.0, 12.3, .62, 1); ramp(17.0, 17.6, 1, .62); ramp(41.0, 42.0, .62, .8)
ramp(49.0, 49.6, .62, 1.0); ramp(53.0, 55.0, 1.0, 0)
mus *= g[:, None]

# ---------------- SFX timeline ----------------
for k in range(4): add(sfx, .05 + k * .4, tick(), .25, pan=.1)
add(sfx, .25, riser(1.35), .22)
add(sfx, 1.6, impact(), .85); add(sfx, 1.6, pfft(), .55)
add(sfx, 1.68, crowd_laugh(2.6, 12, 1), .42)
add(sfx, 2.15, whoosh(1.0, 400, 6000), .3)
add(sfx, 2.9, whoosh(1.7, 200, 3000, up=False), .2)
add(sfx, 3.75, whoosh(.45, 800, 6000), .15, pan=-.5)            # nametag slide
add(sfx, 4.8, flutter(1.25), .18, pan=.4)                       # paper plane
add(sfx, 6.05, popfx(500), .35); add(sfx, 6.15, popfx(700), .25)
add(sfx, 6.8, swipe(), .22)                                     # marker
add(sfx, 8.7, whoosh(.4, 600, 5000, up=False), .15)
add(sfx, 12.0, ding(), .3)
add(sfx, 12.05, crowd_laugh(2.8, 14, 2), .4)
for i in range(11): add(sfx, 12.05 + i * .24, popfx(500 + (i * 137) % 600), .14, pan=((i * .37) % 1.6) - .8)
add(sfx, 15.0, chime(1046.5, 3), .22); add(sfx, 15.0, bass_swell(2.5), .25)
add(sfx, 17.0, whoosh(.8, 300, 6000), .25); add(sfx, 17.7, shimmer(1.4), .25)
add(sfx, 17.75, whoosh(.5, 600, 5000), .14, pan=.5)
add(sfx, 18.6, popfx(800), .18); add(sfx, 18.5, popfx(600), .14)
add(sfx, 24.5, whoosh(.6, 600, 5000, up=False), .15, pan=-.4)
add(sfx, 25.0, whoosh(.6, 600, 5000), .15, pan=.5)
add(sfx, 25.6, shimmer(2.2), .22); add(sfx, 25.6, chime(1568, 3), .12)
add(sfx, 30.7, popfx(700), .2)
add(sfx, 32.5, whoosh(.6, 600, 5000, up=False), .15, pan=-.4)
for i in range(3): add(sfx, 34.0 + i * .7, whoosh(.5, 500, 5000), .14, pan=(-.5 if i % 2 == 0 else .5))
for i in range(3): add(sfx, 36.0 + i * 1.0, popfx(900), .22); add(sfx, 36.05 + i * 1.0, chime(2093, .6), .08)
add(sfx, 41.0, whoosh(1.2, 200, 4000), .2)
add(sfx, 42.8, shimmer(2.6), .18); add(sfx, 44.0, bass_swell(3.5), .3)
add(sfx, 44.2, chime(1318.5, 3), .12)
add(sfx, 49.1, shimmer(1.3), .2); add(sfx, 50.35, popfx(500), .28); add(sfx, 50.35, chime(1046.5, 2), .12)
add(sfx, 51.0, popfx(1200), .15)
for i in range(3): add(sfx, 52.5 + i * .3, popfx(600 + i * 200), .22)
add(sfx, 54.25, whoosh(.75, 300, 6000), .28)

# mosque-ish reverb on sfx (FFT convolution with decaying noise IR)
irn = int(1.4 * SR); ir = noise(irn) * np.exp(-T(irn) / .35); ir = bandpass(ir, 200, 6000); ir /= np.abs(ir).sum() / 6
L = 1 << int(np.ceil(np.log2(N + irn)))
wet = np.stack([np.fft.irfft(np.fft.rfft(sfx[:, ch], L) * np.fft.rfft(ir, L), L)[:N] for ch in (0, 1)], 1)
mix = mus + sfx + wet * .18

# master: gentle limiter + normalise to about -1 dBFS peak
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix *= 0.89 / np.abs(mix).max()
pcm = (mix * 32767).astype('<i2')
out = sys.argv[1] if len(sys.argv) > 1 else 'music_sfx.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out, f'{len(pcm)/SR:.1f}s', 'endB', round(endB, 2))
