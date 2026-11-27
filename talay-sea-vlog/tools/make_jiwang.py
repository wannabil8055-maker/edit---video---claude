"""Synthesize an original Malay 'jiwang' style power-ballad instrumental.

12/8 slow-ballad feel. One bar = 4 dotted-quarter beats = 2.4 s, so every cut in
index.html (which lands on 0.6 s beats / 2.4 s bars) still falls on the music.
Triplet-eighth grid unit U = 0.2 s (12 per bar).

Arrangement:
  bar 0      hook: solo piano + reverse-cymbal swell, lead pickup
  bars 1-6   verse: piano, bass, strings, half-time ballad drums, guitar melody
  bar 6      tom fill into the lift
  bars 7-9   lift: bigger strings, crash, E7 tension, melody climbs
  bar 10     outro (24.0 s): drums drop, long sustained climax note
  bar 11     final C chord rings out to 27.0 s
Output: assets/audio/music.wav (48 kHz, stereo, 16-bit).
"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter

SR = 48000
BAR = 2.4
U = BAR / 12
TOTAL = 27.0
N = int((TOTAL + 0.5) * SR)
rng = np.random.default_rng(11)

dry = np.zeros((N, 2))
verb_send = np.zeros((N, 2))


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "low")
    return lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "high")
    return lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, x)


def place(sig, t0, pan=0.0, gain=1.0, send=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    sig = sig[: N - i0] * gain
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    dry[i0 : i0 + len(sig), 0] += sig * l
    dry[i0 : i0 + len(sig), 1] += sig * r
    if send:
        verb_send[i0 : i0 + len(sig), 0] += sig * l * send
        verb_send[i0 : i0 + len(sig), 1] += sig * r * send


# ---------------------------------------------------------------- harmony
# bar -> chord tones (MIDI), bass root
CHORDS = {
    0: ([57, 60, 64], 45),   # Am
    1: ([60, 64, 67], 48),   # C
    2: ([59, 62, 67], 47),   # G/B
    3: ([57, 60, 64], 45),   # Am
    4: ([53, 57, 60], 41),   # F
    5: ([50, 53, 57], 38),   # Dm
    6: ([55, 59, 62], 43),   # G
    7: ([60, 64, 67], 48),   # C
    8: ([56, 59, 62, 64], 40),  # E7
    9: ([57, 60, 64], 45),   # Am
    10: ([53, 57, 60], 41),  # F
    11: ([55, 60, 64], 36),  # C (final)
}


# ---------------------------------------------------------------- instruments
def piano(m, dur=1.6, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    sig = np.zeros(n)
    for h in range(1, 9):
        fh = f * h * np.sqrt(1 + 0.0004 * h * h)  # slight inharmonicity
        if fh > SR / 2.2:
            break
        sig += np.sin(2 * np.pi * fh * t) / h ** 1.4 * np.exp(-t * (1.8 + 0.9 * h))
    click = hp(rng.standard_normal(n), 2000) * np.exp(-t * 400) * 0.03
    env = np.minimum(t / 0.004, 1) * (0.75 * np.exp(-t * 2.2) + 0.25 * np.exp(-t * 0.5))
    rel = np.ones(n)
    rel[-int(0.15 * SR):] = np.linspace(1, 0, int(0.15 * SR))
    return (sig * env + click) * rel * 0.16 * vel


def strings(chord, dur, level=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in chord + [chord[0] + 12]:
        for det in (-0.08, 0.0, 0.09):
            f = hz(m) * 2 ** (det / 12)
            ph = 2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 5.2 * t)  # gentle vibrato
            for h in range(1, 7):
                sig += np.sin(h * ph) / h
    sig = lp(sig, 1700)
    a, r = int(0.7 * SR), int(0.6 * SR)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    return sig * env * 0.010 * level


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    sig = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3)
    env = np.minimum(t / 0.01, 1) * np.exp(-t * 0.9)
    r = int(0.08 * SR)
    env[-r:] *= np.linspace(1, 0, r)
    return sig * env * 0.17


def lead(m, dur, bend_from=None, vib=1.0):
    """Overdriven 'rock kapak' lead guitar: saw + bend + delayed vibrato + drive."""
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    pitch = np.full(n, float(m))
    if bend_from is not None:
        bt = int(0.12 * SR)
        pitch[:bt] = bend_from + (m - bend_from) * (np.linspace(0, 1, bt) ** 0.6)
    depth = 0.35 * vib * np.clip((t - 0.35) / 0.4, 0, 1)
    pitch = pitch + depth * np.sin(2 * np.pi * 5.6 * t)
    f = hz(pitch)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.zeros(n)
    for h in range(1, 12):
        sig += np.sin(h * ph) / h
    sig = np.tanh(sig * 3.0)
    sig = bp(sig, 250, 3200)
    sig = lp(sig, 2600)
    env = np.minimum(t / 0.012, 1)
    off = int(dur * SR)
    env[off:] *= np.exp(-(t[off:] - dur) * 18)
    env[:off] *= 0.85 + 0.15 * np.exp(-t[:off] * 4)
    return sig * env * 0.11


def kick():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.55


def snare():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 18) * 0.5
    noise = bp(rng.standard_normal(n), 1500, 8000) * np.exp(-t * 9) * 0.55
    return (body + noise) * 0.55


def hat(open_=False):
    n = int((0.35 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (8 if open_ else 70)) * 0.05


def tom(m):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = hz(m) * (1 + 0.5 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.45


def crash(dur=2.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 4000) * np.exp(-t * 1.6) * 0.09


def reverse_cymbal(dur):
    return crash(dur)[::-1] * 0.9


# ---------------------------------------------------------------- arrangement
ARP = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1]
for b, (chord, root) in CHORDS.items():
    t0 = b * BAR
    last = b == 11
    # piano triplet arpeggio (root, 5th-ish, octave, 10th)
    tones = [root + 12] + chord + [chord[0] + 12]
    if last:
        for k, m in enumerate([root + 12] + chord + [chord[1] + 12]):
            place(piano(m, 2.4, 0.9), t0 + k * 0.03, pan=-0.15 + 0.07 * k, send=0.35)
        continue
    for k in range(12):
        idx = ARP[k] if ARP[k] < len(tones) else len(tones) - 1
        m = tones[idx] + (12 if ARP[k] == 3 else 0)
        vel = (1.0 if k % 3 == 0 else 0.72) * (0.85 if b == 0 else 1.0)
        place(piano(m, 1.4, vel), t0 + k * U, pan=-0.25 + 0.05 * ARP[k], send=0.3)
    if b == 0:
        continue
    # strings
    lvl = 1.0 if b < 7 else 1.6
    place(strings(chord, BAR + 0.6, lvl), t0 - 0.1, pan=0.0, send=0.5)
    # bass
    place(bass(root, 1.15), t0)
    if b != 10:
        place(bass(root + (7 if b % 2 else 12), 0.55), t0 + 6 * U)
        place(bass(root + 7, 0.55), t0 + 9 * U)
    # drums (half-time 12/8 ballad)
    if b in (1, 7, 10):
        place(crash(), t0, pan=0.3, send=0.3)
    if b == 10:
        place(kick(), t0)
        continue
    place(kick(), t0)
    place(kick(), t0 + 10 * U, gain=0.7)
    place(snare(), t0 + 6 * U, send=0.45)
    for k in range(12):
        place(hat(open_=(k == 11 and b % 2 == 0)), t0 + k * U, pan=0.35, gain=1.0 if k % 3 == 0 else 0.6)
    if b == 6:  # tom fill into the lift
        for k, m in zip(range(6, 12), [50, 50, 45, 45, 41, 41]):
            place(tom(m), t0 + k * U, pan=-0.3 + 0.12 * (k - 6), send=0.25)

# reverse cymbal into the first downbeat (end of hook)
place(reverse_cymbal(BAR), 0.0, send=0.2)

# ---------------------------------------------------------------- melody
# (bar, unit, length_units, midi, bend_from)
MEL = [
    (0, 6, 3, 72, None), (0, 9, 3, 74, None),                        # pickup
    (1, 0, 6, 76, 74), (1, 6, 3, 74, None), (1, 9, 3, 72, None),     # C
    (2, 0, 9, 74, 72), (2, 9, 3, 71, None),                          # G/B
    (3, 0, 6, 72, None), (3, 6, 3, 76, None), (3, 9, 3, 81, 79),     # Am
    (4, 0, 6, 79, 77), (4, 6, 3, 77, None), (4, 9, 3, 76, None),     # F
    (5, 0, 6, 77, None), (5, 6, 3, 76, None), (5, 9, 3, 74, None),   # Dm
    (6, 0, 6, 74, 72), (6, 6, 3, 71, None), (6, 9, 3, 74, None),     # G
    (7, 0, 9, 76, 74), (7, 9, 3, 79, None),                          # C
    (8, 0, 6, 80, 78), (8, 6, 3, 76, None), (8, 9, 3, 74, None),     # E7
    (9, 0, 4, 72, None), (9, 4, 2, 71, None), (9, 6, 3, 72, None), (9, 9, 3, 76, None),  # Am
    (10, 0, 6, 81, 79), (10, 6, 6, 79, None),                        # F  (climax)
    (11, 0, 3, 76, 74),                                              # C  (final)
]
for b, u, ln, m, bend in MEL:
    t0 = b * BAR + u * U
    dur = ln * U * 0.97
    place(lead(m, dur, bend, vib=1.3 if ln >= 6 else 0.7), t0, pan=0.08, send=0.45)
    # slap-back delay for that 90s ballad shimmer
    place(lead(m, dur, bend) * 0.28, t0 + 0.4, pan=-0.4, send=0.5)

# ---------------------------------------------------------------- reverb (convolution)
ir_len = int(2.6 * SR)
tt = np.arange(ir_len) / SR
ir = np.stack([lp(rng.standard_normal(ir_len), 6000) * np.exp(-tt * 2.6) for _ in range(2)], axis=1)
ir[: int(0.02 * SR)] = 0  # pre-delay
ir /= np.sqrt(np.sum(ir ** 2, axis=0))
wet = np.stack([fftconvolve(verb_send[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
mix = dry + wet * 0.55
mix = np.stack([hp(mix[:, c], 45) for c in range(2)], axis=1)

mix = mix[: int(TOTAL * SR)]
fade = int(0.9 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix = np.tanh(mix * 1.3)
mix /= np.max(np.abs(mix)) / 0.75
pcm = (mix * 32767).astype(np.int16)
os.makedirs("assets/audio", exist_ok=True)
with wave.open("assets/audio/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/music.wav", TOTAL, "s")
