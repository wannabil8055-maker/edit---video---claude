"""Hasilkan versi 16:9 (Facebook/YouTube) + poster/thumbnail untuk semua video berjenama ejen.

Video 9:16 diletak di tengah, dengan panel tajuk (kiri) & kad ejen (kanan).
Output:  16x9/<nama>_16x9.mp4
         poster/<nama>_cover_9x16.png   (cover TikTok/Reels)
         poster/<nama>_thumb_16x9.png   (thumbnail YouTube/Facebook)
Guna:    python3 export_16x9.py
"""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from make_video import (F, X, S, col, text, wrap, rrect, circle, INK, SOFT, TEAL, TEAL_D, TEAL_L, WHITE, BG_TOP,
                        BG_BOT, AGENT, AGENT_INITIALS, PHONE, BRAND)
from make_video import phone_icon

HERE = os.path.dirname(os.path.abspath(__file__))
W2, H2 = 1920, 1080
VX = (W2 - 608) // 2  # kedudukan video 608x1080 di tengah

VIDEOS = [
    ("takaful_aia_nabil_rahman_merah", "KAD PERUBATAN", "Kenapa Perlu Kad Perubatan Takaful?"),
    ("variasi_1_mitos_fakta", "KAD PERUBATAN", "Mitos vs Fakta Kad Perubatan"),
    ("variasi_2_tanpa_vs_dengan", "KAD PERUBATAN", "Tanpa Kad vs Dengan Kad"),
    ("variasi_3_5_sebab", "KAD PERUBATAN", "5 Sebab Perlu Kad Perubatan Takaful"),
    ("variasi_4_siapa_perlu", "KAD PERUBATAN", "Siapa Perlukan Kad Perubatan?"),
    ("chat_1_kad_perubatan", "KAD PERUBATAN", "Soal Jawab Kad Perubatan"),
    ("kuiz_1_kad_perubatan", "KAD PERUBATAN", "Kuiz: Adakah Anda Perlukan Kad Perubatan?"),
    ("hibah_1_cerita", "HIBAH TAKAFUL", "Apa Itu Hibah Takaful?"),
    ("hibah_2_mitos_fakta", "HIBAH TAKAFUL", "Mitos vs Fakta Hibah Takaful"),
    ("hibah_3_tanpa_vs_dengan", "HIBAH TAKAFUL", "Tanpa vs Dengan Hibah"),
    ("chat_2_hibah", "HIBAH TAKAFUL", "Soal Jawab Hibah Takaful"),
    ("kuiz_3_hibah", "HIBAH TAKAFUL", "Kuiz: Adakah Anda Perlukan Hibah Takaful?"),
    ("ci_1_cerita", "PENYAKIT KRITIKAL", "Kenapa Perlu Perlindungan Penyakit Kritikal?"),
    ("ci_2_mitos_fakta", "PENYAKIT KRITIKAL", "Mitos vs Fakta Penyakit Kritikal"),
    ("ci_3_tanpa_vs_dengan", "PENYAKIT KRITIKAL", "Tiada Pelan vs Ada Pelan"),
    ("chat_3_penyakit_kritikal", "PENYAKIT KRITIKAL", "Soal Jawab Penyakit Kritikal"),
    ("kuiz_2_penyakit_kritikal", "PENYAKIT KRITIKAL", "Kuiz: Adakah Anda Perlukan Pelan Penyakit Kritikal?"),
    ("gabungan_3_perlindungan", "PERLINDUNGAN ASAS", "3 Perlindungan Untuk Anda & Keluarga"),
]


