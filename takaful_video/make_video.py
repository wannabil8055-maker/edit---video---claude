"""Animasi kesedaran: Kepentingan Kad Perubatan Takaful.

Menjana video 1080x1920 (9:16) ~1 minit dengan Pillow + ffmpeg.
Guna:  python3 make_video.py [output.mp4]
       python3 make_video.py --preview 3.0 12.5   (simpan frame PNG untuk semakan)
"""
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1080, 1920, 2, 30  # S = supersampling untuk tepi yang licin
HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"
FONTS = {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf",
         "m": "Inter-Medium.otf", "r": "Inter-Regular.otf"}

# Palet warna
BG_TOP, BG_BOT = (238, 249, 246), (204, 237, 230)
INK = (11, 61, 58)
SOFT = (78, 110, 108)
TEAL = (19, 168, 158)
TEAL_D = (10, 112, 106)
TEAL_L = (196, 236, 230)
CORAL = (240, 96, 80)
GOLD = (244, 183, 64)
GOLD_D = (200, 140, 30)
WHITE = (255, 255, 255)
SKIN = (226, 176, 136)
HAIR = (45, 35, 30)

BRAND = "AIA Takaful"
AGENT = "Nabil Rahman"
AGENT_INITIALS = "NR"
PHONE = "011-1188 0895"


@lru_cache(None)
def F(w, size):
    return ImageFont.truetype(FD + FONTS[w], int(size * S))


def X(v):
    return int(round(v * S))


def col(c, a=1.0):
    return (c[0], c[1], c[2], max(0, min(255, int(255 * a))))


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def prog(lt, start, dur):
    return clamp((lt - start) / dur)


def ease(t):  # ease-out cubic
    return 1 - (1 - t) ** 3


def ease_back(t):  # pop dengan sedikit lantunan
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2 if t > 0 else 0.0


# ---------------------------------------------------------------- teks
def wrap(txt, font, maxw):
    lines = []
    for para in txt.split("\n"):
        cur = ""
        for word in para.split(" "):
            test = (cur + " " + word).strip()
            if not cur or font.getlength(test) <= maxw * S:
                cur = test
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text(d, txt, x, y, font, fill, a=1.0, maxw=900, align="center", lh=1.25):
    if a <= 0:
        return y
    lines = wrap(txt, font, maxw)
    for i, line in enumerate(lines):
        w = font.getlength(line)
        px = x * S - w / 2 if align == "center" else x * S
        d.text((px, y * S + i * font.size * lh), line, font=font, fill=col(fill, a))
    return y + len(lines) * font.size * lh / S


def atext(d, txt, x, y, font, fill, lt, start, dur=0.6, **kw):
    e = ease(prog(lt, start, dur))
    if e <= 0:
        return y
    return text(d, txt, x, y + (1 - e) * 40, font, fill, e, **kw)


# ---------------------------------------------------------------- bentuk
def rrect(d, x0, y0, x1, y1, r, fill, a=1.0, outline=None, width=0):
    d.rounded_rectangle((X(x0), X(y0), X(x1), X(y1)), radius=X(r), fill=col(fill, a),
                        outline=col(outline, a) if outline else None, width=X(width))


def card(d, x0, y0, x1, y1, r=36, a=1.0, fill=WHITE):
    rrect(d, x0, y0 + 10, x1, y1 + 10, r, INK, 0.07 * a)
    rrect(d, x0, y0, x1, y1, r, fill, a)


def circle(d, cx, cy, r, fill, a=1.0, outline=None, width=0):
    d.ellipse((X(cx - r), X(cy - r), X(cx + r), X(cy + r)), fill=col(fill, a) if fill else None,
              outline=col(outline, a) if outline else None, width=X(width))


def check_icon(d, cx, cy, r, a=1.0, bg=TEAL):
    circle(d, cx, cy, r, bg, a)
    pts = [(cx - 0.45 * r, cy + 0.02 * r), (cx - 0.12 * r, cy + 0.34 * r), (cx + 0.48 * r, cy - 0.32 * r)]
    d.line([(X(px), X(py)) for px, py in pts], fill=col(WHITE, a), width=X(0.19 * r), joint="curve")


def shield(d, cx, cy, s, a=1.0, fill=TEAL, inner=TEAL_D, cross=True):
    def pts(sz):
        right = [(cx, cy - sz), (cx + 0.85 * sz, cy - 0.68 * sz), (cx + 0.85 * sz, cy)]
        p0, c, p1 = (cx + 0.85 * sz, cy), (cx + 0.80 * sz, cy + 0.70 * sz), (cx, cy + sz)
        for i in range(1, 17):
            t = i / 16
            right.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
                          (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]))
        left = [(2 * cx - px, py) for px, py in reversed(right[1:-1])]
        return [(X(px), X(py)) for px, py in right + left]

    d.polygon(pts(s), fill=col(fill, a))
    d.polygon(pts(s * 0.78), fill=col(inner, a))
    if cross:
        w, l = 0.16 * s, 0.42 * s
        rrect(d, cx - w, cy - l, cx + w, cy + l, w * 0.4, WHITE, a)
        rrect(d, cx - l, cy - w, cx + l, cy + w, w * 0.4, WHITE, a)


