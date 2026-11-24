"""Versi chat soal jawab (kad perubatan, hibah, penyakit kritikal) + video gabungan 3 perlindungan.

Guna:  python3 versi_chat.py                     -> render semua
       python3 versi_chat.py chat_medical        -> render satu
       python3 versi_chat.py --preview chat_medical 10 20
"""
import math
import os
import sys

import variasi as va
from make_video import (F, X, col, prog, ease, ease_back, wrap, text, atext, rrect, card, circle, shield,
                        scene_agent, INK, SOFT, TEAL, TEAL_D, TEAL_L, WHITE, AGENT, AGENT_INITIALS, BRAND)
from variasi import make_intro, pulse_rings
from hibah import icon_gift
from ci import icon_heartbeat

HERE = os.path.dirname(os.path.abspath(__file__))
GREEN = (46, 170, 90)


# ---------------------------------------------------------------- ikon
def icon_chat(d, cx, cy, p):
    rrect(d, cx - 190 * p, cy - 150 * p, cx + 60 * p, cy + 10 * p, 50 * p, WHITE)
    d.polygon([(X(cx - 140 * p), X(cy + 5 * p)), (X(cx - 170 * p), X(cy + 70 * p)), (X(cx - 80 * p), X(cy + 5 * p))],
              fill=col(WHITE))
    if p > 0.6:
        d.text((X(cx - 65), X(cy - 70)), "?", font=F("xb", 110), fill=col(TEAL), anchor="mm")
    rrect(d, cx - 40 * p, cy + 20 * p, cx + 200 * p, cy + 170 * p, 50 * p, TEAL)
    d.polygon([(X(cx + 130 * p), X(cy + 165 * p)), (X(cx + 175 * p), X(cy + 225 * p)), (X(cx + 70 * p), X(cy + 165 * p))],
              fill=col(TEAL))
    if p > 0.6:
        for k in range(3):
            circle(d, cx + 30 + k * 50, cy + 95, 14, WHITE)


def icon_three(d, cx, cy, p):
    circle(d, cx, cy, 175 * p, TEAL)
    if p > 0.5:
        d.text((X(cx), X(cy + 8)), "3", font=F("xb", int(260 * p)), fill=col(WHITE), anchor="mm")


def icon_medical(d, cx, cy, p):
    shield(d, cx, cy, 170 * p)


# ---------------------------------------------------------------- babak chat
TOP, BOTTOM, BW = 300, 1750, 640


def make_chat(topic, msgs):
    timeline, t = [], 1.0
    for side, txt in msgs:
        if side == "a":
            ts = t
            t += 1.0
            timeline.append((side, txt, t, ts))
            t += max(3.4, len(txt) / 21)
        else:
            timeline.append((side, txt, t, None))
            t += max(1.8, len(txt) / 24)

    def scene(d, lt, D):
        f = F("sb", 40)
        items = [("chip", f"Soalan lazim: {topic}", ease(prog(lt, 0.3, 0.4)))]
        for side, txt, ta, ts in timeline:
            if ts is not None and ts <= lt < ta:
                items.append(("typing", None, ease(prog(lt, ts, 0.25))))
            e = ease(prog(lt, ta, 0.35))
            if e > 0:
                items.append((side, txt, e))
        sizes = []
        for kind, txt, e in items:
            if kind == "chip":
                h = 64
            elif kind == "typing":
                h = 92
            else:
                h = len(wrap(txt, f, BW)) * 40 * 1.3 + 56
            sizes.append(h)
        total = sum((h + 28) * e for h, (_, _, e) in zip(sizes, items))
        y = TOP + 40 - max(0.0, TOP + 40 + total - BOTTOM)
        for h, (kind, txt, e) in zip(sizes, items):
            if kind == "chip":
                fc = F("sb", 30)
                w = fc.getlength(txt) / 2 + 60
                rrect(d, 540 - w / 2, y, 540 + w / 2, y + h, h / 2, TEAL_L, e)
                d.text((X(540), X(y + h / 2)), txt, font=fc, fill=col(TEAL_D, e), anchor="mm")
            elif kind == "typing":
                rrect(d, 1020 - 170, y, 1020, y + h, 40, TEAL, e)
                for k in range(3):
                    bounce = 10 * max(0.0, math.sin(lt * 8 - k * 0.8))
                    circle(d, 1020 - 125 + k * 40, y + h / 2 - bounce, 11, WHITE, e)
            else:
                lines = wrap(txt, f, BW)
                w = max(f.getlength(l) for l in lines) / 2 + 56
                o = (1 - e) * 40
                if kind == "c":
                    x0 = 60 - o
                    rrect(d, x0, y + 6, x0 + w, y + h + 6, 34, INK, 0.07 * e)
                    rrect(d, x0, y, x0 + w, y + h, 34, WHITE, e)
                    fg = INK
                else:
                    x0 = 1020 - w + o
                    rrect(d, x0, y, x0 + w, y + h, 34, TEAL, e)
                    fg = WHITE
                text(d, txt, x0 + 28, y + 26, f, fg, e, maxw=BW, align="left", lh=1.3)
            y += (h + 28) * e
        # header & bar input (dilukis terakhir supaya menutup mesej yang tergulung ke atas)
        rrect(d, 0, 0, 1080, TOP, 0, WHITE)
        d.line([(0, X(TOP)), (X(1080), X(TOP))], fill=col(TEAL_L), width=X(3))
        circle(d, 130, 180, 62, TEAL_D)
        d.text((X(130), X(180)), AGENT_INITIALS, font=F("xb", 46), fill=col(WHITE), anchor="mm")
        circle(d, 177, 225, 14, WHITE)
        circle(d, 177, 225, 10, GREEN)
        d.text((X(220), X(155)), AGENT, font=F("b", 46), fill=col(INK), anchor="lm")
        d.text((X(220), X(210)), f"Ejen {BRAND}  ·  dalam talian", font=F("r", 32), fill=col(SOFT), anchor="lm")
        rrect(d, 40, 1790, 900, 1880, 45, WHITE)
        d.text((X(90), X(1835)), "Tulis mesej...", font=F("r", 34), fill=col(SOFT, 0.7), anchor="lm")
        circle(d, 980, 1835, 45, TEAL)
        d.polygon([(X(962), X(1812)), (X(1005), X(1835)), (X(962), X(1858)), (X(970), X(1835))], fill=col(WHITE))

    scene.no_pill = True
    return scene, t + 1.2


