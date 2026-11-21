"""Video TikTok v2 — gaya dinamik: hook, blueprint -> rumah, potongan ikut rentak, CTA.

Usage: python3 video_rumah_v2.py [output.mp4] [--frames t1 t2 ...]
Vertical 1080x1920, 25 s, 120 bpm soundtrack synthesized in code.
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import video_rumah as vr
from video_rumah import F, tapak, depan, kiri, kanan, pelan, logo

W, H, FPS = 1080, 1920, 30
DUR = 25.0
N = int(FPS * DUR)
SR = 44100
BEAT = 0.5
HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args and "--frames" not in sys.argv else os.path.join(HERE, "video_rumah_tiktok_v2.mp4")

YELLOW = (255, 210, 63)
INK = (16, 20, 34)
WHITE = (255, 255, 255)
BP = (14, 52, 104)          # blueprint blue
BPL = (120, 190, 255)       # blueprint line
GREEN = vr.GREEN


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def back(t, s=2.2):
    """Ease-out with overshoot (pop)."""
    t = clamp(t)
    t -= 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


# ---------------------------------------------------------------- image helpers
def place(img, s, fx, fy, bg=None, size=(W, H)):
    """Draw img scaled by s (screen px per source px) so that source point
    (fx, fy) lands at the canvas centre. Only the visible part is resampled."""
    cw, ch = size
    iw, ih = img.size
    x0, y0 = fx - cw / 2 / s, fy - ch / 2 / s
    x1, y1 = fx + cw / 2 / s, fy + ch / 2 / s
    sx0, sy0, sx1, sy1 = max(x0, 0), max(y0, 0), min(x1, iw), min(y1, ih)
    canvas = bg.copy() if bg is not None else Image.new("RGB", size, INK)
    if sx1 <= sx0 or sy1 <= sy0:
        return canvas
    dx0, dy0 = (sx0 - x0) * s, (sy0 - y0) * s
    dw, dh = int(round((sx1 - sx0) * s)), int(round((sy1 - sy0) * s))
    if dw < 1 or dh < 1:
        return canvas
    part = img.resize((dw, dh), Image.BICUBIC, box=(sx0, sy0, sx1, sy1))
    if part.mode == "RGBA":
        canvas.paste(part, (int(round(dx0)), int(round(dy0))), part)
    else:
        canvas.paste(part, (int(round(dx0)), int(round(dy0))))
    return canvas


def fullbleed(img, s, fx, fy):
    """Like place() but clamps the focus so the frame is always filled."""
    iw, ih = img.size
    s = max(s, H / ih, W / iw)
    hw, hh = W / 2 / s, H / 2 / s
    fx = min(max(fx, hw), iw - hw)
    fy = min(max(fy, hh), ih - hh)
    out = place(img, s, fx, fy)
    return out.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.hypot((_xx - W / 2) / (W * 0.62), (_yy - H / 2) / (H * 0.62))
VIGNETTE = np.clip(1.10 - 0.30 * _r ** 2, 0.6, 1.06)[..., None].astype(np.float32)
LEAK = np.zeros((H, W, 3), np.float32)
for (cx, cy, rad, col) in [(W * 1.05, H * 0.05, 850, (255, 170, 70)),
                           (-W * 0.15, H * 0.9, 600, (255, 140, 60))]:
    d = np.hypot(_xx - cx, _yy - cy) / rad
    LEAK += np.exp(-d ** 2)[..., None] * np.array(col, np.float32) / 255
LEAK = np.clip(LEAK, 0, 1)
del _yy, _xx, _r


def grade(img, t, leak=0.0):
    a = np.asarray(img, np.float32) / 255
    a = np.clip((a - 0.5) * 1.1 + 0.53, 0, 1)            # contrast + lift
    lum = a.mean(axis=2, keepdims=True)
    a = np.clip(lum + (a - lum) * 1.22, 0, 1)              # saturation
    a = a * np.array([1.03, 1.0, 0.97], np.float32)        # warm
    if leak > 0:
        k = leak * (0.35 + 0.15 * math.sin(t * 1.7))
        a = 1 - (1 - a) * (1 - LEAK * k)                   # screen
    a = a * VIGNETTE
    rng = np.random.default_rng(int(t * 1000))
    a += rng.normal(0, 0.018, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- text
_cache = {}


def word_img(s, size, color=WHITE, weight="Black", box=None, pad=(26, 10)):
    """Rendered text (optionally on a coloured box) with a soft drop shadow."""
    key = (s, size, color, weight, box)
    if key in _cache:
        return _cache[key]
    f = F(weight, size)
    l, t, r, b = f.getbbox(s)
    tw, th = r - l, b - t
    px, py = pad if box else (0, 0)
    m = 40
    img = Image.new("RGBA", (tw + 2 * px + 2 * m, th + 2 * py + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box:
        d.rounded_rectangle([m, m, m + tw + 2 * px, m + th + 2 * py], 14, fill=box + (255,))
    else:
        d.text((m - l, m - t), s, font=f, fill=color + (255,))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.putalpha(img.getchannel("A").point(lambda v: int(v * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, 8))
    out.alpha_composite(img)
    if box:
        ImageDraw.Draw(out).text((m + px - l, m + py - t), s, font=f, fill=color + (255,))
    _cache[key] = out
    return out


def pop(canvas, wimg, cx, cy, lt, dur=0.35, slide=0, fade_out=None):
    """Paste word image centred at (cx, cy) with a scale-pop entrance."""
    if lt < 0:
        return
    k = back(lt / dur)
    a = clamp(lt / (dur * 0.5))
    if fade_out is not None:
        a *= clamp(1 - fade_out)
    if a <= 0:
        return
    sc = max(0.05, 0.4 + 0.6 * k)
    w, h = int(wimg.width * sc), int(wimg.height * sc)
    im = wimg.resize((w, h), Image.BICUBIC) if sc != 1 else wimg
    if a < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    canvas.alpha_composite(im, (int(cx - w / 2 + slide * (1 - ease(lt / dur))), int(cy - h / 2)))


def chip(canvas, label, lt, y=1330):
    """Yellow caption chip that slides in from the left."""
    if lt < 0:
        return
    wimg = word_img(label, 58, INK, "Black", box=YELLOW, pad=(28, 16))
    x = 70 - 40 + (1 - back(lt / 0.4, 1.6)) * -700
    canvas.alpha_composite(wimg, (int(x), int(y)))


def flash(img, k):
    if k <= 0:
        return img
    return Image.blend(img, Image.new("RGB", img.size, WHITE), clamp(k))


# ---------------------------------------------------------------- blueprint assets
def make_grid():
    g = Image.new("RGB", (W, H), BP)
    d = ImageDraw.Draw(g)
    for x in range(0, W, 45):
        d.line([(x, 0), (x, H)], fill=(30, 72, 128) if x % 225 else (48, 96, 160), width=1)
    for y in range(0, H, 45):
        d.line([(0, y), (W, y)], fill=(30, 72, 128) if y % 225 else (48, 96, 160), width=1)
    a = np.asarray(g, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / W, (yy - H / 2) / H)
    a *= np.clip(1.15 - 0.9 * r, 0.4, 1.1)[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


GRID = make_grid()


def make_lines(img):
    g = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(1.0)), np.float32)
    gx = np.zeros_like(g)
    gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1] = g[2:] - g[:-2]
    m = np.hypot(gx, gy)
    th = np.percentile(m, 87)
    e = np.clip((m - th) / (th * 1.2), 0, 1)
    return e


LINES = make_lines(depan)             # 607 x 1080 float mask
HOUSE_Y = 760                         # top of the framed house on screen
IH, IW = LINES.shape


def blueprint_frame(t, draw_k, color_k, scale=1.0, focus=None):
    """Grid + line drawing revealed left->right (draw_k) and colour flooding
    in radially (color_k). scale/focus zoom the framed house."""
    lt_cx = IW / 2
    # line layer as RGBA
    xs = np.arange(IW, dtype=np.float32)
    sweep = draw_k * (IW + 160) - 80
    rev = np.clip((sweep - xs) / 60, 0, 1)[None, :]
    a = LINES * rev
    glow = np.exp(-((xs - sweep) / 14) ** 2)[None, :] * 0.9 * (draw_k < 1)
    rgb = np.zeros((IH, IW, 3), np.float32)
    rgb[:] = np.array(BPL, np.float32)
    line_rgba = np.dstack([rgb, np.clip(a + glow * 0.0, 0, 1) * 255]).astype(np.uint8)
    house = Image.fromarray(line_rgba, "RGBA")
    if draw_k < 1:
        gl = np.dstack([np.full((IH, IW, 3), 255, np.float32), glow.repeat(IH, 0) * 200]).astype(np.uint8)
        house.alpha_composite(Image.fromarray(gl, "RGBA"))
    if color_k > 0:
        yy, xx = np.mgrid[0:IH, 0:IW].astype(np.float32)
        rad = color_k * 1.25 * math.hypot(IW / 2, IH / 2)
        dist = np.hypot(xx - IW / 2, yy - IH * 0.55)
        m = np.clip((rad - dist) / 40, 0, 1)
        ring = np.exp(-((dist - rad) / 10) ** 2) * (color_k < 1)
        col = np.asarray(depan, np.float32)
        base = np.asarray(house, np.float32)
        out_rgb = base[..., :3] * (1 - m[..., None]) + col * m[..., None]
        out_rgb += ring[..., None] * 255
        out_a = np.maximum(base[..., 3], m * 255)
        house = Image.fromarray(np.dstack([out_rgb.clip(0, 255), out_a]).astype(np.uint8), "RGBA")
    # compose on the grid, zoomed
    fx, fy = focus if focus else (IW / 2, IH / 2)
    canvas = GRID
    sc_bg = 1 + (scale - 1) * 0.15
    if sc_bg != 1:
        canvas = place(GRID, sc_bg, W / 2, H / 2)
    # the framed house sits with its centre at (W/2, HOUSE_Y + IH/2) at scale 1
    cy_screen = HOUSE_Y + IH / 2
    shift = (H / 2 - cy_screen) / scale
    out = place(house, scale, fx, fy + shift, bg=canvas)
    return out


def dims_overlay(canvas, lt):
    """Dimension line under the drawing, like an architect's sheet."""
    if lt < 0:
        return
    k = ease(lt / 0.8)
    d = ImageDraw.Draw(canvas)
    y = HOUSE_Y + IH + 50
    x0, x1 = 90, 90 + (W - 180) * k
    c = BPL + (230,)
    d.line([(x0, y), (x1, y)], fill=c, width=3)
    d.line([(x0, y - 18), (x0, y + 18)], fill=c, width=3)
    if k >= 1:
        d.line([(x1, y - 18), (x1, y + 18)], fill=c, width=3)
    if k > 0.5:
        wimg = word_img("39'-0\"  [11.9 m]", 38, BPL, "Bold")
        tmp = wimg.copy()
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * clamp((k - 0.5) * 2))))
        canvas.alpha_composite(tmp, (int(W / 2 - wimg.width / 2), int(y + 4)))


