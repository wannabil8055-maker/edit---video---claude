"""Variasi video kesedaran kad perubatan takaful (guna komponen dari make_video.py).

Guna:  python3 variasi.py                 -> render semua variasi
       python3 variasi.py mitos sebab     -> render variasi tertentu
       python3 variasi.py --preview mitos 3.0 9.5   -> simpan frame PNG untuk semakan
"""
import math
import os
import subprocess
import sys
from multiprocessing import Pool

from PIL import ImageDraw, Image

import make_video as mv
from make_video import (F, X, col, prog, ease, ease_back, wrap, text, atext, rrect, card, circle, check_icon,
                        shield, heart, sparkle, coin, person, pill, hospital, scene_agent, W, H, S, FPS, INK, SOFT,
                        TEAL, TEAL_D, TEAL_L, CORAL, GOLD, GOLD_D, WHITE, AGENT, PHONE)

mv.FONTS["mi"] = "Inter-MediumItalic.otf"
HERE = os.path.dirname(os.path.abspath(__file__))
GREY = (150, 138, 140)
GREEN = (46, 170, 90)


# ---------------------------------------------------------------- ikon tambahan
def x_icon(d, cx, cy, r, a=1.0, bg=CORAL):
    circle(d, cx, cy, r, bg, a)
    k, w = 0.34 * r, X(0.17 * r)
    d.line([(X(cx - k), X(cy - k)), (X(cx + k), X(cy + k))], fill=col(WHITE, a), width=w)
    d.line([(X(cx - k), X(cy + k)), (X(cx + k), X(cy - k))], fill=col(WHITE, a), width=w)


def pulse_rings(d, cx, cy, r0, lt, start=0.5):
    if lt < start:
        return
    for k in range(2):
        ph = ((lt + k * 0.75) % 1.5) / 1.5
        circle(d, cx, cy, r0 + ph * 200, None, outline=TEAL, width=6, a=0.3 * (1 - ph))


def icon_chart(d, cx, cy, p):
    heights = [70, 105, 145, 190]
    tops = []
    for i, h in enumerate(heights):
        bx = cx - 150 + i * 80
        hh = h * p
        rrect(d, bx, cy + 110 - hh, bx + 56, cy + 110, 12, TEAL if i == 3 else CORAL, 0.55 + 0.15 * i)
        tops.append((bx + 28, cy + 110 - h - 35))
    if p > 0.6:
        d.line([(X(x), X(y)) for x, y in tops], fill=col(INK), width=X(8), joint="curve")
        lx, ly = tops[-1]
        d.polygon([(X(lx + 34), X(ly - 26)), (X(lx - 8), X(ly - 18)), (X(lx + 20), X(ly + 18))], fill=col(INK))


def coin_stack(d, cx, base, n, w=120):
    for k in range(n):
        y = base - k * 26
        d.ellipse((X(cx - w / 2), X(y - 18), X(cx + w / 2), X(y + 26)), fill=col(GOLD_D))
        d.ellipse((X(cx - w / 2), X(y - 26), X(cx + w / 2), X(y + 18)), fill=col(GOLD))


def icon_savings(d, cx, cy, p):
    coin_stack(d, cx - 85, cy + 100, max(1, int(6 * p)))
    coin_stack(d, cx + 45, cy + 100, max(1, int(4 * p)))
    if p > 0.5:
        shield(d, cx + 120, cy + 40, 85 * ease_back((p - 0.5) * 2), cross=False)
        heart(d, cx + 120, cy + 36, 62 * ease_back((p - 0.5) * 2), WHITE)


def icon_hospital(d, cx, cy, p):
    hospital(d, cx, cy + 150, 0.9 * p, 1.0)


def icon_shield(d, cx, cy, p):
    shield(d, cx, cy, 170 * p, cross=False)
    heart(d, cx, cy - 6, 130 * p, WHITE)


def icon_family(d, cx, cy, p):
    person(d, cx - 110, cy + 10, 0.85 * p, "happy", shirt=TEAL)
    person(d, cx + 110, cy + 15, 0.8 * p, "happy", shirt=CORAL, hijab=TEAL_D)
    person(d, cx, cy + 90, 0.55 * p, "happy", shirt=GOLD)


