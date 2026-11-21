"""Versi menegak (1080x1920) video promosi rumah untuk TikTok / Reels / Shorts.

Usage: python3 video_rumah_tiktok.py [output.mp4] [--frames t1 t2 ...]
Reuses assets, fonts, easing and soundtrack from video_rumah.py.
Layout keeps text inside TikTok's safe zone (clear of the top bar,
the right-hand buttons and the bottom caption area).
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import video_rumah as vr
from video_rumah import (F, GREEN, NAVY, NAVY2, WHITE, clamp, ease, ease_io,
                         tapak, depan, kiri, kanan, pelan, logo)

W, H, FPS = 1080, 1920, 30
DUR = vr.DUR
N = int(FPS * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args and "--frames" not in sys.argv else os.path.join(HERE, "video_rumah_tiktok.mp4")

# photo panel and safe-zone text area
PX, PY, PW, PH = 0, 300, 1080, 1000
TX = 70                     # text left margin
TMAX = W - TX - 150         # keep clear of TikTok's right-side buttons

f_tag = F("Bold", 30)
f_sub = F("Medium", 40)
f_stat = F("ExtraBold", 80)
f_statl = F("Medium", 34)
f_phone = F("Bold", 64)


def fit(d, s, weight, size, maxw):
    while size > 30:
        f = F(weight, size)
        if d.textlength(s, font=f) <= maxw:
            return f
        size -= 4
    return F(weight, size)


def text(d, xy, s, f, fill, alpha=1.0, anchor="la"):
    if alpha > 0:
        d.text(xy, s, font=f, fill=fill + (int(255 * clamp(alpha)),), anchor=anchor)


def kenburns(img, t, z0, z1, c0, c1, w=PW, h=PH):
    t = ease_io(t)
    z = z0 + (z1 - z0) * t
    cx = c0[0] + (c1[0] - c0[0]) * t
    cy = c0[1] + (c1[1] - c0[1]) * t
    iw, ih = img.size
    bh = min(ih, iw * h / w) / z
    bw = bh * w / h
    x0 = min(max(cx * iw - bw / 2, 0), iw - bw)
    y0 = min(max(cy * ih - bh / 2, 0), ih - bh)
    return img.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh))


def bg_navy(t):
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    g = np.clip(xx / W * 0.4 + yy / H * 0.6 + 0.08 * np.sin(yy / 260 + t * 0.6), 0, 1)[..., None]
    a = np.array(NAVY, np.float32) * (1 - g) + np.array(NAVY2, np.float32) * g
    return Image.fromarray(a.astype(np.uint8)).resize((W, H), Image.BILINEAR)


# ---------------------------------------------------------------- photo scenes
def panel_tapak(t):
    return kenburns(tapak, t / 6.5, 1.15, 1.4, (0.42, 0.6), (0.5, 0.58))


def panel_depan(t):
    return kenburns(depan, (t - 5.5) / 7.5, 1.25, 1.05, (0.40, 0.55), (0.55, 0.55))


def panel_kiri(t):
    return kenburns(kiri, (t - 12.2) / 5.3, 1.05, 1.15, (0.65, 0.55), (0.38, 0.55))


def panel_kanan(t):
    return kenburns(kanan, (t - 16.7) / 5.5, 1.15, 1.05, (0.32, 0.55), (0.62, 0.55))


def wipe(a, b, k):
    k = ease_io(k)
    if k <= 0:
        return a
    if k >= 1:
        return b
    w, h = a.size
    xs = np.arange(w, dtype=np.float32)
    yy = np.arange(h, dtype=np.float32)[:, None]
    pos = -120 + (w + 240) * k + (yy - h / 2) * 0.18
    m = np.clip((pos - xs[None, :]) / 40 + 0.5, 0, 1)[..., None]
    out = np.asarray(a, np.float32) * (1 - m) + np.asarray(b, np.float32) * m
    glow = np.exp(-((xs[None, :] - pos) / 18) ** 2)[..., None]
    out = out + glow * np.array([200, 255, 210], np.float32) * 0.85
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def panel_at(t):
    if t < 5.5:
        return panel_tapak(t)
    if t < 6.7:
        return wipe(panel_tapak(t), panel_depan(t), (t - 5.5) / 1.2)
    if t < 12.2:
        return panel_depan(t)
    if t < 13.0:
        return Image.blend(panel_depan(t), panel_kiri(t), ease_io((t - 12.2) / 0.8))
    if t < 16.7:
        return panel_kiri(t)
    if t < 17.5:
        return Image.blend(panel_kiri(t), panel_kanan(t), ease_io((t - 16.7) / 0.8))
    return panel_kanan(t)


# soft fade at the panel's top and bottom edges
_fy = np.arange(PH, dtype=np.float32)
_fm = np.clip(np.minimum(_fy, PH - 1 - _fy) / 70, 0, 1)
PANEL_MASK = Image.fromarray((np.repeat(_fm[:, None], PW, 1) * 255).astype(np.uint8), "L")


def photo_frame(t):
    p = panel_at(t)
    # blurred, darkened copy of the photo fills the whole frame behind it
    bg = p.resize((54, 96), Image.BILINEAR, box=(PW * 0.2, 0, PW * 0.8, PH))
    bg = bg.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    a = np.asarray(bg, np.float32) * 0.45 + np.array(NAVY, np.float32) * 0.35
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    img.paste(p, (PX, PY), PANEL_MASK)
    return img


CAPTIONS = [
    (0.6, 5.3, "SEBELUM", "Dari tapak kosong...", None),
    (6.6, 12.0, "SELEPAS", "...ke rumah impian anda", None),
    (13.0, 16.6, "REKA BENTUK", "Moden & Elegan", "Bumbung biru gelap, dinding\nputih & batu hiasan"),
    (17.5, 21.3, "RUMAH SETINGKAT", "Selesa untuk Keluarga", "4 bilik tidur  •  3 bilik air\n1,440 kps"),
]


def captions(img, t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for t0, t1, tag, line1, line2 in CAPTIONS:
        vin = ease((t - t0) / 0.7)
        v = vin * ease((t1 - t) / 0.5)
        if v <= 0:
            continue
        y = PY + PH + 40
        dy = (1 - vin) * 40
        tw = d.textlength(tag, font=f_tag) + 48
        pw = tw * ease((t - t0) / 0.5)
        d.rounded_rectangle([TX, y + dy, TX + pw, y + 56 + dy], 28, fill=GREEN + (int(255 * v),))
        if pw > tw * 0.8:
            text(d, (TX + 24, y + 28 + dy), tag, f_tag, WHITE, v, "lm")
        fh = fit(d, line1, "ExtraBold", 92, TMAX)
        text(d, (TX, y + 84 + dy), line1, fh, WHITE, v * ease((t - t0 - 0.15) / 0.6))
        if line2:
            d.multiline_text((TX, y + 196 + dy), line2, font=f_sub, spacing=14,
                             fill=(225, 232, 245, int(255 * v * clamp(ease((t - t0 - 0.35) / 0.6)))))
    img = img.convert("RGBA")
    img.alpha_composite(ov)
    return img.convert("RGB")


def top_logo(img, alpha):
    if alpha <= 0:
        return img
    lw, lh = 260, 169
    card = Image.new("RGBA", (lw + 24, lh + 24), (255, 255, 255, 255))
    card.paste(logo.resize((lw, lh), Image.LANCZOS), (12, 12))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, *card.size], 16, fill=int(245 * alpha))
    img = img.copy()
    img.paste(card, ((W - card.width) // 2, 92), m)
    return img


# ---------------------------------------------------------------- plan & outro
STATS = [(4, "", "Bilik Tidur"), (3, "", "Bilik Air"),
         (1440, " kps", "Keluasan"), (None, "39'x38'", "Ukuran")]


def scene_pelan(t):          # 21.5 .. 29.5
    lt = t - 21.5
    img = bg_navy(t).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    text(d, (W / 2, 190), "PELAN LANTAI", f_tag, GREEN, ease(lt / 0.6), "mm")
    text(d, (W / 2, 260), "Rumah Setingkat 4 Bilik", F("Bold", 66), WHITE, ease((lt - 0.2) / 0.6), "mm")
    k = ease((lt - 0.3) / 0.9)
    if k > 0:
        pw = 820
        ph = int(pelan.height * pw / pelan.width)
        s = 0.92 + 0.08 * k
        cw, ch = int((pw + 40) * s), int((ph + 40) * s)
        cx, cy = W // 2, 340 + (ph + 40) // 2 + int((1 - k) * 60)
        card = Image.new("RGBA", (cw, ch), (255, 255, 255, 255))
        card.paste(pelan.resize((int(pw * s), int(ph * s)), Image.LANCZOS), (int(20 * s), int(20 * s)))
        m = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, cw, ch], 18, fill=int(255 * k))
        card.putalpha(m)
        img.alpha_composite(card, (cx - cw // 2, cy - ch // 2))
    # 2x2 stat grid below the plan
    for i, (num, suf, lab) in enumerate(STATS):
        st = lt - 1.0 - i * 0.45
        v = ease(st / 0.6)
        if v <= 0:
            continue
        col, row = i % 2, i // 2
        x = 90 + col * 470
        y = 1220 + row * 180 + (1 - v) * 40
        d.rounded_rectangle([x, y, x + 8, y + 140], 4, fill=GREEN + (int(255 * v),))
        val = suf if num is None else f"{int(round(num * ease(st / 1.0))):,}{suf}"
        text(d, (x + 34, y - 6), val, f_stat, WHITE, v)
        text(d, (x + 36, y + 96), lab, f_statl, (190, 202, 225), v)
    img.alpha_composite(ov)
    return img.convert("RGB")


def scene_outro(t):          # 29 .. 34
    lt = t - 29.0
    img = bg_navy(t).convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r = 200 + 450 * ease(lt / 2.0)
    ImageDraw.Draw(glow).ellipse([W / 2 - r, 560 - r, W / 2 + r, 560 + r],
                                 fill=GREEN + (int(55 * ease(lt / 1.0)),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    k = ease(lt / 0.8)
    if k > 0:
        s = 0.8 + 0.2 * k
        lw, lh = int(720 * s), int(720 * logo.height / logo.width * s)
        card = Image.new("RGBA", (lw + 56, lh + 56), (255, 255, 255, 255))
        card.paste(logo.resize((lw, lh), Image.LANCZOS), (28, 28))
        m = Image.new("L", card.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, *card.size], 28, fill=int(255 * k))
        card.putalpha(m)
        img.alpha_composite(card, ((W - card.width) // 2, 560 - card.height // 2))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ft = F("ExtraBold", 76)
    a1 = ease((lt - 0.5) / 0.6)
    text(d, (W / 2, 930), "Bina Rumah Impian", ft, WHITE, a1, "mm")
    text(d, (W / 2, 1020), "Anda Bersama Kami", ft, WHITE, a1, "mm")
    text(d, (W / 2, 1110), "Hubungi kami untuk sebut harga", f_sub, (200, 212, 235),
         ease((lt - 0.8) / 0.6), "mm")
    for j, ph in enumerate(["010-764 6392", "016-696 6781"]):
        v = ease((lt - 1.2 - j * 0.25) / 0.6)
        if v <= 0:
            continue
        y = 1210 + j * 150 + (1 - v) * 30
        d.rounded_rectangle([W / 2 - 380, y, W / 2 + 380, y + 120], 60, fill=GREEN + (int(255 * v),))
        text(d, (W / 2, y + 60), ph, f_phone, WHITE, v, "mm")
    img.alpha_composite(ov)
    return img.convert("RGB")


def frame(i):
    t = i / FPS
    if t < 22.3:
        img = photo_frame(t)
        img = captions(img, t)
        img = top_logo(img, ease((t - 0.3) / 0.6))
        if t >= 21.5:
            img = Image.blend(img, scene_pelan(t), ease_io((t - 21.5) / 0.8))
    elif t < 29.0:
        img = scene_pelan(t)
    elif t < 29.8:
        img = Image.blend(scene_pelan(t), scene_outro(t), ease_io((t - 29.0) / 0.8))
    else:
        img = scene_outro(t)
    g = ease(t / 0.5) * ease((DUR - t) / 0.8)
    if g < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * g).astype(np.uint8))
    return img


def main():
    if "--frames" in sys.argv:
        for s in sys.argv[sys.argv.index("--frames") + 1:]:
            frame(int(float(s) * FPS)).save(f"tiktok_{s}.png")
        return
    wav = OUT.rsplit(".", 1)[0] + "_audio.wav"
    vr.soundtrack(wav)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
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