# ---------------------------------------------------------------- shot list (fast cuts)
# (start, end, image, s0, s1, (fx0, fy0), (fx1, fy1), caption)
SHOTS = [
    (9.0, 10.5, depan, 3.2, 3.35, (260, 330), (820, 330), "FASAD MODEN"),
    (10.5, 11.5, depan, 3.6, 3.4, (610, 190), (610, 230), "DETAIL ELEGAN"),
    (11.5, 12.5, depan, 3.5, 3.3, (300, 420), (330, 380), "BATU HIASAN"),
    (12.5, 14.5, kiri, 3.2, 3.3, (250, 330), (800, 340), "ANJUNG LUAS"),
    (14.5, 15.5, kanan, 3.6, 3.35, (580, 400), (560, 380), "TINGKAP BESAR"),
    (15.5, 17.0, kanan, 3.2, 3.3, (820, 330), (300, 330), "RUMAH SETINGKAT"),
]


def shot_frame(t):
    for (a, b, img, s0, s1, f0, f1, cap) in SHOTS:
        if a <= t < b:
            lt = t - a
            k = ease_io(lt / (b - a))
            punch = 1 + 0.14 * (1 - ease(lt / 0.28))
            s = (s0 + (s1 - s0) * k) * punch
            fx = f0[0] + (f1[0] - f0[0]) * k
            fy = f0[1] + (f1[1] - f0[1]) * k
            fr = fullbleed(img, s, fx, fy)
            fr = grade(fr, t, leak=0.8)
            fr = flash(fr, 0.55 * (1 - lt / 0.12))
            c = fr.convert("RGBA")
            chip(c, cap, lt - 0.08)
            return c
    return None