def laptop(d, cx, cy, s, a=1.0):
    rrect(d, cx - 120 * s, cy - 80 * s, cx + 120 * s, cy + 70 * s, 14 * s, INK, a)
    rrect(d, cx - 106 * s, cy - 66 * s, cx + 106 * s, cy + 56 * s, 8 * s, TEAL_L, a)
    rrect(d, cx - 160 * s, cy + 70 * s, cx + 160 * s, cy + 92 * s, 10 * s, GREY, a)


# ---------------------------------------------------------------- babak umum
def make_intro(tag, title, accent, sub, icon):
    def scene(d, lt, D):
        cy = 640 + 10 * math.sin(lt * 2)
        pulse_rings(d, 540, cy, 230, lt)
        circle(d, 540, cy, 230 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.7)
        p = ease_back(prog(lt, 0.2, 0.7))
        if p > 0:
            icon(d, 540, cy, p)
        pill(d, 540, 950, tag, F("xb", 38), WHITE, TEAL, ease(prog(lt, 0.5, 0.5)), h=84)
        y = atext(d, title, 540, 1080, F("xb", 84), INK, lt, 0.7, maxw=940)
        y = atext(d, accent, 540, y, F("xb", 96), TEAL, lt, 0.95, maxw=940)
        atext(d, sub, 540, y + 40, F("m", 46), SOFT, lt, 1.3, maxw=880)
    return scene


def icon_versus(d, cx, cy, p):
    x_icon(d, cx - 95, cy, 95 * p, bg=GREY)
    check_icon(d, cx + 95, cy, 95 * p)
    if p > 0.7:
        circle(d, cx, cy, 52, WHITE)
        d.text((X(cx), X(cy)), "vs", font=F("xb", 46), fill=col(INK), anchor="mm")


def icon_myth(d, cx, cy, p):
    rrect(d, cx - 170 * p, cy - 120 * p, cx + 170 * p, cy + 90 * p, 40 * p, TEAL_L)
    d.polygon([(X(cx - 60 * p), X(cy + 85 * p)), (X(cx - 110 * p), X(cy + 160 * p)), (X(cx + 10 * p), X(cy + 85 * p))],
              fill=col(TEAL_L))
    if p > 0.6:
        d.text((X(cx), X(cy - 15)), "?", font=F("xb", 170), fill=col(TEAL), anchor="mm")
    x_icon(d, cx + 160 * p, cy - 110 * p, 52 * p)


def icon_five(d, cx, cy, p):
    circle(d, cx, cy, 175 * p, TEAL)
    if p > 0.5:
        d.text((X(cx), X(cy + 8)), "5", font=F("xb", int(260 * p)), fill=col(WHITE), anchor="mm")


def icon_who(d, cx, cy, p):
    for i, (dx, sc, sh, hj) in enumerate([(-150, 0.7, CORAL, None), (0, 0.85, TEAL, None), (150, 0.7, GOLD, TEAL_D)]):
        person(d, cx + dx, cy + 40 + (1 - sc) * 100, sc * p, "happy", shirt=sh, hijab=hj)
    if p > 0.6:
        circle(d, cx, cy - 200, 50, WHITE)
        d.text((X(cx), X(cy - 200)), "?", font=F("xb", 70), fill=col(TEAL), anchor="mm")


# ---------------------------------------------------------------- 1. Mitos vs Fakta
MYTHS = [
    ("“Saya masih muda dan sihat, tak perlu lagi.”",
     "Sakit dan kemalangan tak kenal usia. Bila mendaftar semasa muda dan sihat, caruman biasanya lebih rendah "
     "dan permohonan lebih mudah diterima."),
    ("“Hospital kerajaan kan ada, cukuplah.”",
     "Hospital kerajaan sangat membantu. Kad perubatan pula memberi lebih banyak pilihan hospital & doktor pakar, "
     "serta kemasukan yang lebih segera."),
    ("“Majikan dah sediakan medical card, dah cukup.”",
     "Perlindungan majikan biasanya tamat bila anda berhenti kerja, dan hadnya mungkin terhad. Pelan sendiri "
     "kekal bersama anda."),
    ("“Mahal, saya tak mampu.”",
     "Caruman boleh disesuaikan ikut bajet & keperluan. Bil hospital tanpa perlindungan biasanya jauh lebih mahal."),
]


