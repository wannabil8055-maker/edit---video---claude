"""Video promosi animasi rumah setingkat (AA Land Sdn Bhd).

Usage: python3 video_rumah.py [output.mp4]
Requires: numpy, Pillow, ffmpeg. Images are read from ./assets/.
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
DUR = 34.0
N = int(FPS * DUR)
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda p: os.path.join(HERE, "assets", p)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "video_rumah.mp4")

NAVY = (24, 33, 58)
NAVY2 = (38, 52, 88)
GREEN = (59, 181, 74)
WHITE = (255, 255, 255)

FD = "/usr/share/fonts/opentype/inter/"


def F(weight, size):
    try:
        return ImageFont.truetype(FD + f"Inter-{weight}.otf", size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


f_hero = F("ExtraBold", 96)
f_title = F("Bold", 64)
f_sub = F("Medium", 40)
f_tag = F("Bold", 28)
f_stat = F("ExtraBold", 84)
f_statl = F("Medium", 34)
f_phone = F("Bold", 56)


def clamp(x):
    return max(0.0, min(1.0, x))


def ease(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- assets
def hide_logo(img, box=(0, 0, 200, 140), src_dx=200):
    """Clone the neighbouring patch over the corner logo with a feathered edge,
    so it never appears half-cropped during pans (a clean logo is overlaid instead)."""
    x0, y0, x1, y1 = box
    patch = img.crop((x0 + src_dx, y0, x1 + src_dx, y1)).transpose(Image.FLIP_LEFT_RIGHT)
    m = Image.new("L", patch.size, 0)
    ImageDraw.Draw(m).rectangle([0, 0, x1 - x0 - 14, y1 - y0 - 14], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(7))
    out = img.copy()
    out.paste(patch.filter(ImageFilter.GaussianBlur(1.2)), (x0, y0), m)
    return out


tapak = Image.open(A("tapak.jpg")).convert("RGB")
_depan_raw = Image.open(A("render_depan.jpg")).convert("RGB")
depan = hide_logo(_depan_raw)
kiri = hide_logo(Image.open(A("render_kiri.jpg")).convert("RGB"))
kanan = hide_logo(Image.open(A("render_kanan.jpg")).convert("RGB"))
pelan_src = Image.open(A("pelan_lantai.jpg")).convert("RGB")
pelan = pelan_src.crop((150, 280, 800, 900))
logo = _depan_raw.crop((17, 13, 182, 120)).resize((495, 321), Image.LANCZOS)

# bottom gradient for text legibility
_g = np.linspace(0, 1, H, dtype=np.float32)[:, None]
_g = np.clip((_g - 0.45) / 0.55, 0, 1) ** 1.6 * 0.82
SHADE = np.repeat(_g, W, axis=1)[..., None]


def kenburns(img, t, z0, z1, c0, c1):
    """Smooth zoom/pan: zoom z0->z1, centre c0->c1 (fractions of image)."""
    t = ease_io(t)
    z = z0 + (z1 - z0) * t
    cx = c0[0] + (c1[0] - c0[0]) * t
    cy = c0[1] + (c1[1] - c0[1]) * t
    iw, ih = img.size
    bw = min(iw, ih * W / H) / z
    bh = bw * H / W
    x0 = min(max(cx * iw - bw / 2, 0), iw - bw)
    y0 = min(max(cy * ih - bh / 2, 0), ih - bh)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh))


def shade(img, amt=1.0):
    a = np.asarray(img, np.float32)
    a = a * (1 - SHADE * amt) + np.array(NAVY, np.float32) * 0.15 * SHADE * amt
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def blend(a, b, k):
    return Image.blend(a, b, clamp(k))


def text(d, xy, s, f, fill, alpha=1.0, anchor="la"):
    if alpha <= 0:
        return
    d.text(xy, s, font=f, fill=fill + (int(255 * clamp(alpha)),), anchor=anchor)


def lower_third(img, t, t0, t1, tag, line1, line2=None):
    """Animated caption block at bottom-left, visible between t0 and t1."""
    vin = ease((t - t0) / 0.7)
    vout = ease((t1 - t) / 0.5)
    v = vin * vout
    if v <= 0:
        return img
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x, y = 110, H - 300
    dy = (1 - vin) * 40
    # tag pill
    tw = d.textlength(tag, font=f_tag) + 44
    pw = tw * ease((t - t0) / 0.5)
    d.rounded_rectangle([x, y + dy, x + pw, y + 52 + dy], 26, fill=GREEN + (int(255 * v),))
    if pw > tw * 0.8:
        text(d, (x + 22, y + 26 + dy), tag, f_tag, WHITE, v, "lm")
    text(d, (x, y + 80 + dy), line1, f_hero if line2 is None else f_title, WHITE,
         v * ease((t - t0 - 0.15) / 0.6))
    if line2:
        text(d, (x, y + 168 + dy), line2, f_sub, (225, 232, 245), v * ease((t - t0 - 0.35) / 0.6))
    img = img.convert("RGBA")
    img.alpha_composite(ov)
    return img.convert("RGB")


def corner_logo(img, alpha):
    if alpha <= 0:
        return img
    sm = logo.resize((198, 128), Image.LANCZOS).convert("RGBA")
    card = Image.new("RGBA", (222, 152), (255, 255, 255, 255))
    card.paste(sm, (12, 12))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, *card.size], 14, fill=int(240 * alpha))
    img = img.copy()
    img.paste(card, (60, 50), mask)
    return img


# ---------------------------------------------------------------- scenes
def scene_tapak(t):          # 0 .. 6.5
    return kenburns(tapak, t / 6.5, 1.25, 1.55, (0.45, 0.62), (0.52, 0.58))


def scene_depan(t):          # 5.5 .. 13
    return kenburns(depan, (t - 5.5) / 7.5, 1.32, 1.08, (0.55, 0.55), (0.52, 0.55))


def scene_kiri(t):           # 12.2 .. 17.5
    return kenburns(kiri, (t - 12.2) / 5.3, 1.12, 1.25, (0.62, 0.55), (0.45, 0.55))


def scene_kanan(t):          # 16.7 .. 22.2
    return kenburns(kanan, (t - 16.7) / 5.5, 1.25, 1.12, (0.40, 0.55), (0.58, 0.55))


def bg_navy(t):
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    g = np.clip(xx / W * 0.5 + yy / H * 0.5 + 0.08 * np.sin(xx / 260 + t * 0.6), 0, 1)[..., None]
    a = np.array(NAVY, np.float32) * (1 - g) + np.array(NAVY2, np.float32) * g
    return Image.fromarray(a.astype(np.uint8)).resize((W, H), Image.BILINEAR)


STATS = [
    (4, "", "Bilik Tidur"),
    (3, "", "Bilik Air"),
    (1440, " kps", "Jumlah Keluasan"),
    (None, "39' x 38'", "Ukuran Rumah"),
]


def scene_pelan(t):          # 21.5 .. 29.5
    lt = t - 21.5
    img = bg_navy(t)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # title
    text(d, (110, 120), "PELAN LANTAI", f_tag, GREEN, ease(lt / 0.6))
    text(d, (110, 160), "Rumah Setingkat 4 Bilik", f_title, WHITE, ease((lt - 0.2) / 0.6))
    # plan card (left)
    k = ease((lt - 0.3) / 0.9)
    ph = 760
    pw = int(pelan.width * ph / pelan.height)
    s = 0.92 + 0.08 * k
    cw, ch = int((pw + 40) * s), int((ph + 40) * s)
    cx, cy = 110 + cw // 2, 270 + ch // 2 + int((1 - k) * 60)
    img = img.convert("RGBA")
    if k > 0:
        card = Image.new("RGBA", (cw, ch), (255, 255, 255, 255))
        card.paste(pelan.resize((int(pw * s), int(ph * s)), Image.LANCZOS), (int(20 * s), int(20 * s)))
        m = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, cw, ch], 18, fill=int(255 * k))
        shadow = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([40, 50, cw + 40, ch + 50], 18, fill=(0, 0, 0, int(110 * k)))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(shadow, (cx - cw // 2 - 40, cy - ch // 2 - 40))
        card.putalpha(m)
        img.alpha_composite(card, (cx - cw // 2, cy - ch // 2))
    # stats (right)
    sx = 1060
    for i, (num, suf, lab) in enumerate(STATS):
        st = lt - 1.0 - i * 0.55
        v = ease(st / 0.6)
        if v <= 0:
            continue
        y = 290 + i * 175
        dx = (1 - v) * 50
        d.rounded_rectangle([sx + dx, y, sx + dx + 8, y + 130], 4, fill=GREEN + (int(255 * v),))
        if num is None:
            val = suf
        else:
            n = int(round(num * ease(st / 1.0)))
            val = f"{n:,}{suf}"
        text(d, (sx + 40 + dx, y - 6), val, f_stat, WHITE, v)
        text(d, (sx + 42 + dx, y + 92), lab, f_statl, (190, 202, 225), v)
    img.alpha_composite(ov)
    return img.convert("RGB")


def scene_outro(t):          # 29 .. 34
    lt = t - 29.0
    img = bg_navy(t).convert("RGBA")
    # expanding soft green glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r = 200 + 500 * ease(lt / 2.0)
    ImageDraw.Draw(glow).ellipse([W / 2 - r, 380 - r * 0.6, W / 2 + r, 380 + r * 0.6],
                                 fill=GREEN + (int(55 * ease(lt / 1.0)),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    k = ease(lt / 0.8)
    if k > 0:
        s = 0.8 + 0.2 * k
        lw, lh = int(logo.width * 1.0 * s), int(logo.height * 1.0 * s)
        card = Image.new("RGBA", (lw + 48, lh + 48), (255, 255, 255, 255))
        card.paste(logo.resize((lw, lh), Image.LANCZOS), (24, 24))
        m = Image.new("L", card.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, *card.size], 24, fill=int(255 * k))
        card.putalpha(m)
        img.alpha_composite(card, ((W - card.width) // 2, 330 - card.height // 2))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    text(d, (W / 2, 640), "Bina Rumah Impian Anda Bersama Kami", f_title, WHITE,
         ease((lt - 0.5) / 0.6), "mm")
    text(d, (W / 2, 720), "Hubungi kami untuk sebut harga & maklumat lanjut", f_sub,
         (200, 212, 235), ease((lt - 0.8) / 0.6), "mm")
    v = ease((lt - 1.2) / 0.6)
    if v > 0:
        bw = 1000
        d.rounded_rectangle([W / 2 - bw / 2, 790, W / 2 + bw / 2, 900], 55, fill=GREEN + (int(255 * v),))
        text(d, (W / 2, 845), "010-764 6392   |   016-696 6781", f_phone, WHITE, v, "mm")
    img.alpha_composite(ov)
    return img.convert("RGB")


def wipe(a, b, k):
    """Left-to-right reveal of b over a with a glowing edge."""
    k = ease_io(k)
    if k <= 0:
        return a
    if k >= 1:
        return b
    edge = int(-120 + (W + 240) * k)
    xs = np.arange(W, dtype=np.float32)
    # slight diagonal edge
    yy = np.arange(H, dtype=np.float32)[:, None]
    pos = edge + (yy - H / 2) * 0.18
    m = np.clip((pos - xs[None, :]) / 40 + 0.5, 0, 1)[..., None]
    out = np.asarray(a, np.float32) * (1 - m) + np.asarray(b, np.float32) * m
    glow = np.exp(-((xs[None, :] - pos) / 18) ** 2)[..., None]
    out = out + glow * np.array([200, 255, 210], np.float32) * 0.85
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def frame(i):
    t = i / FPS

    if t < 5.5:
        img = scene_tapak(t)
    elif t < 6.7:
        img = wipe(scene_tapak(t), scene_depan(t), (t - 5.5) / 1.2)
    elif t < 12.2:
        img = scene_depan(t)
    elif t < 13.0:
        img = blend(scene_depan(t), scene_kiri(t), ease_io((t - 12.2) / 0.8))
    elif t < 16.7:
        img = scene_kiri(t)
    elif t < 17.5:
        img = blend(scene_kiri(t), scene_kanan(t), ease_io((t - 16.7) / 0.8))
    elif t < 21.5:
        img = scene_kanan(t)
    elif t < 22.3:
        img = blend(scene_kanan(t), scene_pelan(t), ease_io((t - 21.5) / 0.8))
    elif t < 29.0:
        img = scene_pelan(t)
    elif t < 29.8:
        img = blend(scene_pelan(t), scene_outro(t), ease_io((t - 29.0) / 0.8))
    else:
        img = scene_outro(t)

    if t < 22.3:
        img = shade(img, 1.0 if t < 21.5 else 1 - (t - 21.5) / 0.8)
        img = lower_third(img, t, 0.6, 5.3, "SEBELUM", "Dari tapak kosong...")
        img = lower_third(img, t, 6.6, 12.0, "SELEPAS", "...ke rumah impian anda")
        img = lower_third(img, t, 13.0, 16.6, "REKA BENTUK", "Moden & Elegan",
                          "Bumbung biru gelap, dinding putih & batu hiasan")
        img = lower_third(img, t, 17.5, 21.3, "RUMAH SETINGKAT", "Selesa untuk Keluarga",
                          "4 bilik tidur  •  3 bilik air  •  1,440 kps")
        img = corner_logo(img, ease((t - 6.8) / 0.6) * ease((21.5 - t) / 0.4))

    g = ease(t / 0.5) * ease((DUR - t) / 0.8)
    if g < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * g).astype(np.uint8))
    return img


# ---------------------------------------------------------------- audio
def soundtrack(path):
    n = int(SR * DUR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    bpm = 92
    beat = 60 / bpm
    bar = beat * 4
    # C - G - Am - F
    prog = [[261.6, 329.6, 392.0], [196.0, 246.9, 293.7], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6]]
    nb = int(DUR / bar) + 1
    for b in range(nb):
        ch = prog[b % 4]
        a0, a1 = b * bar, b * bar + bar + 0.3
        m = (t >= a0) & (t < a1)
        lt = t[m] - a0
        env = np.minimum(1, lt / 0.5) * np.clip((a1 - t[m]) / 0.6, 0, 1)
        lvl = 0.05 if a0 < 5.5 else 0.07
        for f in ch:
            out[m] += lvl * env * (np.sin(2 * np.pi * f * t[m]) + 0.25 * np.sin(2 * np.pi * f * 2.003 * t[m]))
        # bass from the reveal on
        if a0 >= 5.0:
            out[m] += 0.12 * env * np.sin(2 * np.pi * ch[0] / 2 * t[m])
    # piano-ish plucks (8th notes) — arpeggiate chord tones
    step = beat / 2
    for k, st in enumerate(np.arange(0.2, DUR - 1.0, step)):
        ch = prog[int(st // bar) % 4]
        f = [ch[0] * 2, ch[1] * 2, ch[2] * 2, ch[1] * 2][k % 4]
        m = (t >= st) & (t < st + 0.6)
        lt = t[m] - st
        out[m] += 0.06 * np.exp(-lt * 6) * (np.sin(2 * np.pi * f * lt) + 0.3 * np.sin(4 * np.pi * f * lt))
    # kick + hat after the reveal, pause during outro build
    for bt in np.arange(6.5, DUR - 2.5, beat):
        m = (t >= bt) & (t < bt + 0.35)
        lt = t[m] - bt
        out[m] += 0.32 * np.exp(-lt * 12) * np.sin(2 * np.pi * (50 + 80 * np.exp(-lt * 28)) * lt)
    rng = np.random.default_rng(1)
    for bt in np.arange(6.5 + beat / 2, DUR - 2.5, beat):
        m = (t >= bt) & (t < bt + 0.08)
        lt = t[m] - bt
        out[m] += 0.05 * np.exp(-lt * 60) * rng.standard_normal(m.sum())
    # whoosh at the reveal and before outro
    for wt in (5.3, 28.6):
        m = (t >= wt) & (t < wt + 1.4)
        lt = t[m] - wt
        noise = rng.standard_normal(m.sum())
        noise = np.convolve(noise, np.ones(25) / 25, mode="same")
        out[m] += 0.6 * np.sin(np.pi * lt / 1.4) ** 2 * noise
    fade = np.minimum(1, t / 0.8) * np.clip((DUR - t) / 1.5, 0, 1)
    out *= fade
    out = out / np.abs(out).max() * 0.85
    st = np.stack([out, np.roll(out, 220)], axis=1)  # tiny stereo widening
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def main():
    if "--frames" in sys.argv:          # quick preview stills
        for s in sys.argv[sys.argv.index("--frames") + 1:]:
            frame(int(float(s) * FPS)).save(f"preview_{s}.png")
        return
    wav = OUT.rsplit(".", 1)[0] + "_audio.wav"
    soundtrack(wav)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
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