# ---------------------------------------------------------------- scenes
def scene_hook(t):           # 0 .. 3
    s = 1.0 * (H / tapak.height) * (1.0 + 0.10 * ease_io(t / 3.0))
    fr = fullbleed(tapak, s, 1150 + 60 * t, 1000)
    fr = grade(fr, t, leak=0.5)
    c = fr.convert("RGBA")
    pop(c, word_img("DARI", 96, WHITE), W / 2, 520, t - 0.25)
    pop(c, word_img("TANAH", 190, WHITE), W / 2, 680, t - 0.5)
    pop(c, word_img("KOSONG", 190, INK, box=YELLOW, pad=(30, 12)), W / 2, 880, t - 0.75)
    pop(c, word_img("...", 120, WHITE), W / 2, 1040, t - 1.5)
    # zoom-out exit
    if t > 2.75:
        k = ease((t - 2.75) / 0.25)
        c = c.resize((int(W * (1 + 0.4 * k)), int(H * (1 + 0.4 * k))), Image.BILINEAR)
        c = c.crop(((c.width - W) // 2, (c.height - H) // 2, (c.width - W) // 2 + W, (c.height - H) // 2 + H))
    return c


def scene_blueprint(t):      # 3 .. 9
    lt = t - 3.0
    draw_k = ease_io((lt - 0.3) / 2.8)
    color_k = ease((t - 7.0) / 0.55)
    scale = 1.0
    focus = None
    if t >= 7.6:
        z = ease_io((t - 7.6) / 1.4)
        scale = 1.0 + (H / IH - 1.0) * z ** 1.6
        focus = (IW / 2 + 40 * z, IH / 2 - 20 * z)
    fr = blueprint_frame(t, draw_k, color_k, scale, focus)
    fr = grade(fr, t, leak=0.6 * color_k)
    fr = flash(fr, 0.85 * (1 - (lt / 0.25)) if lt < 0.25 else 0)
    fr = flash(fr, 0.9 * (1 - (t - 7.0) / 0.35) if 7.0 <= t < 7.35 else 0)
    c = fr.convert("RGBA")
    if t < 7.0:
        fo = clamp((t - 6.7) / 0.3)
        pop(c, word_img("REKA BENTUK", 92, WHITE), W / 2, 380, lt - 0.2, fade_out=fo)
        pop(c, word_img("EKSKLUSIF", 92, INK, box=YELLOW), W / 2, 500, lt - 0.45, fade_out=fo)
        if scale == 1.0:
            dims_overlay(c, lt - 2.6)
    else:
        lt2 = t - 7.0
        fo = clamp((t - 8.7) / 0.3)
        pop(c, word_img("JADI RUMAH", 120, WHITE), W / 2, 400, lt2 - 0.05, fade_out=fo)
        pop(c, word_img("IMPIAN!", 150, INK, box=YELLOW, pad=(34, 12)), W / 2, 560, lt2 - 0.3, fade_out=fo)
    return c


STATS = [("4", "BILIK TIDUR"), ("3", "BILIK AIR"), ("1,440", "KAKI PERSEGI"), ("39'x38'", "UKURAN RUMAH")]


def scene_specs(t):          # 17 .. 21
    lt = t - 17.0
    c = place(GRID, 1.0 + 0.03 * lt, W / 2, H / 2).convert("RGBA")
    pop(c, word_img("PELAN LANTAI", 70, YELLOW), W / 2, 230, lt - 0.0, dur=0.3)
    # plan card
    k = back(lt / 0.45, 1.4)
    pw = 760
    ph = int(pelan.height * pw / pelan.width)
    s = 0.6 + 0.4 * k
    cw, chh = int((pw + 30) * s), int((ph + 30) * s)
    if cw > 10:
        card = Image.new("RGBA", (cw, chh), (255, 255, 255, 255))
        card.paste(pelan.resize((max(1, int(pw * s)), max(1, int(ph * s))), Image.LANCZOS), (int(15 * s), int(15 * s)))
        m = Image.new("L", (cw, chh), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, cw, chh], 16, fill=int(255 * clamp(lt / 0.2)))
        card.putalpha(m)
        c.alpha_composite(card, (int(W / 2 - cw / 2), int(300 + (ph + 30) / 2 - chh / 2)))
    # stats slam in on the beat, 2x2 grid
    for i, (num, lab) in enumerate(STATS):
        st = lt - 0.5 - i * BEAT
        if st < 0:
            continue
        col, row = i % 2, i // 2
        cx = W / 2 + (col - 0.5) * 470
        cy = 1150 + row * 210
        sl = 1 + 0.6 * (1 - ease(st / 0.22))
        wn = word_img(num, 104, YELLOW if i < 2 else WHITE)
        wn2 = wn.resize((int(wn.width * sl), int(wn.height * sl)), Image.BICUBIC)
        c.alpha_composite(wn2, (int(cx - wn2.width / 2), int(cy - wn2.height / 2)))
        wl = word_img(lab, 36, (200, 220, 245), "Bold")
        c.alpha_composite(wl, (int(cx - wl.width / 2), int(cy + 50)))
    fr = grade(c.convert("RGB"), t, leak=0.3)
    # tiny shake on each slam
    for i in range(4):
        st = lt - 0.5 - i * BEAT
        if 0 <= st < 0.15:
            dx = int(10 * math.sin(st * 120) * (1 - st / 0.15))
            fr = Image.fromarray(np.roll(np.asarray(fr), dx, axis=1))
    fr = flash(fr, 0.5 * (1 - lt / 0.15))
    return fr.convert("RGBA")


_cta_bg = depan.resize((W, int(W * IH / IW)), Image.LANCZOS)
CTA_BG = fullbleed(depan, H / IH, 540, IH / 2).filter(ImageFilter.GaussianBlur(14))
CTA_BG = Image.fromarray((np.asarray(CTA_BG, np.float32) * 0.42 + np.array(INK) * 0.25).clip(0, 255).astype(np.uint8))


def scene_cta(t):            # 21 .. 25
    lt = t - 21.0
    c = place(CTA_BG, 1.0 + 0.04 * lt, W / 2, H / 2).convert("RGBA")
    # logo card pop
    k = back(lt / 0.5, 1.8)
    if k > 0.02:
        lw = int(640 * k)
        lh = int(lw * logo.height / logo.width)
        card = Image.new("RGBA", (lw + 44, lh + 44), (255, 255, 255, 255))
        card.paste(logo.resize((max(1, lw), max(1, lh)), Image.LANCZOS), (22, 22))
        m = Image.new("L", card.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, *card.size], 26, fill=255)
        card.putalpha(m)
        c.alpha_composite(card, (int(W / 2 - card.width / 2), int(470 - card.height / 2)))
    pop(c, word_img("JOM BINA", 110, WHITE), W / 2, 820, lt - 0.45)
    pop(c, word_img("RUMAH IMPIAN", 110, INK, box=YELLOW, pad=(28, 10)), W / 2, 960, lt - 0.7)
    pop(c, word_img("ANDA!", 110, WHITE), W / 2, 1100, lt - 0.95)
    for j, num in enumerate(["010-764 6392", "016-696 6781"]):
        st = lt - 1.4 - j * 0.25
        if st < 0:
            continue
        pulse = 1 + 0.035 * math.sin(max(0, lt - 2.0) * 2 * math.pi / (BEAT * 2))
        wimg = word_img(num, 84, WHITE, "ExtraBold", box=GREEN, pad=(64, 28))
        sc = back(st / 0.4) * pulse
        im = wimg.resize((max(1, int(wimg.width * sc)), max(1, int(wimg.height * sc))), Image.BICUBIC)
        c.alpha_composite(im, (int(W / 2 - im.width / 2), int(1300 + j * 185 - im.height / 2)))
    fr = grade(c.convert("RGB"), t, leak=0.5)
    fr = flash(fr, 0.5 * (1 - lt / 0.15))
    return fr