CHAT_MEDICAL = [
    ("c", "Salam Nabil. Saya dah ada medical card majikan. Perlu ke ambil sendiri?"),
    ("a", "Waalaikumussalam. Medical card majikan biasanya tamat bila berhenti kerja. Pelan sendiri kekal bersama "
          "anda."),
    ("c", "Kalau masuk hospital, kena bayar dulu ke?"),
    ("a", "Di hospital panel, boleh masuk tanpa tunai. Tunjuk kad sahaja, tertakluk kepada syarat pelan."),
    ("c", "Apa yang dilindungi?"),
    ("a", "Contohnya bilik hospital, pembedahan, ujian makmal & ubat semasa di wad. Liputan ikut pelan."),
    ("c", "Ok, saya nak tahu pelan yang sesuai."),
    ("a", "Boleh! Saya bantu pilih ikut bajet & keperluan anda."),
]

CHAT_HIBAH = [
    ("c", "Nabil, apa sebenarnya hibah takaful?"),
    ("a", "Hibah maksudnya hadiah. Anda namakan penerima, contohnya isteri atau anak."),
    ("c", "Bila mereka akan terima?"),
    ("a", "Bila berlaku kematian, manfaat dibayar terus kepada penerima hibah. Tak perlu tunggu proses pusaka."),
    ("c", "Kena bahagi ikut faraid ke?"),
    ("a", "Jika penamaan dibuat sebagai penerima hibah, manfaat itu milik penerima dan tidak dibahagikan ikut "
          "faraid."),
    ("c", "Kalau dapat anak baru nanti?"),
    ("a", "Penama boleh dikemas kini. Saya boleh bantu uruskan."),
]

CHAT_CI = [
    ("c", "Saya dah ada medical card. Perlu lagi ke pelan penyakit kritikal?"),
    ("a", "Medical card bayar bil hospital. Pelan penyakit kritikal bayar wang tunai sekaligus terus kepada anda."),
    ("c", "Wang tu boleh guna untuk apa?"),
    ("a", "Apa sahaja: ganti pendapatan, bayar ansuran rumah, kereta & belanja keluarga semasa pulih."),
    ("c", "Penyakit apa yang dilindungi?"),
    ("a", "Contohnya kanser, serangan jantung & strok. Senarai penuh bergantung kepada pelan."),
    ("c", "Bila patut ambil?"),
    ("a", "Semasa masih sihat. Penyakit sedia ada biasanya tidak dilindungi, dan caruman lebih rendah bila mula "
          "awal."),
]


