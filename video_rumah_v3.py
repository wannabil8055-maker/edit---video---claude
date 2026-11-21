"""Video TikTok v3 — gaya mewah & sinematik (hitam, emas, serif, piano).

Usage: python3 video_rumah_v3.py [output.mp4] [--frames t1 t2 ...]
Vertical 1080x1920, 30 s. Soundtrack (piano + strings pad) synthesized in code.
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import video_rumah as vr
from video_rumah import tapak, depan, kiri, kanan, pelan, logo

W, H, FPS = 1080, 1920, 30
DUR = 30.0
N = int(FPS * DUR)
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args and "--frames" not in sys.argv else os.path.join(HERE, "video_rumah_tiktok_v3.mp4")

BLACK = (10, 10, 12)
GOLD = (201, 164, 92)
GOLD_L = (232, 205, 150)
IVORY = (244, 238, 226)
GREY = (150, 146, 140)

SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-{}.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-{}.otf"


def serif(size, style="Regular"):
    return ImageFont.truetype(SERIF.format(style), size)


def sans(size, weight="Light"):
    return ImageFont.truetype(SANS.format(weight), size)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def fade(t, a, b, fi=0.8, fo=0.8):
    return ease((t - a) / fi) * ease((b - t) / fo)


# ---------------------------------------------------------------- text with tracking
def tracked(d, cx, y, s, font, fill, alpha, spacing=0.0, anchor_mid=True):
    """Draw text centred at cx with extra letter spacing (px)."""
    if alpha <= 0:
        return
    widths = [d.textlength(ch, font=font) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2 if anchor_mid else cx
    col = fill + (int(255 * clamp(alpha)),)
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=font, fill=col, anchor="ls")
        x += w + spacing


def gold_line(d, cx, y, half, k, alpha=1.0):
    if k <= 0 or alpha <= 0:
        return
    hw = half * ease(k)
    d.line([(cx - hw, y), (cx + hw, y)], fill=GOLD + (int(255 * alpha),), width=2)


# ---------------------------------------------------------------- framed photo
FW, FH = 900, 1125                     # 4:5 frame
FX, FY = (W - FW) // 2, 330


def framed(img, t01, z0, z1, c0, c1, bw=False):
    """Slow push inside the 4:5 frame."""
    t = ease_io(t01)
    z = z0 + (z1 - z0) * t
    cx = c0 + (c1 - c0) * t
    iw, ih = img.size
    bh = min(ih, iw * FH / FW) / z
    bwid = bh * FW / FH
    x0 = min(max(cx * iw - bwid / 2, 0), iw - bwid)
    y0 = (ih - bh) / 2
    out = img.resize((FW, FH), Image.BICUBIC, box=(x0, y0, x0 + bwid, y0 + bh))
    out = out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    if bw:
        g = out.convert("L").convert("RGB")
        out = Image.blend(g, Image.new("RGB", out.size, (40, 34, 26)), 0.12)
    return out


def film(img, t):
    a = np.asarray(img, np.float32) / 255
    a = np.clip((a - 0.5) * 1.06 + 0.5, 0, 1)
    rng = np.random.default_rng(int(t * 997))
    a += rng.normal(0, 0.012, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def base():
    return Image.new("RGBA", (W, H), BLACK + (255,))


def put_frame(c, ph, alpha, border=True):
    if alpha <= 0:
        return
    im = ph.convert("RGBA")
    if alpha < 1:
        im.putalpha(int(255 * alpha))
    c.alpha_composite(im, (FX, FY))
    if border:
        d = ImageDraw.Draw(c)
        o = 18
        d.rectangle([FX - o, FY - o, FX + FW + o, FY + FH + o], outline=GOLD + (int(200 * alpha),), width=2)


def index_label(d, n, total, alpha):
    tracked(d, W / 2, FY - 60, f"{n:02d}  /  {total:02d}", sans(26, "Regular"), GOLD, alpha, 6)


def caption(d, t, a, b, small, big, italic=None):
    al = fade(t, a, b, 0.9, 0.6)
    y0 = FY + FH + 110
    k = ease((t - a) / 1.0)
    tracked(d, W / 2, y0, small, sans(28, "Regular"), GOLD, al, 10)
    tracked(d, W / 2, y0 + 92 + (1 - k) * 20, big, serif(76), IVORY, al, 1)
    if italic:
        tracked(d, W / 2, y0 + 150 + (1 - k) * 20, italic, serif(40, "Italic"), GREY, al * ease((t - a - 0.4) / 0.8), 0)


# ---------------------------------------------------------------- scenes
def scene_intro(t):          # 0 .. 4.5
    c = base()
    d = ImageDraw.Draw(c)
    a = fade(t, 0.3, 4.3, 1.0, 0.6)
    gold_line(d, W / 2, 820, 160, (t - 0.3) / 1.2, a)
    sp = 4 + 14 * ease(t / 4.5)          # slow tracking expansion
    tracked(d, W / 2, 900, "AA LAND SDN BHD", sans(30, "Regular"), GOLD, a * ease((t - 0.6) / 1.0), sp)
    tracked(d, W / 2, 1030, "Sebuah Kediaman", serif(92), IVORY, a * ease((t - 1.2) / 1.0), 1)
    tracked(d, W / 2, 1130, "untuk keluarga anda", serif(60, "Italic"), GOLD_L, a * ease((t - 1.8) / 1.0), 0)
    gold_line(d, W / 2, 1200, 60, (t - 2.2) / 1.0, a)
    return c


def scene_land(t):           # 4.5 .. 10.5 (land in B&W, then curtain reveal to colour house)
    lt = t - 4.5
    c = base()
    a_in = ease(lt / 1.0)
    land = framed(tapak, lt / 6.0, 1.0, 1.12, 0.48, 0.55, bw=True)
    ph = land
    if t >= 8.0:
        k = ease_io((t - 8.0) / 1.6)
        house = framed(depan, (t - 8.0) / 8.0, 1.0, 1.06, 0.40, 0.45)
        # curtain: house revealed from the centre outwards
        m = Image.new("L", (FW, FH), 0)
        hw = FW / 2 * k
        ImageDraw.Draw(m).rectangle([FW / 2 - hw, 0, FW / 2 + hw, FH], fill=255)
        ph = land.copy()
        ph.paste(house, (0, 0), m.filter(ImageFilter.GaussianBlur(6)))
        if 0 < k < 1:
            dd = ImageDraw.Draw(ph)
            for x in (FW / 2 - hw, FW / 2 + hw):
                dd.line([(x, 0), (x, FH)], fill=GOLD_L, width=3)
    put_frame(c, ph, a_in)
    d = ImageDraw.Draw(c)
    caption(d, t, 5.0, 8.0, "BERMULA DI SINI", "Sebidang Tanah", "tapak sebenar projek")
    caption(d, t, 9.0, 12.0, "KINI", "Rumah Impian", "reka bentuk siap dibina")
    return c


SHOTS = [
    # start, end, img, z0, z1, c0, c1, small, big, italic
    (10.5, 15.0, depan, 1.06, 1.18, 0.45, 0.62, "FASAD", "Klasik Moden", "bumbung biru, dinding putih"),
    (15.0, 19.5, kiri, 1.0, 1.12, 0.62, 0.45, "ANJUNG", "Luas & Selesa", "tiang batu hiasan"),
    (19.5, 24.0, kanan, 1.12, 1.0, 0.40, 0.58, "KEDIAMAN", "Setingkat", "tenang untuk seisi keluarga"),
]


def shot_photo(t):
    for i, (a, b, img, z0, z1, c0, c1, *_r) in enumerate(SHOTS):
        if a <= t < b:
            return i, framed(img, (t - a) / (b - a), z0, z1, c0, c1)
    return None, None


def scene_shots(t):          # 10.5 .. 24
    c = base()
    i, ph = shot_photo(t)
    # cross-dissolve 0.8 s into each new shot
    a, b = SHOTS[i][0], SHOTS[i][1]
    if i == 0:
        # continuity from the curtain reveal (same image), keep
        put_frame(c, framed(depan, (t - 8.0) / 8.0, 1.0, 1.06, 0.40, 0.45) if t < 12.0 else ph, 1.0)
        if t < 12.0:
            k = ease_io((t - 10.5) / 1.5)
            c2 = base()
            put_frame(c2, ph, 1.0)
            c = Image.blend(c, c2, k)
    else:
        prev = SHOTS[i - 1]
        pph = framed(prev[2], (t - prev[0]) / (prev[1] - prev[0]), *prev[3:7])
        put_frame(c, pph, 1.0)
        k = ease_io((t - a) / 0.9)
        if k < 1:
            c2 = base()
            put_frame(c2, ph, 1.0)
            c = Image.blend(c, c2, k)
        else:
            c = base()
            put_frame(c, ph, 1.0)
    d = ImageDraw.Draw(c)
    if t >= 10.5:
        if t < 12.0:
            caption(d, t, 9.0, 12.0, "KINI", "Rumah Impian", "reka bentuk siap dibina")
        index_label(d, i + 1, 3, fade(t, 10.8, 23.8, 0.8, 0.6))
        s = SHOTS[i]
        caption(d, t, max(s[0] + 0.5, 12.2), s[1] - 0.2, s[7], s[8], s[9])
    return c


SPECS = [("4", "Bilik Tidur"), ("3", "Bilik Air"), ("1,440", "Kaki Persegi"), ("39' × 38'", "Ukuran Rumah")]


def scene_plan(t):           # 24 .. 28 (overlaps into outro)
    lt = t - 24.0
    c = base()
    d = ImageDraw.Draw(c)
    a = ease(lt / 0.9)
    tracked(d, W / 2, 250, "PELAN LANTAI", sans(28, "Regular"), GOLD, a, 10)
    gold_line(d, W / 2, 285, 70, lt / 1.0, a)
    pw = 760
    ph = int(pelan.height * pw / pelan.width)
    im = pelan.resize((pw, ph), Image.LANCZOS)
    # warm, slightly dimmed plan on an ivory card with a gold rule
    card = Image.new("RGBA", (pw + 40, ph + 40), IVORY + (255,))
    card.paste(im, (20, 20))
    if a < 1:
        card.putalpha(int(255 * a))
    c.alpha_composite(card, ((W - card.width) // 2, 340 + int((1 - a) * 30)))
    d.rectangle([(W - card.width) // 2 - 14, 340 - 14 + int((1 - a) * 30),
                 (W + card.width) // 2 + 14, 340 + card.height + 14 + int((1 - a) * 30)],
                outline=GOLD + (int(200 * a),), width=2)
    y = 340 + card.height + 120
    for i, (num, lab) in enumerate(SPECS):
        al = ease((lt - 0.6 - i * 0.35) / 0.8)
        col, row = i % 2, i // 2
        cx = W / 2 + (col - 0.5) * 460
        yy = y + row * 190
        tracked(d, cx, yy, num, serif(84), GOLD_L, al, 1)
        tracked(d, cx, yy + 50, lab.upper(), sans(24, "Regular"), GREY, al, 6)
    d.line([(W / 2, y - 70), (W / 2, y + 260)], fill=GOLD + (int(120 * ease((lt - 0.6) / 1.2)),), width=1)
    return c


def scene_outro(t):          # 27.5 .. 30
    lt = t - 27.5
    c = base()
    d = ImageDraw.Draw(c)
    a = ease(lt / 0.9)
    lw = 560
    lh = int(lw * logo.height / logo.width)
    card = Image.new("RGBA", (lw + 40, lh + 40), (255, 255, 255, 255))
    card.paste(logo.resize((lw, lh), Image.LANCZOS), (20, 20))
    card.putalpha(int(255 * a))
    cy = 560
    c.alpha_composite(card, ((W - card.width) // 2, cy - card.height // 2))
    d.rectangle([(W - card.width) // 2 - 16, cy - card.height // 2 - 16,
                 (W + card.width) // 2 + 16, cy + card.height // 2 + 16], outline=GOLD + (int(200 * a),), width=2)
    tracked(d, W / 2, 930, "Kediaman Impian", serif(88), IVORY, ease((lt - 0.3) / 0.9), 1)
    tracked(d, W / 2, 1020, "anda menanti", serif(60, "Italic"), GOLD_L, ease((lt - 0.5) / 0.9), 0)
    gold_line(d, W / 2, 1090, 90, (lt - 0.6) / 0.8, 1.0)
    al = ease((lt - 0.8) / 0.9)
    tracked(d, W / 2, 1180, "HUBUNGI KAMI", sans(28, "Regular"), GOLD, al, 10)
    tracked(d, W / 2, 1275, "010-764 6392", serif(72), IVORY, al, 3)
    tracked(d, W / 2, 1365, "016-696 6781", serif(72), IVORY, ease((lt - 1.0) / 0.9), 3)
    return c


def frame(i):
    t = i / FPS
    if t < 4.5:
        c = scene_intro(t)
    elif t < 10.5:
        c = scene_land(t)
    elif t < 24.0:
        c = scene_shots(t)
    elif t < 27.5:
        c = scene_plan(t)
    else:
        c = scene_outro(t)
    # dip to black between major sections
    dip = 1.0
    for tc in (24.0, 27.5):
        dip *= clamp(abs(t - tc) / 0.45)
    img = c.convert("RGB")
    g = dip * ease(t / 0.6) * ease((DUR - t) / 1.2)
    if g < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * ease(g)).astype(np.uint8))
    return film(img, t)


# ---------------------------------------------------------------- music: piano + strings, 72 bpm
def soundtrack(path):
    n = int(SR * DUR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    beat = 60 / 72
    bar = beat * 4

    def add(start, sig, g):
        i0 = int(start * SR)
        i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n:
            L[i0:i1] += g * sig[: i1 - i0]

    def piano(f, dur=2.5):
        lt = np.arange(int(dur * SR)) / SR
        sig = (np.sin(2 * np.pi * f * lt) + 0.45 * np.sin(2 * np.pi * 2 * f * lt) * np.exp(-lt * 2)
               + 0.2 * np.sin(2 * np.pi * 3 * f * lt) * np.exp(-lt * 4) + 0.08 * np.sin(2 * np.pi * 4.01 * f * lt) * np.exp(-lt * 6))
        return sig * np.exp(-lt * 1.6) * np.minimum(1, lt / 0.004)

    # Cmaj7 - Am7 - Fmaj7 - G(sus)  (warm, hopeful)
    prog = [
        (130.8, [261.6, 329.6, 392.0, 493.9]),
        (110.0, [220.0, 261.6, 329.6, 392.0]),
        (87.3, [174.6, 220.0, 261.6, 329.6]),
        (98.0, [196.0, 246.9, 293.7, 392.0]),
    ]
    nb = int(DUR / bar) + 1
    for b in range(nb):
        root, ch = prog[b % 4]
        a0 = b * bar
        # strings pad (slow swell), enters after the intro
        dur = bar + 0.6
        lt = np.arange(int(dur * SR)) / SR
        env = np.minimum(1, lt / 1.2) * np.minimum(1, (dur - lt) / 0.8)
        vib = 1 + 0.003 * np.sin(2 * np.pi * 5 * lt)
        pad = sum(np.sin(2 * np.pi * f * vib * lt) + 0.3 * np.sin(2 * np.pi * f * 2 * vib * lt) for f in ch[:3])
        add(a0, env * pad, 0.018 if a0 < 4 else 0.03)
        # piano: bass note + broken chord
        add(a0, piano(root, 3.5), 0.16)
        pattern = [0, 1, 2, 3, 2, 1, 2, 3] if a0 >= 8.0 else [0, 2, 3, 2]
        step = bar / len(pattern)
        for k, idx in enumerate(pattern):
            add(a0 + k * step, piano(ch[idx] * (2 if (a0 >= 10.5 and k == 3) else 1)), 0.075)
    # melody (sparse, from 10.5 s)
    mel = [(10.5, 659.3), (11.9, 587.3), (12.6, 523.3), (13.8, 493.9), (15.2, 523.3), (16.6, 440.0),
           (17.3, 523.3), (18.7, 587.3), (19.9, 659.3), (21.3, 784.0), (22.0, 659.3), (23.4, 587.3),
           (24.4, 523.3), (25.8, 493.9), (27.6, 523.3)]
    for st, f in mel:
        add(st, piano(f * 2, 3.0), 0.06)
    # gentle shimmer at the curtain reveal
    lt = np.arange(int(2.5 * SR)) / SR
    shimmer = sum(np.sin(2 * np.pi * f * lt) for f in (1046.5, 1318.5, 1568.0)) * np.exp(-lt * 1.5) * np.minimum(1, lt / 0.3)
    add(8.0, shimmer, 0.03)
    # simple stereo reverb: a few feedback delays
    R = L.copy()
    for dly, g in ((0.031, 0.35), (0.053, 0.3), (0.089, 0.25), (0.137, 0.2), (0.211, 0.15)):
        d = int(dly * SR)
        tmp = np.zeros(n)
        tmp[d:] = L[:-d] * g
        R += tmp
    Lr = R.copy()
    Rr = np.roll(R, int(0.012 * SR))
    fadeenv = np.minimum(1, t / 1.0) * np.clip((DUR - t) / 2.0, 0, 1)
    st = np.stack([Lr * fadeenv, Rr * fadeenv], 1)
    st = np.tanh(st * 1.2)
    st = st / np.abs(st).max() * 0.85
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def main():
    if "--frames" in sys.argv:
        for s in sys.argv[sys.argv.index("--frames") + 1:]:
            frame(int(float(s) * FPS)).save(f"v3_{s}.png")
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