def heart(d, cx, cy, s, fill=CORAL, a=1.0):
    r = s * 0.3
    circle(d, cx - r * 0.95, cy - r * 0.4, r, fill, a)
    circle(d, cx + r * 0.95, cy - r * 0.4, r, fill, a)
    d.polygon([(X(cx - 1.86 * r), X(cy - 0.1 * r)), (X(cx + 1.86 * r), X(cy - 0.1 * r)),
               (X(cx), X(cy + 2.1 * r))], fill=col(fill, a))


def sparkle(d, cx, cy, s, a=1.0, fill=GOLD):
    q = s * 0.22
    d.polygon([(X(cx), X(cy - s)), (X(cx + q), X(cy - q)), (X(cx + s), X(cy)), (X(cx + q), X(cy + q)),
               (X(cx), X(cy + s)), (X(cx - q), X(cy + q)), (X(cx - s), X(cy)), (X(cx - q), X(cy - q))],
              fill=col(fill, a))


def coin(d, cx, cy, r=18, a=1.0):
    circle(d, cx, cy, r, GOLD_D, a)
    circle(d, cx, cy - 2, r * 0.86, GOLD, a)


def person(d, cx, cy, sc=1.0, mood="happy", a=1.0, shirt=TEAL, hijab=None, wave_ang=None):
    k = lambda v: v * sc
    hy = cy - k(110)
    if hijab:
        rrect(d, cx - k(100), cy - k(60), cx + k(100), cy + k(160), k(70), shirt, a)
        rrect(d, cx - k(98), cy - k(70), cx + k(98), cy + k(45), k(55), hijab, a)
        d.ellipse((X(cx - k(90)), X(hy - k(90)), X(cx + k(90)), X(hy + k(95))), fill=col(hijab, a))
        d.ellipse((X(cx - k(58)), X(hy - k(54)), X(cx + k(58)), X(hy + k(62))), fill=col(SKIN, a))
    else:
        rrect(d, cx - k(85), cy - k(30), cx + k(85), cy + k(160), k(60), shirt, a)
        d.ellipse((X(cx - k(72)), X(hy - k(78)), X(cx + k(72)), X(hy + k(38))), fill=col(HAIR, a))
        d.ellipse((X(cx - k(64)), X(hy - k(50)), X(cx + k(64)), X(hy + k(68))), fill=col(SKIN, a))
    if wave_ang is not None:
        sx, sy = cx + k(70), cy - k(5)
        hx, hy2 = sx + k(110) * math.cos(wave_ang), sy - k(110) * math.sin(wave_ang)
        d.line([(X(sx), X(sy)), (X(hx), X(hy2))], fill=col(shirt, a), width=X(k(36)))
        circle(d, hx, hy2, k(24), SKIN, a)
    ey = hy + k(2)
    circle(d, cx - k(23), ey, k(7), INK, a)
    circle(d, cx + k(23), ey, k(7), INK, a)
    if mood == "happy":
        circle(d, cx - k(40), ey + k(22), k(10), CORAL, 0.3 * a)
        circle(d, cx + k(40), ey + k(22), k(10), CORAL, 0.3 * a)
        d.arc((X(cx - k(24)), X(ey + k(4)), X(cx + k(24)), X(ey + k(38))), 20, 160,
              fill=col(INK, a), width=max(2, X(k(5))))
    else:
        d.arc((X(cx - k(20)), X(ey + k(30)), X(cx + k(20)), X(ey + k(54))), 200, 340,
              fill=col(INK, a), width=max(2, X(k(5))))
        d.line([(X(cx - k(36)), X(ey - k(22))), (X(cx - k(14)), X(ey - k(16)))], fill=col(INK, a), width=X(k(5)))
        d.line([(X(cx + k(36)), X(ey - k(22))), (X(cx + k(14)), X(ey - k(16)))], fill=col(INK, a), width=X(k(5)))


def pill(d, cx, y, label, font, fg, bg, a=1.0, padx=34, h=72, icon=False):
    w = font.getlength(label) / S + 2 * padx + (h * 0.8 if icon else 0)
    x0 = cx - w / 2
    rrect(d, x0, y, x0 + w, y + h, h / 2, bg, a)
    tx = x0 + padx
    if icon:
        check_icon(d, tx + h * 0.28, y + h / 2, h * 0.28, a)
        tx += h * 0.8
    d.text((X(tx), X(y + h / 2)), label, font=font, fill=col(fg, a), anchor="lm")


