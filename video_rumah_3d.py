"""Video TikTok 3D — hook tapak -> animasi 3D (pelan jadi rumah) -> render sebenar -> CTA.

Usage: python3 video_rumah_3d.py FRAMES3D_DIR [output.mp4] [--frames t1 t2 ...]
FRAMES3D_DIR holds the Blender frames from house3d.py (0000.png .. 0347.png, 24 fps).
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
DUR = 25.0
N = int(DUR * FPS)
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))

args = [a for a in sys.argv[1:] if not a.startswith("--")]
FR3D = args[0]
OUT = args[1] if len(args) > 1 and "--frames" not in sys.argv else os.path.join(HERE, "video_rumah_3d.mp4")

T3D = 2.5                          # 3D sequence starts here
L3D = 14.5                         # and lasts this long
DROP = T3D + 6.4 + 0.3636          # main roof first touches the walls
BEAT = 0.5
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


SPEC_CHIPS = [("4 BILIK TIDUR", 2), ("3 BILIK AIR", 4), ("1,440 KAKI PERSEGI", 6), ("39' x 38'", 8)]


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
    # 1. plan on the ground
    fo = clamp((lt - 1.9) / 0.3)
    pop(c, word_img("PELAN LANTAI", 96, WHITE), W / 2, 330, lt - 0.25, fade_out=fo)
    pop(c, word_img("39' x 38'", 84, INK, box=YELLOW), W / 2, 460, lt - 0.55, fade_out=fo)
    # 2. walls rising
    fo = clamp((lt - 4.9) / 0.3)
    pop(c, word_img("DIBINA", 120, WHITE), W / 2, 330, lt - 2.1, fade_out=fo)
    pop(c, word_img("IKUT PELAN", 110, INK, box=YELLOW, pad=(30, 10)), W / 2, 480, lt - 2.35, fade_out=fo)
    # 3. roof drop
    fo = clamp((lt - 5.6) / 0.25)
    pop(c, word_img("BUMBUNG", 120, WHITE), W / 2, 330, lt - 5.0, fade_out=clamp((t - DROP + 0.05) / 0.15))
    pop(c, word_img("SIAP!", 220, INK, box=YELLOW, pad=(40, 14)), W / 2, 400, t - DROP,
        fade_out=clamp((t - DROP - 1.2) / 0.3))
    # 4. spec chips stacking on the beat during the orbit
    for i, (label, kb) in enumerate(SPEC_CHIPS):
        st = t - beat_at(kb)
        if st < 0 or t > T3D + L3D - 0.15:
            continue
        chip(c, label, st, y=250 + i * 125)
    return c


# ---------------------------------------------------------------- real renders (fast cuts)
CUTS = [
    (T3D + L3D, beat_at(18), depan, 3.2, 3.35, (300, 330), (800, 330), "REKA BENTUK SEBENAR"),
    (beat_at(18), beat_at(21), kiri, 3.25, 3.35, (260, 330), (780, 340), "ANJUNG LUAS"),
    (beat_at(21), beat_at(24), kanan, 3.3, 3.2, (820, 330), (300, 330), "RUMAH SETINGKAT"),
]
CTA_START = beat_at(24)


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
    elif t < CTA_START:
        c = scene_cuts(t)
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
        elif T3D + 2.0 <= bt < T3D + 5.6:
            add(bt, thud(), 0.45)
            add(bt + BEAT / 2, hat(), 0.08)
    # pops for windows (5.0-6.2 in 3D time)
    for j in range(8):
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
    for ct in [T3D, T3D + L3D, beat_at(18), beat_at(21), CTA_START]:
        lt = np.arange(int(0.45 * SR)) / SR
        w = np.convolve(rng.standard_normal(len(lt)), np.ones(12) / 12, mode="same") * np.sin(np.pi * lt / 0.45) ** 2
        add(ct - 0.25, w, 0.35)
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