def make_panel(tag, title, path):
    g = np.linspace(0, 1, H2 * S)[:, None, None]
    arr = (np.array(BG_TOP) * (1 - g) + np.array(BG_BOT) * g).astype(np.uint8)
    img = Image.fromarray(np.repeat(arr, W2 * S, axis=1), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for cx, cy, r in [(120, 140, 110), (560, 980, 150), (1500, 120, 90), (1820, 900, 160), (300, 640, 60)]:
        circle(d, cx, cy, r, WHITE, 0.35)
    # bayang di belakang video
    rrect(d, VX - 14, -20, VX + 608 + 14, H2 + 20, 0, INK, 0.12)
    # panel kiri: tajuk
    lx, lw = 60, VX - 110
    f_tag = F("xb", 30)
    tw = f_tag.getlength(tag) / S + 60
    rrect(d, lx, 300, lx + tw, 360, 30, TEAL)
    d.text((X(lx + tw / 2), X(330)), tag, font=f_tag, fill=col(WHITE), anchor="mm")
    f_t = F("xb", 54)
    lines = wrap(title, f_t, lw)
    if len(lines) > 4:
        f_t = F("xb", 46)
    y = text(d, title, lx, 400, f_t, INK, maxw=lw, align="left", lh=1.18)
    rrect(d, lx, y + 30, lx + 90, y + 40, 5, TEAL)
    text(d, f"Bersama {AGENT}, ejen {BRAND}", lx, y + 70, F("m", 28), SOFT, maxw=lw, align="left")
    # panel kanan: kad ejen
    rx0, rx1 = VX + 608 + 50, W2 - 50
    cx = (rx0 + rx1) / 2
    rrect(d, rx0, 250 + 10, rx1, 830 + 10, 36, INK, 0.07)
    rrect(d, rx0, 250, rx1, 830, 36, WHITE)
    rrect(d, rx0, 250, rx1, 380, 36, TEAL)
    d.rectangle((X(rx0), X(340), X(rx1), X(380)), fill=col(TEAL))
    circle(d, cx, 380, 82, WHITE)
    circle(d, cx, 380, 72, TEAL_D)
    d.text((X(cx), X(380)), AGENT_INITIALS, font=F("xb", 56), fill=col(WHITE), anchor="mm")
    d.text((X(cx), X(510)), AGENT.upper(), font=F("xb", 44), fill=col(INK), anchor="mm")
    d.text((X(cx), X(560)), f"Ejen {BRAND}", font=F("sb", 30), fill=col(TEAL), anchor="mm")
    d.line([(X(rx0 + 50), X(605)), (X(rx1 - 50), X(605))], fill=col(TEAL_L), width=X(3))
    nf = F("xb", 46)
    nw = nf.getlength(PHONE) / S
    d.text((X(cx + 22), X(670)), PHONE, font=nf, fill=col(INK), anchor="mm")
    phone_icon(d, cx + 22 - nw / 2 - 38, 670, 50)
    d.text((X(cx), X(730)), "Telefon / WhatsApp", font=F("m", 28), fill=col(SOFT), anchor="mm")
    f_b = F("xb", 30)
    bw = f_b.getlength("Hubungi saya hari ini!") / S + 60
    rrect(d, cx - bw / 2, 870, cx + bw / 2, 940, 35, TEAL)
    d.text((X(cx), X(905)), "Hubungi saya hari ini!", font=f_b, fill=col(WHITE), anchor="mm")
    img.reduce(S).save(path)


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    out_v = os.path.join(HERE, "16x9")
    out_p = os.path.join(HERE, "poster")
    os.makedirs(out_v, exist_ok=True)
    os.makedirs(out_p, exist_ok=True)
    for name, tag, title in VIDEOS:
        src = os.path.join(HERE, f"{name}.mp4")
        panel = os.path.join(out_p, f"_panel_{name}.png")
        make_panel(tag, title, panel)
        dst = os.path.join(out_v, f"{name}_16x9.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", panel, "-i", src, "-filter_complex",
             f"[1:v]scale=608:1080[v];[0:v][v]overlay={VX}:0:shortest=1,format=yuv420p", "-map", "1:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30", "-c:a", "copy",
             "-movflags", "+faststart", dst])
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "3.5", "-i", src, "-frames:v", "1",
             os.path.join(out_p, f"{name}_cover_9x16.png")])
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "3.5", "-i", dst, "-frames:v", "1",
             os.path.join(out_p, f"{name}_thumb_16x9.png")])
        os.remove(panel)
        print("Siap:", name, flush=True)


if __name__ == "__main__":
    main()