# ---------------------------------------------------------------- latar
def _make_bg():
    g = np.linspace(0, 1, H * S)[:, None, None]
    arr = (np.array(BG_TOP) * (1 - g) + np.array(BG_BOT) * g).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, W * S, axis=1), "RGB")


BG = _make_bg()
rng = np.random.default_rng(7)
BUBBLES = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 130), rng.uniform(12, 35), rng.uniform(0, 6))
           for _ in range(9)]


def background(t):
    img = BG.copy()
    d = ImageDraw.Draw(img, "RGBA")
    for x0, y0, r, sp, ph in BUBBLES:
        y = (y0 - t * sp) % (H + 300) - 150
        x = x0 + 30 * math.sin(t * 0.5 + ph)
        circle(d, x, y, r, WHITE, 0.35)
    return img


# ---------------------------------------------------------------- babak
def scene_title(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.8))
    cy = 700 + 10 * math.sin(lt * 2)
    for k in range(2):
        ph = ((lt + k * 0.75) % 1.5) / 1.5
        if lt > 0.6:
            circle(d, 540, cy, 200 + ph * 220, None, outline=TEAL, width=6, a=0.35 * (1 - ph))
    if p > 0:
        shield(d, 540, cy, 200 * p)
    pill(d, 540, 990, "TAHUKAH ANDA?", F("b", 34), TEAL_D, TEAL_L, ease(prog(lt, 0.7, 0.5)))
    y = atext(d, "Kenapa Perlu\nKad Perubatan", 540, 1100, F("xb", 96), INK, lt, 0.9)
    atext(d, "Takaful?", 540, y, F("xb", 110), TEAL, lt, 1.2)
    atext(d, "Fahami dalam 1 minit", 540, 1560, F("m", 46), SOFT, lt, 1.6)