# ---------------------------------------------------------------- video gabungan 3 perlindungan
def make_plan(n, situation, plan, desc, icon):
    def scene(d, lt, D):
        va.pill(d, 540, 200, f"#{n}", F("xb", 42), WHITE, TEAL, ease(prog(lt, 0.1, 0.4)), h=88, padx=40)
        atext(d, situation, 540, 330, F("sb", 56), SOFT, lt, 0.2, maxw=900)
        circle(d, 540, 760, 270 * ease_back(prog(lt, 0.3, 0.6)), WHITE, 0.7)
        p = ease_back(prog(lt, 0.5, 0.7))
        if p > 0:
            icon(d, 540, 760, p)
        y = atext(d, plan, 540, 1100, F("xb", 88), TEAL, lt, 0.9, maxw=940)
        atext(d, desc, 540, y + 30, F("m", 50), INK, lt, 1.3, maxw=860)
    return scene


PLANS = [
    ("Bila masuk hospital...", "Kad Perubatan", "Bayar bil hospital. Masuk tanpa tunai di hospital panel.",
     icon_medical),
    ("Bila disahkan sakit kritikal...", "Penyakit Kritikal", "Wang tunai sekaligus untuk ganti pendapatan & "
     "komitmen.", icon_heartbeat),
    ("Bila ketua keluarga tiada...", "Hibah Takaful", "Wang terus kepada keluarga, tanpa tunggu proses pusaka.",
     icon_gift),
]


def scene_summary(d, lt, D):
    atext(d, "Lengkapkan perlindungan anda", 540, 210, F("xb", 62), INK, lt, 0.2, maxw=980)
    for i, (_, plan, desc, icon) in enumerate(PLANS):
        e = ease(prog(lt, 0.8 + i * 0.7, 0.6))
        if e <= 0:
            continue
        o = (1 - e) * 500
        y0 = 420 + i * 300
        card(d, 90 + o, y0, 990 + o, y0 + 260, 40, e)
        circle(d, 240 + o, y0 + 130, 100, TEAL_L, e)
        icon(d, 240 + o, y0 + 130, 0.42)
        d.text((X(380 + o), X(y0 + 75)), plan, font=F("xb", 50), fill=col(TEAL, e), anchor="lm")
        text(d, desc, 380 + o, y0 + 115, F("m", 38), INK, e, maxw=560, align="left", lh=1.22)
    atext(d, "Setiap satu melindungi keperluan yang berbeza.", 540, 1350, F("sb", 52), INK, lt, 3.0, maxw=880)
    atext(d, "Semak perlindungan anda hari ini.", 540, 1520, F("xb", 54), TEAL_D, lt, 3.6, maxw=980)


# ---------------------------------------------------------------- senarai
def chat_video(fname, topic, accent, msgs, chords):
    chat, dur = make_chat(topic, msgs)
    return (fname, [(4.0, make_intro("SOAL JAWAB", "Soalan lazim tentang", accent,
                                     f"Bersama {AGENT}, ejen {BRAND}", icon_chat)),
                    (dur, chat), (7.5, scene_agent)], chords)


NEW = {
    "chat_medical": chat_video("chat_1_kad_perubatan.mp4", "Kad Perubatan", "Kad Perubatan", CHAT_MEDICAL,
                               ["F", "G", "C", "Am"] * 5),
    "chat_hibah": chat_video("chat_2_hibah.mp4", "Hibah Takaful", "Hibah Takaful", CHAT_HIBAH,
                             ["C", "Am", "F", "G"] * 5),
    "chat_ci": chat_video("chat_3_penyakit_kritikal.mp4", "Penyakit Kritikal", "Penyakit Kritikal", CHAT_CI,
                          ["Am", "F", "C", "G"] * 5),
    "gabungan": ("gabungan_3_perlindungan.mp4",
                 [(4.0, make_intro("PERLINDUNGAN ASAS", "Perlindungan untuk", "Anda & Keluarga",
                                   "Kad perubatan, penyakit kritikal & hibah", icon_three))]
                 + [(5.5, make_plan(i + 1, *pl)) for i, pl in enumerate(PLANS)]
                 + [(7.0, scene_summary), (7.5, scene_agent)],
                 ["C", "G", "Am", "F"] * 4),
}
va.VARIATIONS.update(NEW)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        va.CUR = args[1]
        outdir = os.path.join(HERE, "preview")
        os.makedirs(outdir, exist_ok=True)
        for ts in args[2:]:
            va.render(float(ts)).save(os.path.join(outdir, f"{va.CUR}_{float(ts):05.1f}.png"))
        return
    for name in (args or list(NEW)):
        va.build(name)


if __name__ == "__main__":
    main()