def make_myth(n, myth, fact):
    def scene(d, lt, D):
        pill(d, 540, 200, f"MITOS #{n}", F("xb", 42), WHITE, CORAL, ease(prog(lt, 0.1, 0.4)), h=88)
        e = ease(prog(lt, 0.3, 0.6))
        if e > 0:
            o = (1 - e) * 50
            card(d, 90, 330 + o, 990, 680 + o, 40, e)
            f = F("mi", 52)
            hh = len(wrap(myth, f, 760)) * 52 * 1.25
            text(d, myth, 540, 505 + o - hh / 2, f, INK, e * (1 - 0.45 * ease(prog(lt, 1.6, 0.4))), maxw=760)
        xb = ease_back(prog(lt, 1.5, 0.5))
        if xb > 0:
            x_icon(d, 925, 345, 62 * xb)
        fa = ease(prog(lt, 2.2, 0.6))
        if fa > 0:
            o = (1 - fa) * 40
            d.polygon([(X(500), X(720 + o)), (X(580), X(720 + o)), (X(540), X(770 + o))], fill=col(TEAL, fa))
            pill(d, 540, 800 + o, "FAKTA", F("xb", 42), WHITE, TEAL, fa, h=88)
            card(d, 90, 930 + o, 990, 1440 + o, 40, fa)
            f = F("sb", 47)
            hh = len(wrap(fact, f, 790)) * 47 * 1.3
            text(d, fact, 540, 1185 + o - hh / 2, f, INK, fa, maxw=790, lh=1.3)
        pp = ease_back(prog(lt, 3.0, 0.6))
        if pp > 0:
            person(d, 540, 1660, 0.85 * pp, "happy")
            check_icon(d, 650, 1520, 40 * pp, bg=GREEN)
    return scene


# ---------------------------------------------------------------- 2. Tanpa vs Dengan
ROWS = [("Perlu bayar deposit dahulu", "Masuk tanpa tunai di hospital panel"),
        ("Guna simpanan atau berhutang", "Bil ditanggung ikut had pelan"),
        ("Risau kos, susah nak berehat", "Tenang & fokus untuk sembuh")]


def scene_compare(d, lt, D):
    atext(d, "Bila masuk hospital...", 540, 170, F("xb", 68), INK, lt, 0.1)
    cols = [(70, 525, "TANPA KAD", GREY, "sad", 0.4), (555, 1010, "DENGAN KAD", TEAL, "happy", 0.7)]
    for side, (x0, x1, hdr, c, mood, st) in enumerate(cols):
        cx = (x0 + x1) / 2
        p = ease_back(prog(lt, st, 0.6))
        if p > 0:
            person(d, cx, 470, 0.95 * p, mood, shirt=c)
        e = ease(prog(lt, st + 0.2, 0.5))
        if e > 0:
            rrect(d, x0, 660, x1, 755, 30, c, e)
            d.text((X(cx), X(707)), hdr, font=F("xb", 42), fill=col(WHITE, e), anchor="mm")
    for i, (left, right) in enumerate(ROWS):
        y0 = 790 + i * 250
        for side, (x0, x1, txt, st) in enumerate([(70, 525, left, 1.5 + i * 1.5), (555, 1010, right, 2.1 + i * 1.5)]):
            e = ease(prog(lt, st, 0.5))
            if e <= 0:
                continue
            o = (1 - e) * 40
            cx = (x0 + x1) / 2
            card(d, x0, y0 + o, x1, y0 + 225 + o, 30, e)
            (x_icon if side == 0 else check_icon)(d, cx, y0 + 52 + o, 30, e, *( [GREY] if side == 0 else []))
            f = F("sb", 40)
            hh = len(wrap(txt, f, 390)) * 40 * 1.22
            text(d, txt, cx, y0 + 150 + o - hh / 2, f, INK, e, maxw=390, lh=1.22)
    atext(d, "Bezanya besar, bukan?", 540, 1580, F("xb", 60), TEAL_D, lt, 6.6)