def scene_ali(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    if p > 0:
        person(d, 540, 900, 1.7 * p, "happy", wave_ang=math.radians(60 + 25 * math.sin(lt * 7)))
    for i, (sx, sy, ss) in enumerate([(330, 640, 34), (770, 600, 26), (800, 820, 20)]):
        a = ease(prog(lt, 0.8 + i * 0.2, 0.5))
        sparkle(d, sx, sy, ss * (1 + 0.15 * math.sin(lt * 4 + i)), a)
    atext(d, "Ini Ali.", 540, 1250, F("xb", 96), INK, lt, 0.6)
    atext(d, "Sihat, aktif dan bekerja keras untuk keluarga.", 540, 1390, F("m", 54), SOFT, lt, 1.0, maxw=820)


def ecg_points(x0, x1, yc, amp):
    pts, x = [], x0
    pattern = [(0, 0), (60, 0), (80, -0.15), (100, 0), (125, 0), (140, 0.25), (160, -1.0), (182, 0.55),
               (200, 0), (240, 0), (265, -0.2), (290, 0), (330, 0)]
    while x < x1:
        for dx, dy in pattern:
            if x + dx <= x1:
                pts.append((x + dx, yc + dy * amp))
        x += 330
    return pts


def scene_sick(d, lt, D):
    rrect(d, 0, 0, W, H, 0, CORAL, 0.05 * ease(prog(lt, 0, 0.6)))
    atext(d, "Tapi...", 540, 300, F("xb", 84), CORAL, lt, 0.2)
    atext(d, "sakit datang tanpa amaran.", 540, 410, F("xb", 80), INK, lt, 0.5, maxw=900)
    a = ease(prog(lt, 0.8, 0.5))
    if a > 0:
        card(d, 90, 640, 990, 940, a=a)
        pts = ecg_points(130, 950, 800, 100)
        head = 130 + 820 * ease(prog(lt, 1.0, 2.4))
        vis = [p for p in pts if p[0] <= head]
        if len(vis) >= 2:
            d.line([(X(px), X(py)) for px, py in vis], fill=col(CORAL, a), width=X(9), joint="curve")
            circle(d, vis[-1][0], vis[-1][1], 14, CORAL, a)
            circle(d, vis[-1][0], vis[-1][1], 26 + 6 * math.sin(lt * 10), CORAL, 0.25 * a)
    p = ease_back(prog(lt, 1.2, 0.7))
    if p > 0:
        person(d, 540, 1310, 1.25 * p, "sad", shirt=TEAL)
        drop_y = 1145 + 30 * ((lt * 0.8) % 1)
        circle(d, 640, drop_y, 14 * p, (120, 190, 235), 0.9)
    atext(d, "Demam denggi, kemalangan atau pembedahan kecemasan boleh berlaku pada sesiapa.",
          540, 1600, F("m", 46), SOFT, lt, 1.8, maxw=860)


BILL_ROWS = [("Bilik & wad", 4500), ("Pembedahan", 18000), ("Ubat & ujian makmal", 7500), ("Doktor pakar", 5000)]


def scene_bill(d, lt, D):
    atext(d, "Bil hospital boleh mencecah", 540, 240, F("sb", 58), INK, lt, 0.2)
    atext(d, "puluhan ribu ringgit!", 540, 320, F("xb", 84), CORAL, lt, 0.4)
    e = ease(prog(lt, 0.6, 0.7))
    if e > 0:
        x0, x1, y0, y1 = 170, 910, 490 + (1 - e) * 80, 1090 + (1 - e) * 80
        teeth = []
        n = 16
        for i in range(n + 1):
            tx = x1 - (x1 - x0) * i / n
            teeth.append((tx, y1 + (18 if i % 2 else 0)))
        poly = [(x0, y0), (x1, y0)] + teeth
        d.polygon([(X(px), X(py + 10)) for px, py in poly], fill=col(INK, 0.07 * e))
        d.polygon([(X(px), X(py)) for px, py in poly], fill=col(WHITE, e))
        rrect(d, x0, y0, x1, y0 + 100, 0, TEAL, e)
        d.text((X(540), X(y0 + 50)), "BIL HOSPITAL", font=F("b", 42), fill=col(WHITE, e), anchor="mm")
        cnt = ease(prog(lt, 1.0, 2.6))
        for i, (name, amt) in enumerate(BILL_ROWS):
            ra = e * ease(prog(lt, 1.0 + i * 0.35, 0.4))
            ry = y0 + 150 + i * 80
            d.text((X(x0 + 50), X(ry)), name, font=F("m", 40), fill=col(SOFT, ra), anchor="lm")
            d.text((X(x1 - 50), X(ry)), f"RM {int(amt * cnt):,}", font=F("sb", 40), fill=col(INK, ra), anchor="rm")
        ly = y0 + 150 + 4 * 80 - 20
        d.line([(X(x0 + 50), X(ly)), (X(x1 - 50), X(ly))], fill=col(TEAL_L, e), width=X(4))
        total = sum(a for _, a in BILL_ROWS)
        d.text((X(x0 + 50), X(ly + 65)), "JUMLAH", font=F("b", 44), fill=col(INK, e), anchor="lm")
        d.text((X(x1 - 50), X(ly + 65)), f"RM {int(total * cnt):,}", font=F("xb", 62), fill=col(CORAL, e),
               anchor="rm")
    atext(d, "*Contoh anggaran sahaja", 540, 1125, F("r", 32), SOFT, lt, 1.5)
    base, bw = 1600, 92
    heights = [110, 150, 195, 245, 300]
    tops = []
    for i, hgt in enumerate(heights):
        g = ease(prog(lt, 3.6 + i * 0.15, 0.6))
        bx = 250 + i * 130
        if g > 0:
            rrect(d, bx, base - hgt * g, bx + bw, base, 18, CORAL, 0.35 + 0.13 * i)
        tops.append((bx + bw / 2, base - hgt - 40))
    ta = ease(prog(lt, 4.5, 0.6))
    if ta > 0:
        n = max(2, int(len(tops) * ta + 0.999))
        d.line([(X(px), X(py)) for px, py in tops[:n]], fill=col(INK, ta), width=X(7), joint="curve")
        lx, ly = tops[n - 1]
        d.polygon([(X(lx + 30), X(ly - 22)), (X(lx - 8), X(ly - 18)), (X(lx + 18), X(ly + 16))], fill=col(INK, ta))
    atext(d, "Kos rawatan pula meningkat setiap tahun.", 540, 1650, F("sb", 52), INK, lt, 3.9, maxw=860)


def scene_pool(d, lt, D):
    y = atext(d, "Di sinilah", 540, 220, F("xb", 72), INK, lt, 0.2)
    atext(d, "TAKAFUL membantu", 540, y, F("xb", 80), TEAL, lt, 0.4)
    cx, cy, R = 540, 900, 345
    people = []
    for i in range(6):
        ang = math.radians(-90 + i * 60)
        people.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    sick_i = 1
    phase_b = lt > 4.4
    # wang masuk ke dana
    if 1.2 < lt < 4.3:
        for i, (px, py) in enumerate(people):
            ph = ((lt - 1.2 - i * 0.22) % 1.3) / 1.3
            if lt - 1.2 - i * 0.22 < 0:
                continue
            qx, qy = px + (cx - px) * ease(ph), py + (cy - py) * ease(ph)
            coin(d, qx, qy, 20, 1 - ph ** 4)
    # dana membantu peserta yang sakit
    if phase_b:
        px, py = people[sick_i]
        for k in range(3):
            ph = ((lt - 4.6 - k * 0.4) % 1.2) / 1.2
            if lt - 4.6 - k * 0.4 < 0:
                continue
            qx, qy = cx + (px - cx) * ease(ph), cy + (py - cy) * ease(ph)
            heart(d, qx, qy, 46, TEAL, 1 - ph ** 4)
    p = ease_back(prog(lt, 0.5, 0.7))
    if p > 0:
        circle(d, cx, cy, 175 * p, TEAL_L, 0.8)
        circle(d, cx, cy, 150 * p, TEAL)
        if p > 0.7:
            d.text((X(cx), X(cy - 26)), "DANA", font=F("xb", 46), fill=col(WHITE), anchor="mm")
            d.text((X(cx), X(cy + 28)), "TAKAFUL", font=F("b", 36), fill=col(WHITE), anchor="mm")
    shirts = [CORAL, GOLD, TEAL_D, (120, 110, 200), (90, 160, 90), (230, 130, 60)]
    for i, (px, py) in enumerate(people):
        pa = ease_back(prog(lt, 0.7 + i * 0.1, 0.5))
        if pa <= 0:
            continue
        sick = phase_b and i == sick_i
        if sick:
            circle(d, px, py - 10, 105, CORAL, 0.15 + 0.08 * math.sin(lt * 6))
        person(d, px, py, 0.55 * pa, "sad" if (sick and lt < 5.6) else "happy", shirt=shirts[i],
               hijab=(TEAL_D if i in (2, 4) else None))
    a1 = ease(prog(lt, 1.3, 0.5)) * (1 - ease(prog(lt, 4.0, 0.3)))
    text(d, "Setiap peserta menyumbang (tabarru') ke dalam satu dana bersama.", 540, 1390, F("sb", 50), INK,
         a1, maxw=880)
    a2 = ease(prog(lt, 4.4, 0.5))
    text(d, "Bila seorang peserta sakit, dana ini membantu menanggung kos rawatannya.", 540, 1390 + (1 - a2) * 40,
         F("sb", 50), INK, a2, maxw=880)
    pill(d, 540, 1680, "Saling membantu (ta'awun) & patuh Syariah", F("sb", 36), TEAL_D, WHITE,
         ease(prog(lt, 1.8, 0.5)), h=84, icon=True)


BENEFITS = ["Bilik & makan di hospital", "Kos pembedahan & rawatan", "Ujian makmal & ubat di wad",
            "Kemasukan tanpa tunai di hospital panel", "Rawatan sebelum & selepas masuk wad"]


def hospital(d, cx, by, s, a):
    rrect(d, cx - 170 * s, by - 260 * s, cx + 170 * s, by, 24 * s, WHITE, a)
    rrect(d, cx - 70 * s, by - 340 * s, cx + 70 * s, by - 230 * s, 20 * s, WHITE, a)
    rrect(d, cx - 12 * s, by - 322 * s, cx + 12 * s, by - 248 * s, 5 * s, CORAL, a)
    rrect(d, cx - 37 * s, by - 297 * s, cx + 37 * s, by - 273 * s, 5 * s, CORAL, a)
    for r in range(2):
        for c in range(4):
            if c in (1, 2) and r == 1:
                continue
            wx = cx - 135 * s + c * 75 * s
            wy = by - 220 * s + r * 95 * s
            rrect(d, wx, wy, wx + 45 * s, wy + 55 * s, 8 * s, TEAL_L, a)
    rrect(d, cx - 45 * s, by - 110 * s, cx + 45 * s, by, 10 * s, TEAL, a)


def scene_benefits(d, lt, D):
    atext(d, "Apa yang dilindungi?", 540, 240, F("xb", 78), INK, lt, 0.2)
    atext(d, "Contoh perlindungan kad perubatan takaful:", 540, 350, F("m", 42), SOFT, lt, 0.4, maxw=900)
    for i, label in enumerate(BENEFITS):
        e = ease(prog(lt, 1.0 + i * 0.85, 0.6))
        if e <= 0:
            continue
        off = (1 - e) * 500
        y0 = 470 + i * 165
        card(d, 90 + off, y0, 990 + off, y0 + 135, 32, e)
        check_icon(d, 165 + off, y0 + 67, 36, e)
        text(d, label, 225 + off, y0 + 67 - (52 if len(wrap(label, F("sb", 42), 720)) > 1 else 26),
             F("sb", 42), INK, e, maxw=720, align="left", lh=1.2)
    s = ease_back(prog(lt, 5.4, 0.7))
    if s > 0:
        hospital(d, 540, 1790, 0.85 * s, 1.0)
    atext(d, "*Liputan sebenar bergantung kepada pelan & syarat masing-masing.", 540, 1300, F("r", 32), SOFT, lt,
          5.2, maxw=880)


def _make_card():
    cw, ch = 820, 500
    g = np.linspace(0, 1, X(cw))[None, :, None]
    arr = (np.array(TEAL_D) * (1 - g) + np.array(TEAL) * g).astype(np.uint8)
    arr = np.repeat(arr, X(ch), axis=0)
    face = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(face, "RGBA")
    circle(d, 760, 60, 230, WHITE, 0.08)
    circle(d, 700, 520, 200, WHITE, 0.06)
    shield(d, 720, 110, 58, 1.0, fill=WHITE, inner=TEAL_L, cross=False)
    heart(d, 720, 108, 44, TEAL_D)
    d.text((X(50), X(60)), BRAND.upper(), font=F("b", 32), fill=col(WHITE, 0.85))
    d.text((X(50), X(100)), "KAD PERUBATAN", font=F("xb", 56), fill=col(WHITE))
    rrect(d, 50, 210, 150, 285, 14, GOLD)
    d.line([(X(50), X(247)), (X(150), X(247))], fill=col(GOLD_D), width=X(3))
    d.line([(X(100), X(210)), (X(100), X(285))], fill=col(GOLD_D), width=X(3))
    d.text((X(50), X(330)), "NAMA", font=F("r", 24), fill=col(WHITE, 0.75))
    d.text((X(50), X(360)), "ALI", font=F("b", 40), fill=col(WHITE))
    d.text((X(330), X(330)), "NO. AHLI", font=F("r", 24), fill=col(WHITE, 0.75))
    d.text((X(330), X(360)), "0000 1234 5678", font=F("sb", 40), fill=col(WHITE))
    mask = Image.new("L", face.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, face.size[0] - 1, face.size[1] - 1), radius=X(40), fill=255)
    img = face.convert("RGBA")
    img.putalpha(mask)
    return img


