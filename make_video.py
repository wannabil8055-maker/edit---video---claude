"""Render a short animated motion-graphics video with a synthesized soundtrack.

Usage: python3 make_video.py [output.mp4]
Requires: numpy, Pillow, ffmpeg on PATH.
"""
import math
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1280, 720, 30, 12.0
N = int(FPS * DUR)
OUT = sys.argv[1] if len(sys.argv) > 1 else "output.mp4"
SR = 44100

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def window(t, a, b, fade=0.5):
    """0..1 visibility for a scene running from a to b with fades."""
    return ease((t - a) / fade) * ease((b - t) / fade)


# --- static assets ---------------------------------------------------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
P = 90
px, py = rng.uniform(0, W, P), rng.uniform(0, H, P)
pvx, pvy = rng.uniform(-30, 30, P), rng.uniform(-40, -10, P)
pr = rng.uniform(1.5, 4, P)

f_big = font(FONT_BOLD, 96)
f_mid = font(FONT_BOLD, 60)
f_small = font(FONT_REG, 34)

PALETTE = [(255, 120, 80), (255, 200, 90), (110, 200, 255), (180, 130, 255)]


def background(t):
    a = 0.35 * t
    c1 = np.array([20 + 15 * math.sin(a), 18, 45 + 20 * math.cos(a)], np.float32)
    c2 = np.array([90 + 40 * math.sin(a + 1), 40, 120 + 30 * math.cos(a * 1.3)], np.float32)
    g = (xx / W * 0.6 + yy / H * 0.4 + 0.15 * np.sin(xx / 180 + t) * np.cos(yy / 140 - t * 0.7))
    g = np.clip(g, 0, 1)[..., None]
    img = c1 * (1 - g) + c2 * g
    return Image.fromarray(img.astype(np.uint8), "RGB")


def centered(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)


def frame(i):
    t = i / FPS
    img = background(t)

    # glow layer: particles + rings
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for k in range(P):
        x = (px[k] + pvx[k] * t) % W
        y = (py[k] + pvy[k] * t) % H
        c = PALETTE[k % 4]
        r = pr[k] * (1 + 0.3 * math.sin(t * 3 + k))
        gd.ellipse([x - r, y - r, x + r, y + r], fill=c)

    # scene 2: pulsing rings (3.5s - 8s)
    v2 = window(t, 3.5, 8.0)
    if v2 > 0:
        for k in range(5):
            ph = (t * 0.6 + k / 5) % 1
            r = 60 + ph * 380
            a = (1 - ph) * v2
            c = tuple(int(ch * a) for ch in PALETTE[k % 4])
            gd.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], outline=c, width=4)

    blurred = glow.filter(ImageFilter.GaussianBlur(6))
    img = Image.fromarray(np.clip(
        np.asarray(img, np.int16) + np.asarray(blurred, np.int16) * 2 + np.asarray(glow, np.int16) // 2,
        0, 255).astype(np.uint8))

    d = ImageDraw.Draw(img, "RGBA")

    # scene 1: title (0 - 3.8s)
    v1 = window(t, 0.2, 3.8)
    if v1 > 0:
        off = (1 - ease((t - 0.2) / 0.8)) * 60
        centered(d, H / 2 - 90 + off, "Create Anything", f_big, (255, 255, 255, int(255 * v1)))
        bw = 520 * ease((t - 0.7) / 0.8)
        d.rectangle([W / 2 - bw / 2, H / 2 + 30, W / 2 + bw / 2, H / 2 + 36],
                    fill=(255, 170, 90, int(255 * v1)))
        centered(d, H / 2 + 60, "an idea becomes motion", f_small, (230, 230, 255, int(230 * v1)))

    # scene 2 text
    if v2 > 0:
        words = ["Imagine.", "Design.", "Animate."]
        for k, wtxt in enumerate(words):
            vk = v2 * ease((t - 3.9 - k * 0.6) / 0.5)
            if vk > 0:
                centered(d, H / 2 - 120 + k * 80, wtxt, f_mid,
                         PALETTE[k] + (int(255 * vk),))

    # scene 3: outro (7.8 - 12s)
    v3 = window(t, 7.8, 12.4)
    if v3 > 0:
        s = ease((t - 7.8) / 1.0)
        centered(d, H / 2 - 80, "Made with Claude", f_big, (255, 255, 255, int(255 * v3)))
        centered(d, H / 2 + 40, "a video rendered entirely from code", f_small,
                 (255, 210, 150, int(230 * v3 * s)))

    # global fade in/out
    g = ease(t / 0.6) * ease((DUR - t) / 0.8)
    if g < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * g).astype(np.uint8))
    return img


def soundtrack(path):
    n = int(SR * DUR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # chord pad: Am - F - C - G, 3s each
    chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [130.8, 196, 261.6], [196, 246.9, 293.7]]
    for ci, ch in enumerate(chords):
        a, b = ci * 3.0, ci * 3.0 + 3.2
        m = (t >= a) & (t < b)
        lt = t[m] - a
        env = np.minimum(1, lt / 0.4) * np.minimum(1, (b - t[m]) / 0.6)
        for f in ch:
            out[m] += 0.08 * env * (np.sin(2 * np.pi * f * t[m]) + 0.3 * np.sin(2 * np.pi * f * 2.005 * t[m]))
    # soft kick on each beat (100 bpm) from 3.5s on
    beat = 0.6
    for bt in np.arange(3.6, DUR - 0.5, beat):
        m = (t >= bt) & (t < bt + 0.3)
        lt = t[m] - bt
        out[m] += 0.35 * np.exp(-lt * 14) * np.sin(2 * np.pi * (55 + 90 * np.exp(-lt * 30)) * lt)
    # arpeggio sparkle
    notes = [440, 523.3, 659.3, 784, 659.3, 523.3]
    for k, st in enumerate(np.arange(0.3, DUR - 1, 0.3)):
        f = notes[k % len(notes)] * (2 if st > 7.8 else 1)
        m = (t >= st) & (t < st + 0.4)
        lt = t[m] - st
        out[m] += 0.05 * np.exp(-lt * 9) * np.sin(2 * np.pi * f * lt)
    fade = np.minimum(1, t / 0.6) * np.minimum(1, (DUR - t) / 1.0)
    out = out * fade
    out = out / max(1e-9, np.abs(out).max()) * 0.8
    data = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main():
    wav = OUT.rsplit(".", 1)[0] + "_audio.wav"
    soundtrack(wav)
    proc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT,
    ], stdin=subprocess.PIPE)
    for i in range(N):
        proc.stdin.write(frame(i).tobytes())
    proc.stdin.close()
    proc.wait()
    import os
    os.remove(wav)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