def frame(i):
    t = i / FPS
    if t < 3.0:
        img = scene_hook(t)
    elif t < 9.0:
        img = scene_blueprint(t)
    elif t < 17.0:
        img = shot_frame(t)
    elif t < 21.0:
        img = scene_specs(t)
    else:
        img = scene_cta(t)
    img = img.convert("RGB")
    g = ease(t / 0.25) * ease((DUR - t) / 0.6)
    if g < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * g).astype(np.uint8))
    return img


# ---------------------------------------------------------------- music (120 bpm)
def soundtrack(path):
    n = int(SR * DUR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    rng = np.random.default_rng(3)

    def add(start, sig, gain=1.0):
        i0 = int(start * SR)
        i1 = min(n, i0 + len(sig))
        if i0 < n:
            L[i0:i1] += gain * sig[: i1 - i0]

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
        nz = nz - np.convolve(nz, np.ones(3) / 3, mode="same")
        return nz * np.exp(-lt * 70)

    def tone(f, dur, decay=4.0, harm=(1, 0.5, 0.25)):
        lt = np.arange(int(dur * SR)) / SR
        sig = sum(a * np.sin(2 * np.pi * f * (k + 1) * lt) for k, a in enumerate(harm))
        return sig * np.exp(-lt * decay) * np.minimum(1, lt / 0.005)

    # chords: Am F C G (one bar = 2 s)
    prog = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (130.8, 196.0, 261.6), (196.0, 246.9, 293.7)]
    bar = BEAT * 4

    # pads throughout (low-passed by mixing few harmonics)
    for b in range(int(DUR / bar) + 1):
        ch = prog[b % 4]
        a0 = b * bar
        dur = bar + 0.2
        lt = np.arange(int(dur * SR)) / SR
        env = np.minimum(1, lt / 0.3) * np.minimum(1, (dur - lt) / 0.3)
        g = 0.05 if a0 < 7 else 0.07
        for f in ch:
            add(a0, env * (np.sin(2 * np.pi * f * lt) + 0.2 * np.sin(2 * np.pi * f * 2.01 * lt)), g)

    # pluck arp (16ths in the hook, 8ths elsewhere)
    for k, st in enumerate(np.arange(0.0, DUR - 0.6, BEAT / 2)):
        if 3.0 <= st < 7.0 and k % 2:
            continue
        ch = prog[int(st // bar) % 4]
        f = (ch[0] * 2, ch[2] * 2, ch[1] * 2, ch[2] * 4)[k % 4]
        add(st, tone(f, 0.4, 9, (1, 0.3)), 0.07)

    # hook: light kick on beats
    for st in np.arange(0.0, 3.0, BEAT):
        add(st, kick(), 0.35)
    # blueprint build: snare roll accelerating + riser
    st = 5.0
    while st < 7.0:
        add(st, clap(), 0.10 + 0.12 * (st - 5) / 2)
        st += BEAT / 2 if st < 6.0 else (BEAT / 4 if st < 6.5 else BEAT / 8)
    lt = np.arange(int(2.0 * SR)) / SR
    riser = rng.standard_normal(len(lt))
    riser = np.convolve(riser, np.ones(8) / 8, mode="same") * (lt / 2.0) ** 2
    riser += 0.4 * np.sin(2 * np.pi * (200 * lt + 400 * lt ** 2)) * (lt / 2.0) ** 2
    add(5.0, riser, 0.35)
    # drop impact at 7.0
    lt = np.arange(int(1.6 * SR)) / SR
    boom = np.sin(2 * np.pi * (40 * lt + 60 * (1 - np.exp(-lt * 6)) / 6)) * np.exp(-lt * 2.5)
    add(7.0, boom, 0.9)
    nz = rng.standard_normal(len(lt)) * np.exp(-lt * 5)
    add(7.0, np.convolve(nz, np.ones(4) / 4, mode="same"), 0.25)

    # main beat 7.0 .. 21 and CTA 21 .. 24
    for st in np.arange(7.0, DUR - 1.0, BEAT):
        add(st, kick(), 0.6)
        if int(round((st - 7.0) / BEAT)) % 2 == 1:
            add(st, clap(), 0.22)
        add(st + BEAT / 2, hat(), 0.12)
    # bass (offbeat pumping)
    for st in np.arange(7.0, DUR - 1.0, BEAT / 2):
        ch = prog[int(st // bar) % 4]
        f = ch[0] / 2 if ch[0] > 160 else ch[0]
        add(st + 0.0, tone(f, BEAT / 2, 6, (1, 0.6, 0.3)), 0.16)
    # whoosh/impact on every shot cut and section change
    for ct in [3.0, 17.0, 21.0] + [s[0] for s in SHOTS[1:]]:
        lt = np.arange(int(0.45 * SR)) / SR
        w = rng.standard_normal(len(lt))
        w = np.convolve(w, np.ones(12) / 12, mode="same") * np.sin(np.pi * lt / 0.45) ** 2
        add(ct - 0.25, w, 0.35)
    # sidechain feel: duck everything a bit right after each kick in the drop
    duck = np.ones(n)
    for st in np.arange(7.0, DUR - 1.0, BEAT):
        i0 = int(st * SR)
        lt = np.arange(int(0.25 * SR)) / SR
        seg = 1 - 0.35 * np.exp(-lt * 12)
        duck[i0:i0 + len(seg)] = np.minimum(duck[i0:i0 + len(seg)], seg[: n - i0])
    L *= duck
    fade = np.minimum(1, t / 0.05) * np.clip((DUR - t) / 1.2, 0, 1)
    L *= fade
    L = np.tanh(L * 1.4) / np.tanh(1.4)               # soft limiter
    L = L / np.abs(L).max() * 0.9
    st = np.stack([L, np.roll(L, 180)], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def main():
    if "--frames" in sys.argv:
        for s in sys.argv[sys.argv.index("--frames") + 1:]:
            frame(int(float(s) * FPS)).save(f"v2_{s}.png")
        return
    wav = OUT.rsplit(".", 1)[0] + "_audio.wav"
    soundtrack(wav)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "25", "-pix_fmt", "yuv420p",
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