CARD_IMG = None


def scene_card(d, lt, D, img):
    global CARD_IMG
    if CARD_IMG is None:
        CARD_IMG = _make_card()
    atext(d, f"Dengan kad perubatan\n{BRAND}...", 540, 230, F("xb", 66), INK, lt, 0.2, maxw=900)
    e = ease(prog(lt, 0.5, 0.9))
    if e > 0:
        ang = (1 - e) * 14
        cimg = CARD_IMG.rotate(ang, resample=Image.BICUBIC, expand=True) if ang > 0.01 else CARD_IMG
        if e < 1:
            r, g, b, al = cimg.split()
            cimg = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * e))))
        cx, cy = 540, 720 + (1 - e) * 260
        rrect(d, 130, cy - 250 + 16, 950, cy + 250 + 16, 40, INK, 0.12 * e)
        img.paste(cimg, (X(cx) - cimg.size[0] // 2, X(cy) - cimg.size[1] // 2), cimg)
    b = ease_back(prog(lt, 1.8, 0.6))
    if b > 0:
        circle(d, 900, 500, 78 * b, WHITE)
        check_icon(d, 900, 500, 64 * b, 1.0, bg=(46, 170, 90))
    atext(d, "Tunjuk kad di hospital panel, terus dirawat.", 540, 1040, F("sb", 54), INK, lt, 1.6, maxw=860)
    p = ease_back(prog(lt, 2.3, 0.7))
    if p > 0:
        person(d, 540, 1450, 1.1 * p, "happy")
        for i, (sx, sy) in enumerate([(380, 1290), (700, 1270)]):
            sparkle(d, sx, sy, 28 * p * (1 + 0.2 * math.sin(lt * 5 + i)))
    atext(d, "Fokus untuk sembuh, bukan risau bil.", 540, 1690, F("xb", 58), TEAL_D, lt, 2.8, maxw=880)


TIPS = ["Had tahunan & had seumur hidup", "Tempoh menunggu & penyakit sedia ada",
        "Senarai hospital panel berdekatan", "Penerangan lengkap daripada ejen takaful berdaftar"]


def scene_tips(d, lt, D):
    atext(d, "Sebelum mendaftar, semak:", 540, 250, F("xb", 72), INK, lt, 0.2, maxw=900)
    for i, tip in enumerate(TIPS):
        e = ease(prog(lt, 0.9 + i * 0.8, 0.6))
        if e <= 0:
            continue
        y0 = 450 + i * 215
        off = (1 - e) * 60
        card(d, 90, y0 + off, 990, y0 + 180 + off, 32, e)
        circle(d, 175, y0 + 90 + off, 46, TEAL, e)
        d.text((X(175), X(y0 + 90 + off)), str(i + 1), font=F("xb", 50), fill=col(WHITE, e), anchor="mm")
        lines = wrap(tip, F("sb", 44), 700)
        ty = y0 + 90 + off - len(lines) * 44 * 1.22 / 2
        text(d, tip, 255, ty, F("sb", 44), INK, e, maxw=700, align="left", lh=1.22)
    atext(d, "Baca dokumen pelan dengan teliti sebelum menandatangani.", 540, 1380, F("m", 44), SOFT, lt, 4.4,
          maxw=860)
    s = ease_back(prog(lt, 4.8, 0.6))
    if s > 0:
        rrect(d, 430, 1560, 650, 1830, 20, WHITE, 1.0)
        for k in range(5):
            rrect(d, 465, 1610 + k * 40, 615 - (50 if k == 4 else 0), 1626 + k * 40, 8, TEAL_L, 1.0)
        circle(d, 640, 1750, 70 * s, None, outline=TEAL_D, width=16)
        d.line([(X(640 + 50 * s), X(1750 + 50 * s)), (X(640 + 100 * s), X(1750 + 100 * s))],
               fill=col(TEAL_D), width=X(22))


def scene_cta(d, lt, D):
    s = ease(prog(lt, 0.2, 0.8))
    if s > 0:
        shield(d, 540, 790, 330 * (0.8 + 0.2 * s), 0.25 * s, fill=TEAL, inner=TEAL_L, cross=False)
    fam = [(400, 830, 1.0, TEAL, None, 0.4), (680, 840, 0.95, CORAL, TEAL_D, 0.6), (540, 930, 0.62, GOLD, None, 0.8)]
    for fx, fy, sc, sh, hj, st in fam:
        p = ease_back(prog(lt, st, 0.6))
        if p > 0:
            person(d, fx, fy, sc * p, "happy", shirt=sh, hijab=hj)
    hp = ease_back(prog(lt, 1.1, 0.6))
    if hp > 0:
        heart(d, 540, 560 + 8 * math.sin(lt * 3), 90 * hp)
    atext(d, "Sihat itu nikmat.", 540, 1150, F("xb", 88), INK, lt, 1.2)
    atext(d, "Lindungi diri & keluarga hari ini.", 540, 1275, F("sb", 52), TEAL_D, lt, 1.5, maxw=940)


def phone_icon(d, cx, cy, s, a=1.0, c=TEAL):
    rrect(d, cx - 0.32 * s, cy - 0.5 * s, cx + 0.32 * s, cy + 0.5 * s, 0.1 * s, c, a)
    rrect(d, cx - 0.24 * s, cy - 0.38 * s, cx + 0.24 * s, cy + 0.3 * s, 0.04 * s, WHITE, a)
    circle(d, cx, cy + 0.4 * s, 0.05 * s, WHITE, a)


def scene_agent(d, lt, D):
    atext(d, "Nak tahu lebih lanjut?", 540, 220, F("xb", 76), INK, lt, 0.2, maxw=900)
    atext(d, f"Hubungi ejen {BRAND} anda:", 540, 330, F("m", 46), SOFT, lt, 0.4, maxw=900)
    e = ease(prog(lt, 0.6, 0.7))
    if e > 0:
        o = (1 - e) * 80
        card(d, 90, 470 + o, 990, 1250 + o, 44, e)
        rrect(d, 90, 470 + o, 990, 640 + o, 44, TEAL, e)
        d.rectangle((X(90), X(600 + o), X(990), X(640 + o)), fill=col(TEAL, e))
        circle(d, 540, 640 + o, 122, WHITE, e)
        circle(d, 540, 640 + o, 108, TEAL_D, e)
        d.text((X(540), X(640 + o)), AGENT_INITIALS, font=F("xb", 84), fill=col(WHITE, e), anchor="mm")
        d.text((X(540), X(830 + o)), AGENT.upper(), font=F("xb", 66), fill=col(INK, e), anchor="mm")
        d.text((X(540), X(905 + o)), f"Ejen {BRAND}", font=F("sb", 42), fill=col(TEAL, e), anchor="mm")
        d.line([(X(190), X(970 + o)), (X(890), X(970 + o))], fill=col(TEAL_L, e), width=X(4))
        nf = F("xb", 78)
        nw = nf.getlength(PHONE) / S
        nx = 540 + 40
        d.text((X(nx), X(1065 + o)), PHONE, font=nf, fill=col(INK, e), anchor="mm")
        phone_icon(d, nx - nw / 2 - 60, 1065 + o, 80 * (1 + 0.07 * math.sin(lt * 6)), e)
        d.text((X(540), X(1160 + o)), "Telefon / WhatsApp", font=F("m", 40), fill=col(SOFT, e), anchor="mm")
    b = ease_back(prog(lt, 1.6, 0.6))
    if b > 0:
        pf = F("xb", 46)
        pw = (pf.getlength("Hubungi saya hari ini!") / S + 100) * b
        rrect(d, 540 - pw / 2, 1310, 540 + pw / 2, 1420, 55, CORAL, 1.0)
        if b > 0.8:
            d.text((X(540), X(1365)), "Hubungi saya hari ini!", font=pf, fill=col(WHITE), anchor="mm")
    a = ease(prog(lt, 2.4, 0.6))
    if a > 0:
        rrect(d, 90, 1530, 990, 1735, 28, WHITE, 0.75 * a)
        text(d, "Video ini untuk kesedaran umum sahaja dan bukan nasihat kewangan. Perlindungan, terma & syarat "
                "tertakluk kepada pelan dan sijil takaful yang diambil.", 540, 1570, F("r", 32), SOFT, a, maxw=820)


SCENES = [(5.0, scene_title), (5.5, scene_ali), (5.5, scene_sick), (7.5, scene_bill), (7.5, scene_pool),
          (9.5, scene_benefits), (6.5, scene_card), (7.5, scene_tips), (5.5, scene_cta),
          (7.5, scene_agent)]
TOTAL = sum(s[0] for s in SCENES)
N_FRAMES = int(TOTAL * FPS)
FADE = 0.35


def render(t):
    acc = 0.0
    for idx, (dur, fn) in enumerate(SCENES):
        if t < acc + dur or idx == len(SCENES) - 1:
            break
        acc += dur
    lt = t - acc
    bg = background(t)
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    if fn is scene_card:
        fn(d, lt, dur, img)
    else:
        fn(d, lt, dur)
    a = min(1.0, lt / FADE if idx > 0 else 1.0, (dur - lt) / FADE if idx < len(SCENES) - 1 else 1.0)
    if a < 1:
        img = Image.blend(bg, img, clamp(a))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, X(W * t / TOTAL), X(10)), fill=col(TEAL))
    if fn is not scene_agent:
        pill(d, 540, 36, f"{AGENT}  ·  {PHONE}", F("b", 36), TEAL_D, WHITE, 0.9, padx=34, h=76)
    return img.reduce(S)