def scene_umbrella(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    cy = 640
    pulse_rings(d, 540, cy, 220, lt)
    if p > 0:
        shield(d, 540, cy, 210 * p)
    y = atext(d, "Jangan tunggu sakit, baru nak cari perlindungan.", 540, 960, F("xb", 74), INK, lt, 0.6, maxw=900)
    atext(d, "Sediakan payung sebelum hujan.", 540, y + 50, F("sb", 56), TEAL, lt, 1.2, maxw=900)


# ---------------------------------------------------------------- 3. 5 Sebab
REASONS = [
    ("Kos perubatan naik setiap tahun", "Rawatan hari ini lebih mahal berbanding beberapa tahun lalu, dan dijangka "
     "terus meningkat.", icon_chart),
    ("Lindungi simpanan anda", "Simpanan untuk rumah, pendidikan anak & persaraan tak perlu habis untuk bil "
     "hospital.", icon_savings),
    ("Lebih pilihan hospital", "Akses ke hospital swasta & doktor pakar, dengan kemasukan tanpa tunai di hospital "
     "panel.", icon_hospital),
    ("Patuh Syariah", "Berasaskan konsep tabarru' & ta'awun, iaitu saling membantu sesama peserta.", icon_shield),
    ("Ketenangan untuk keluarga", "Keluarga tak perlu menanggung beban kewangan ketika anda sakit.", icon_family),
]


def make_reason(n, title, desc, icon):
    def scene(d, lt, D):
        b = ease_back(prog(lt, 0.1, 0.5))
        if b > 0:
            circle(d, 540, 330, 85 * b, TEAL)
            d.text((X(540), X(335)), str(n), font=F("xb", int(100 * b) + 1), fill=col(WHITE), anchor="mm")
        p = ease_back(prog(lt, 0.4, 0.7))
        if p > 0:
            circle(d, 540, 800, 270 * p, TEAL_L, 0.75)
            icon(d, 540, 800, p)
        y = atext(d, title, 540, 1170, F("xb", 72), INK, lt, 0.7, maxw=920)
        atext(d, desc, 540, y + 30, F("m", 48), SOFT, lt, 1.1, maxw=860)
    return scene


# ---------------------------------------------------------------- 4. Siapa perlu
def persona_young(d, cx, cy, p, lt):
    person(d, cx, cy, 1.4 * p, "happy", shirt=TEAL, wave_ang=math.radians(60 + 25 * math.sin(lt * 7)))
    for i, (sx, sy) in enumerate([(cx - 200, cy - 230), (cx + 220, cy - 260)]):
        sparkle(d, sx, sy, 30 * p * (1 + 0.2 * math.sin(lt * 5 + i)))


def persona_parents(d, cx, cy, p, lt):
    icon_family(d, cx, cy - 20, p * 1.25)
    heart(d, cx, cy - 280 + 8 * math.sin(lt * 3), 80 * p, TEAL)


def persona_business(d, cx, cy, p, lt):
    person(d, cx, cy - 20, 1.25 * p, "happy", shirt=TEAL_D)
    laptop(d, cx, cy + 150, 0.95 * p)


def make_persona(n, title, desc, draw):
    def scene(d, lt, D):
        pill(d, 540, 260, f"#{n}", F("xb", 42), WHITE, TEAL, ease(prog(lt, 0.1, 0.4)), h=88, padx=40)
        p = ease_back(prog(lt, 0.3, 0.7))
        circle(d, 540, 800, 310 * ease_back(prog(lt, 0.15, 0.6)), WHITE, 0.7)
        if p > 0:
            draw(d, 540, 860, p, lt)
        y = atext(d, title, 540, 1230, F("xb", 74), INK, lt, 0.7, maxw=920)
        atext(d, desc, 540, y + 30, F("m", 48), SOFT, lt, 1.1, maxw=860)
    return scene


PERSONAS = [
    ("Anak muda baru bekerja", "Mula awal. Caruman biasanya lebih rendah semasa muda & sihat.", persona_young),
    ("Ibu bapa", "Pastikan seisi keluarga terlindung, termasuk anak-anak.", persona_parents),
    ("Pekerja sendiri & peniaga", "Tiada medical card majikan? Pelan sendiri jadi pelindung utama anda.",
     persona_business),
]


def scene_everyone(d, lt, D):
    atext(d, "Jawapannya?", 540, 520, F("sb", 60), SOFT, lt, 0.1)
    atext(d, "SEMUA ORANG.", 540, 620, F("xb", 110), TEAL, lt, 0.5)
    people = [(180, CORAL, None), (360, GOLD, TEAL_D), (540, TEAL, None), (720, (120, 110, 200), TEAL_D),
              (900, (90, 160, 90), None)]
    for i, (px, sh, hj) in enumerate(people):
        p = ease_back(prog(lt, 1.0 + i * 0.15, 0.5))
        if p > 0:
            person(d, px, 1120 + 12 * math.sin(lt * 3 + i), 0.8 * p, "happy", shirt=sh, hijab=hj)
    atext(d, "Kesihatan tak boleh dijangka. Perlindungan boleh dirancang.", 540, 1450, F("sb", 54), INK, lt, 2.0,
          maxw=880)


# ---------------------------------------------------------------- senarai variasi
VARIATIONS = {
    "mitos": ("variasi_1_mitos_fakta.mp4",
              [(4.0, make_intro("MITOS vs FAKTA", "Kad Perubatan", "Takaful", "Yang mana pernah anda dengar?",
                                icon_myth))]
              + [(7.0, make_myth(i + 1, m, f)) for i, (m, f) in enumerate(MYTHS)] + [(7.5, scene_agent)],
              ["Am", "F", "C", "G"] * 4),
    "banding": ("variasi_2_tanpa_vs_dengan.mp4",
                [(4.0, make_intro("TANPA vs DENGAN", "Bila masuk hospital, apa", "bezanya?",
                                  "Ada dan tiada kad perubatan takaful", icon_versus)),
                 (11.0, scene_compare), (5.0, scene_umbrella), (7.5, scene_agent)],
                ["Am", "F", "Dm", "E", "F", "G", "C", "Am", "F", "G", "C", "C"]),
    "sebab": ("variasi_3_5_sebab.mp4",
              [(4.0, make_intro("TAHUKAH ANDA?", "Sebab anda perlu", "Kad Perubatan Takaful", "", icon_five))]
              + [(5.5, make_reason(i + 1, *r)) for i, r in enumerate(REASONS)] + [(7.5, scene_agent)],
              ["C", "G", "Am", "F"] * 4),
    "siapa": ("variasi_4_siapa_perlu.mp4",
              [(4.0, make_intro("SOALAN", "Siapa perlukan", "kad perubatan?", "Mungkin anda salah seorang...",
                                icon_who))]
              + [(5.5, make_persona(i + 1, *pp)) for i, pp in enumerate(PERSONAS)]
              + [(5.0, scene_everyone), (7.5, scene_agent)],
              ["F", "G", "C", "Am"] * 4),
}

CUR = None


def render(t):
    _, scenes, _ = VARIATIONS[CUR]
    total = sum(s[0] for s in scenes)
    acc = 0.0
    for idx, (dur, fn) in enumerate(scenes):
        if t < acc + dur or idx == len(scenes) - 1:
            break
        acc += dur
    lt = t - acc
    bg = mv.background(t)
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    fn(d, lt, dur)
    a = min(1.0, lt / mv.FADE if idx > 0 else 1.0, (dur - lt) / mv.FADE if idx < len(scenes) - 1 else 1.0)
    if a < 1:
        img = Image.blend(bg, img, max(0.0, a))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, X(W * t / total), X(10)), fill=col(TEAL))
    if fn is not scene_agent:
        pill(d, 540, 36, f"{AGENT}  ·  {PHONE}", F("b", 36), TEAL_D, WHITE, 0.9, padx=34, h=76)
    return img.reduce(S)


def render_bytes(i):
    return render(i / FPS).tobytes()


def build(name):
    global CUR
    CUR = name
    fname, scenes, chords = VARIATIONS[name]
    total = sum(s[0] for s in scenes)
    out = os.path.join(HERE, fname)
    music = os.path.join(HERE, f"music_{name}.wav")
    mv.make_music(music, total=total, prog_=chords)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", music, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for buf in pool.imap(render_bytes, range(int(total * FPS)), chunksize=6):
            proc.stdin.write(buf)
    proc.stdin.close()
    proc.wait()
    os.remove(music)
    print(f"Siap: {out} ({total:.1f}s)")


def main():
    global CUR
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        CUR = args[1]
        outdir = os.path.join(HERE, "preview")
        os.makedirs(outdir, exist_ok=True)
        for ts in args[2:]:
            render(float(ts)).save(os.path.join(outdir, f"{CUR}_{float(ts):05.1f}.png"))
        return
    for name in (args or list(VARIATIONS)):
        build(name)


if __name__ == "__main__":
    main()
