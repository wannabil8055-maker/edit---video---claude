"""Synthesize a royalty-free tropical-chill music bed for the vlog.

100 BPM, 4/4 -> 1 beat = 0.6 s, 1 bar = 2.4 s. Cuts in index.html land on bar lines.
Structure (bars): 0 hook (pad + filtered pluck + riser), 1-9 full groove, 10 outro.
Output: assets/audio/music.wav (48 kHz stereo).
"""
import wave
import numpy as np

SR = 48000
BPM = 100
BEAT = 60 / BPM
BAR = BEAT * 4
TOTAL = 26.4 + 1.2
N = int(TOTAL * SR)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0] * gain
    L[i0 : i0 + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i0 : i0 + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def onepole_lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def env_adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    sus = max(n - a - d - r, 0)
    return np.concatenate([
        np.linspace(0, 1, a, endpoint=False),
        np.linspace(1, s, d, endpoint=False),
        np.full(sus, s),
        np.linspace(s, 0, r),
    ])[:n]


# Chords: Am  F  C  G (voicings as MIDI)
CHORDS = [
    [57, 60, 64, 69],  # Am
    [53, 57, 60, 65],  # F
    [55, 60, 64, 67],  # C
    [55, 59, 62, 67],  # G
]
BASS = [45, 41, 48, 43]


def pad(chord, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in chord:
        f = note_hz(m)
        for det in (-0.12, 0.12):
            ff = f * 2 ** (det / 12)
            # soft saw from a few harmonics
            for h in range(1, 6):
                sig += np.sin(2 * np.pi * ff * h * t) / (h * 1.6)
    sig = onepole_lp(sig, 1400)
    return sig * env_adsr(n, 0.35, 0.3, 0.8, 0.5) * 0.035


def pluck(midi, dur=0.5, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = note_hz(midi)
    sig = np.sin(2 * np.pi * f * t) + 0.35 * bright * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    sig += 0.2 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 12)
    return sig * np.exp(-t * 7) * 0.16


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    freq = 48 + 110 * np.exp(-t * 28)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    return np.sin(phase) * np.exp(-t * 7.5) * 0.85


def clap():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    hp = noise - onepole_lp(noise, 900)
    e = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return hp * e * 0.22


def shaker():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    hp = noise - onepole_lp(noise, 5000)
    return hp * np.exp(-t * 60) * 0.07


def bass(midi, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = note_hz(midi)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2 * t)
    return sig * env_adsr(n, 0.01, 0.1, 0.7, 0.08) * 0.28


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep cutoff by chunks
    chunks = 24
    for c in range(chunks):
        a, b = c * n // chunks, (c + 1) * n // chunks
        cut = 400 + 7000 * (c / chunks) ** 2
        seg = noise[a:b]
        out[a:b] = seg - onepole_lp(seg, cut)
    return out * (t / dur) ** 2 * 0.12


def impact():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    freq = 40 + 60 * np.exp(-t * 10)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    boom = np.sin(phase) * np.exp(-t * 2.8) * 0.7
    noise = rng.standard_normal(n)
    return boom + onepole_lp(noise, 2500) * np.exp(-t * 6) * 0.25


def whoosh(dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    bp = onepole_lp(noise, 3000) - onepole_lp(noise, 500)
    e = np.sin(np.pi * t / dur) ** 2
    return bp * e * 0.18


ARP = [0, 2, 1, 3, 2, 1, 3, 2]  # index into chord voicing, 8ths
n_bars = int(np.ceil(TOTAL / BAR))
for b in range(n_bars):
    t0 = b * BAR
    ci = b % 4
    chord = CHORDS[ci]
    outro = b >= 10
    hook = b == 0
    add(pad(chord, BAR + 0.4), t0, gain=1.0 if not outro else 1.1)
    # arp plucks (8th notes) an octave up
    for k in range(8):
        tk = t0 + k * BEAT / 2
        if tk > 26.4:
            break
        m = chord[ARP[k]] + 12
        pan = -0.35 if k % 2 == 0 else 0.35
        add(pluck(m, bright=0.4 if hook else 1.0), tk, pan=pan, gain=0.55 if hook else 1.0)
    if hook or outro:
        continue
    for beat in range(4):
        tb = t0 + beat * BEAT
        add(kick(), tb)
        if beat in (1, 3):
            add(clap(), tb, pan=0.05)
        # offbeat bass (tropical feel)
        add(bass(BASS[ci], BEAT * 0.45), tb + BEAT / 2)
        for s in range(4):
            add(shaker(), tb + s * BEAT / 4, pan=0.4, gain=1.0 if s % 2 else 0.55)

# hook riser + impact on the first downbeat
add(riser(BAR), 0.0)
add(impact(), BAR)
# whooshes just before each cut (cut times mirror index.html)
for cut in [4.2, 6.0, 9.6, 13.2, 15.6, 19.2, 21.8, 24.0]:
    add(whoosh(), cut - 0.3, pan=0.0)
# final impact on outro start
add(impact(), 24.0, gain=0.6)

mix = np.stack([L, R], axis=1)
# fade out last 1.6 s
fade = int(1.6 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
# soft clip + normalize to -1 dBFS peak
mix = np.tanh(mix * 1.4)
mix /= np.max(np.abs(mix)) / 0.75
pcm = (mix * 32767).astype(np.int16)
import os
os.makedirs("assets/audio", exist_ok=True)
with wave.open("assets/audio/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/music.wav", TOTAL, "s")
