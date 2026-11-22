"""Video TikTok 5 lot — hook tapak -> 5 rumah dibina sebaris (3D) -> render sebenar -> CTA.

Usage: python3 video_rumah_lots.py FRAMES3D_DIR [output.mp4] [--frames t1 t2 ...]
FRAMES3D_DIR holds the Blender frames from house3d_lots.py (0000.png .. 0275.png, 24 fps).
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import video_rumah_v2 as v2
from video_rumah import depan, kiri, kanan

W, H, FPS = 1080, 1920, 24
L3D = 11.5
T3D = 2.5
DROP = T3D + 6.4 + 0.3636
BEAT = 0.5
DUR = DROP + 29 * BEAT + 4.0
N = int(DUR * FPS)
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))

args = [a for a in sys.argv[1:] if not a.startswith("--")]
FR3D = args[0]
OUT = args[1] if len(args) > 1 and "--frames" not in sys.argv else os.path.join(HERE, "video_rumah_5lot.mp4")

LOT_DELAY = [0.0, 0.35, 0.7, 1.05, 1.4]   # build start of each plot (matches house3d_lots.py)
YELLOW, INK, WHITE, GREEN = v2.YELLOW, v2.INK, v2.WHITE, v2.GREEN

clamp, ease, ease_io, back = v2.clamp, v2.ease, v2.ease_io, v2.back
word_img, pop, chip, flash = v2.word_img, v2.pop, v2.chip, v2.flash


def beat_at(k):
    return DROP + k * BEAT


# ---------------------------------------------------------------- 3D frames
_last = {}


def frame3d(t):
    idx = int(round((t - T3D) * 24))
    idx = max(0, min(idx, int(L3D * 24) - 1))
    if idx in _last:
        return _last[idx].copy()
    p = os.path.join(FR3D, f"{idx:04d}.png")
    while not os.path.exists(p) and idx > 0:   # fall back to the nearest earlier frame
        idx -= 1
        p = os.path.join(FR3D, f"{idx:04d}.png")
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=50, threshold=2))
    _last.clear()
    _last[idx] = im
    return im.copy()


SPEC_CHIPS = [("TANAH 5,000 KAKI PERSEGI", 7), ("4 BILIK TIDUR", 7.5), ("3 BILIK AIR", 8), ("BINAAN 1,440 KAKI PERSEGI", 8.5)]


def scene_3d(t):
    lt = t - T3D
    fr = frame3d(t)
    # camera shake when the roof slams down
    if DROP <= t < DROP + 0.3:
        s = 1 - (t - DROP) / 0.3
        dx = int(14 * s * math.sin((t - DROP) * 90))
        dy = int(10 * s * math.cos((t - DROP) * 70))
        fr = Image.fromarray(np.roll(np.roll(np.asarray(fr), dx, 1), dy, 0))
    fr = v2.grade(fr, t, leak=0.25 + 0.35 * clamp((t - DROP) / 1.0))
    fr = flash(fr, 0.8 * (1 - (t - T3D) / 0.2) if t < T3D + 0.2 else 0)
    fr = flash(fr, 0.75 * (1 - (t - DROP) / 0.25) if DROP <= t < DROP + 0.25 else 0)
    c = fr.convert("RGBA")
    # 1. five empty plots on the land
    fo = clamp((lt - 1.9) / 0.3)
    pop(c, word_img("5 LOT TANAH", 110, WHITE), W / 2, 330, lt - 0.25, fade_out=fo)
    pop(c, word_img("5,000 KAKI PERSEGI / LOT", 66, INK, box=YELLOW), W / 2, 460, lt - 0.55, fade_out=fo)
    # 2. walls rising, plot after plot
    fo = clamp((lt - 5.2) / 0.3)
    pop(c, word_img("5 UNIT", 140, WHITE), W / 2, 330, lt - 2.1, fade_out=fo)
    pop(c, word_img("BANGLO SETINGKAT", 84, INK, box=YELLOW, pad=(30, 10)), W / 2, 480, lt - 2.35, fade_out=fo)
    # 3. roofs land one by one: count them
    for i, d in enumerate(LOT_DELAY):
        land = DROP + d
        nxt = DROP + LOT_DELAY[i + 1] if i + 1 < len(LOT_DELAY) else land + 0.45
        if land <= t < nxt + 0.15:
            pop(c, word_img(f"RUMAH {i + 1}", 120, WHITE), W / 2, 330, t - land,
                fade_out=clamp((t - nxt) / 0.15))
    last = DROP + LOT_DELAY[-1] + 0.45
    pop(c, word_img("5 RUMAH", 130, WHITE), W / 2, 320, t - last, fade_out=clamp((t - last - 1.3) / 0.3))
    pop(c, word_img("SIAP!", 220, INK, box=YELLOW, pad=(40, 14)), W / 2, 470, t - last - 0.15,
        fade_out=clamp((t - last - 1.3) / 0.3))
    # 4. spec chips stacking on the beat during the fly-down
    for i, (label, kb) in enumerate(SPEC_CHIPS):
        st = t - beat_at(kb)
        if st < 0 or t > T3D + L3D - 0.15:
            continue
        chip(c, label, st, y=250 + i * 125)
    return c


# ---------------------------------------------------------------- real renders (fast cuts)
CUTS = [
    (T3D + L3D, beat_at(13), depan, 3.2, 3.35, (300, 330), (800, 330), "REKA BENTUK SEBENAR"),
    (beat_at(13), beat_at(16), kiri, 3.25, 3.35, (260, 330), (780, 340), "ANJUNG LUAS"),
    (beat_at(16), beat_at(19), kanan, 3.3, 3.2, (820, 330), (300, 330), "5 LOT SAHAJA"),
]
PRICE_START = beat_at(19)
CTA_START = beat_at(29)
RED = (230, 57, 70)


def scene_price(t):
    """Price card: normal price struck out -> first-buyer rebate -> price after rebate."""
    lt = t - PRICE_START
    k = lt / (CTA_START - PRICE_START)
    fr = v2.fullbleed(kanan, 3.0 + 0.25 * k, 560, 340)
    fr = fr.filter(ImageFilter.GaussianBlur(10))
    fr = Image.fromarray((np.asarray(v2.grade(fr, t, leak=0.3), np.float32) * 0.42).astype(np.uint8))
    fr = flash(fr, 0.6 * (1 - lt / 0.15))
    c = fr.convert("RGBA")
    pop(c, word_img("HARGA BIASA", 66, WHITE), W / 2, 430, lt - 0.1)
    old = word_img("RM419,000", 150, WHITE)
    pop(c, old, W / 2, 570, lt - 0.3)
    ks = ease(clamp((lt - 1.1) / 0.3))
    if ks > 0:                                  # red strike-through
        d = ImageDraw.Draw(c)
        x0 = W / 2 - old.width / 2 + 20
        x1 = x0 + (old.width - 40) * ks
        d.line([(x0, 585), (x1, 555)], fill=RED + (255,), width=14)
    pop(c, word_img("PEMBELI RUMAH PERTAMA", 62, WHITE), W / 2, 800, lt - 1.5)
    pop(c, word_img("REBATE RM20,000", 100, INK, box=YELLOW, pad=(34, 12)), W / 2, 940, lt - 1.75)
    pop(c, word_img("HARGA SELEPAS REBATE", 58, WHITE), W / 2, 1170, lt - 2.6)
    pop(c, word_img("RM399,000", 160, YELLOW), W / 2, 1330, lt - 2.85, dur=0.45)
    chip(c, "TANAH 5,000 KAKI PERSEGI", lt - 3.3, y=1560)
    return c


def scene_cuts(t):
    for (a, b, img, s0, s1, f0, f1, cap) in CUTS:
        if a <= t < b:
            lt = t - a
            k = ease_io(lt / (b - a))
            punch = 1 + 0.14 * (1 - ease(lt / 0.28))
            fr = v2.fullbleed(img, (s0 + (s1 - s0) * k) * punch,
                              f0[0] + (f1[0] - f0[0]) * k, f0[1] + (f1[1] - f0[1]) * k)
            fr = v2.grade(fr, t, leak=0.6)
            if img is depan and lt < 0.45:      # 3D -> real render: dissolve through a flash
                fr = Image.blend(scene_3d(T3D + L3D - 0.01).convert("RGB"), fr, ease(lt / 0.45))
                fr = flash(fr, 0.6 * math.sin(math.pi * clamp(lt / 0.45)))
            else:
                fr = flash(fr, 0.5 * (1 - lt / 0.12))
            c = fr.convert("RGBA")
            chip(c, cap, lt - 0.15)
            return c
    return None


def frame(i):
    t = i / FPS
    if t < T3D:
        c = v2.scene_hook(t * 3.0 / T3D)
    elif t < T3D + L3D:
        c = scene_3d(t)
    elif t < PRICE_START:
        c = scene_cuts(t)
    elif t < CTA_START:
        c = scene_price(t)
    else:
        c = v2.scene_cta(21.0 + (t - CTA_START))
    img = c.convert("RGB")
    g = ease(t / 0.25) * ease((DUR - t) / 0.6)
    if g < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * g).astype(np.uint8))
    return img


# ---------------------------------------------------------------- music (120 bpm, drop on the roof)
def soundtrack(path):
    n = int(SR * DUR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    rng = np.random.default_rng(5)

    def add(start, sig, g=1.0):
        i0 = int(start * SR)
        if i0 >= n:
            return
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        i1 = min(n, i0 + len(sig))
        L[i0:i1] += g * sig[: i1 - i0]

    def kick(dur=0.4):
        lt = np.arange(int(dur * SR)) / SR
        return np.exp(-lt * 9) * np.sin(2 * np.pi * (48 * lt + 120 * (1 - np.exp(-lt * 35)) / 35))

    def clap():
        lt = np.arange(int(0.25 * SR)) / SR
        nz = rng.standard_normal(len(lt))
        nz = nz - np.convolve(nz, np.ones(6) / 6, mode="same")
        return nz * (np.exp(-lt * 22) + 0.6 * np.exp(-((lt - 0.012) * 300) ** 2))

    def hat():
        lt = np.arange(int(0.06 * SR)) / SR
        nz = rng.standard_normal(len(lt))
        return (nz - np.convolve(nz, np.ones(3) / 3, mode="same")) * np.exp(-lt * 70)

    def tone(f, dur, decay=4.0, harm=(1, 0.5, 0.25)):
        lt = np.arange(int(dur * SR)) / SR
        sig = sum(a * np.sin(2 * np.pi * f * (k + 1) * lt) for k, a in enumerate(harm))
        return sig * np.exp(-lt * decay) * np.minimum(1, lt / 0.005)

    def thud():
        lt = np.arange(int(0.3 * SR)) / SR
        return np.sin(2 * np.pi * (70 + 60 * np.exp(-lt * 25)) * lt) * np.exp(-lt * 14)

    prog = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (130.8, 196.0, 261.6), (196.0, 246.9, 293.7)]
    k0 = int(math.floor(-DROP / BEAT)) - 1
    kend = int((DUR - DROP) / BEAT) + 1
    beats = [(k, DROP + k * BEAT) for k in range(k0, kend) if 0 <= DROP + k * BEAT < DUR]

    def chord_at(tt):
        bar_i = int(math.floor((tt - DROP) / (BEAT * 4)))
        return prog[bar_i % 4]

    # pads
    for k, bt in beats:
        if k % 4 == 0:
            ch = chord_at(bt + 0.01)
            dur = BEAT * 4 + 0.2
            lt = np.arange(int(dur * SR)) / SR
            env = np.minimum(1, lt / 0.3) * np.minimum(1, (dur - lt) / 0.3)
            g = 0.045 if bt < DROP else 0.065
            for f in ch:
                add(bt, env * (np.sin(2 * np.pi * f * lt) + 0.2 * np.sin(2 * np.pi * f * 2.01 * lt)), g)
    # plucks (8ths)
    for k, bt in beats:
        for h in (0, 1):
            tt = bt + h * BEAT / 2
            ch = chord_at(tt)
            f = (ch[0] * 2, ch[2] * 2, ch[1] * 2, ch[2] * 4)[(2 * k + h) % 4]
            if tt < DUR - 0.8:
                add(tt, tone(f, 0.4, 9, (1, 0.3)), 0.065)
    # hook kicks, then "construction" thuds on each beat while the walls rise
    for k, bt in beats:
        if bt < T3D:
            add(bt, kick(), 0.35)
        elif T3D + 2.0 <= bt < T3D + 6.6:
            add(bt, thud(), 0.45)
            add(bt + BEAT / 2, hat(), 0.08)
    # pops for windows (5.0-6.2 in 3D time)
    for j in range(16):
        add(T3D + 5.0 + j * 0.15, tone(880 + 110 * j, 0.15, 25, (1, 0.2)), 0.05)
    # riser into the roof drop + snare roll
    rs = DROP - 2.0
    lt = np.arange(int(2.0 * SR)) / SR
    riser = np.convolve(rng.standard_normal(len(lt)), np.ones(8) / 8, mode="same") * (lt / 2.0) ** 2
    riser += 0.4 * np.sin(2 * np.pi * (200 * lt + 400 * lt ** 2)) * (lt / 2.0) ** 2
    add(rs, riser, 0.35)
    st = DROP - 1.5
    while st < DROP - 0.02:
        add(st, clap(), 0.10 + 0.14 * (st - (DROP - 1.5)) / 1.5)
        rem = DROP - st
        st += BEAT / 2 if rem > 1.0 else (BEAT / 4 if rem > 0.5 else BEAT / 8)
    # roof impact
    lt = np.arange(int(1.6 * SR)) / SR
    add(DROP, np.sin(2 * np.pi * (38 * lt + 70 * (1 - np.exp(-lt * 6)) / 6)) * np.exp(-lt * 2.3), 1.0)
    for d in LOT_DELAY[1:]:
        add(DROP + d, thud(), 0.5)
    add(DROP, np.convolve(rng.standard_normal(len(lt)) * np.exp(-lt * 5), np.ones(4) / 4, mode="same"), 0.25)
    # full beat after the drop
    for k, bt in beats:
        if bt >= DROP and bt < DUR - 1.0:
            add(bt, kick(), 0.6)
            if k % 2 == 1:
                add(bt, clap(), 0.22)
            add(bt + BEAT / 2, hat(), 0.12)
            ch = chord_at(bt)
            f = ch[0] / 2 if ch[0] > 160 else ch[0]
            add(bt, tone(f, BEAT / 2, 6, (1, 0.6, 0.3)), 0.15)
            add(bt + BEAT / 2, tone(f, BEAT / 2, 6, (1, 0.6, 0.3)), 0.15)
    # whooshes at cuts
    for ct in [T3D, T3D + L3D, beat_at(13), beat_at(16), PRICE_START, CTA_START]:
        lt = np.arange(int(0.45 * SR)) / SR
        w = np.convolve(rng.standard_normal(len(lt)), np.ones(12) / 12, mode="same") * np.sin(np.pi * lt / 0.45) ** 2
        add(ct - 0.25, w, 0.35)
    # price reveal: strike hit, rebate pop, final-price chime
    add(PRICE_START + 1.1, thud(), 0.5)
    add(PRICE_START + 1.75, tone(1318.5, 0.5, 6, (1, 0.4)), 0.12)
    for j, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
        add(PRICE_START + 2.85 + j * 0.07, tone(f, 0.9, 4, (1, 0.3)), 0.11)
    # sidechain duck
    duck = np.ones(n)
    for k, bt in beats:
        if bt >= DROP:
            i0 = int(bt * SR)
            seg = 1 - 0.35 * np.exp(-(np.arange(int(0.25 * SR)) / SR) * 12)
            j1 = min(n, i0 + len(seg))
            duck[i0:j1] = np.minimum(duck[i0:j1], seg[: j1 - i0])
    L *= duck
    L *= np.minimum(1, t / 0.05) * np.clip((DUR - t) / 1.2, 0, 1)
    L = np.tanh(L * 1.4) / np.tanh(1.4)
    L = L / np.abs(L).max() * 0.88
    stereo = np.stack([L, np.roll(L, 180)], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())


def main():
    if "--frames" in sys.argv:
        for s in sys.argv[sys.argv.index("--frames") + 1:]:
            frame(int(round(float(s) * FPS))).save(f"v3d_{s}.png")
        return
    wav = OUT.rsplit(".", 1)[0] + "_audio.wav"
    soundtrack(wav)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT,
    ], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close()
    p.wait()
    os.remove(wav)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