def render_bytes(i):
    return render(i / FPS).tobytes()


# ---------------------------------------------------------------- muzik
def make_music(path):
    sr = 44100
    n = int(sr * (TOTAL + 0.5))
    t = np.arange(n) / sr
    mf = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    chords = {"C": ([60, 64, 67], 36), "Am": ([57, 60, 64], 33), "F": ([57, 60, 65], 41),
              "G": ([59, 62, 67], 43), "Dm": ([57, 62, 65], 38), "E": ([56, 59, 64], 40)}
    prog_ = ["C", "Am", "F", "Am", "F", "Dm", "E", "Am", "F", "G", "C", "Am", "F", "G", "C", "Am", "F", "G",
             "C", "Am", "F", "G", "C"]
    bar = 3.0
    pad = np.zeros(n)
    arp = np.zeros(n)
    bass = np.zeros(n)
    for b, name in enumerate(prog_):
        notes, root = chords[name]
        t0, t1 = b * bar, (b + 1) * bar + 0.5
        i0, i1 = int(t0 * sr), min(n, int(t1 * sr))
        if i0 >= n:
            break
        tt = t[i0:i1] - t0
        env = np.minimum(1, tt / 0.5) * np.clip((t1 - t0 - tt) / 0.5, 0, 1)
        for m in notes:
            f = mf(m)
            pad[i0:i1] += env * (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt))
        bass[i0:i1] += env * np.sin(2 * np.pi * mf(root) * tt)
        order = [0, 1, 2, 1, 0, 1, 2, 1]
        for k, oi in enumerate(order):
            s0 = t0 + k * bar / 8
            j0, j1 = int(s0 * sr), min(n, int((s0 + 1.2) * sr))
            if j0 >= n:
                continue
            ts = t[j0:j1] - s0
            f = mf(notes[oi] + 12)
            e = np.minimum(1, ts / 0.005) * np.exp(-ts * 5)
            arp[j0:j1] += e * (np.sin(2 * np.pi * f * ts) + 0.25 * np.sin(4 * np.pi * f * ts))
    mix = 0.10 * pad + 0.16 * arp + 0.22 * bass
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.5
    fade_in = np.minimum(1, t / 1.5)
    fade_out = np.clip((TOTAL - t) / 3.0, 0, 1)
    mix *= fade_in * fade_out
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        outdir = os.path.join(HERE, "preview")
        os.makedirs(outdir, exist_ok=True)
        for ts in sys.argv[2:]:
            render(float(ts)).save(os.path.join(outdir, f"frame_{float(ts):05.1f}.png"))
        return
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "takaful_aia_nabil_rahman.mp4")
    music = os.path.join(HERE, "music.wav")
    make_music(music)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", music, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for i, buf in enumerate(pool.imap(render_bytes, range(N_FRAMES), chunksize=6)):
            proc.stdin.write(buf)
            if i % 150 == 0:
                print(f"frame {i}/{N_FRAMES}", flush=True)
    proc.stdin.close()
    proc.wait()
    os.remove(music)
    print("Siap:", out)


if __name__ == "__main__":
    main()
