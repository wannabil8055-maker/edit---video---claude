"""Video kesedaran: Kepentingan Hibah Takaful (cerita utama + 2 variasi).

Guna:  python3 hibah.py                       -> render semua
       python3 hibah.py hibah_cerita          -> render satu
       python3 hibah.py --preview hibah_cerita 3.0 12.0
"""
import math
import os
import sys

import variasi as va
from make_video import (F, X, col, prog, ease, ease_back, wrap, text, atext, rrect, card, circle, check_icon, shield,
                        heart, sparkle, person, pill, scene_agent, INK, SOFT, TEAL, TEAL_D, TEAL_L, CORAL, GOLD,
                        GOLD_D, WHITE)
from variasi import x_icon, pulse_rings, make_intro, make_myth, GREY

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- ikon
def gift(d, cx, cy, s, a=1.0, c=TEAL):
    rrect(d, cx - s, cy - 0.2 * s, cx + s, cy + s, 0.12 * s, c, a)
    rrect(d, cx - 1.12 * s, cy - 0.52 * s, cx + 1.12 * s, cy - 0.12 * s, 0.1 * s, TEAL_D, a)
    rrect(d, cx - 0.14 * s, cy - 0.52 * s, cx + 0.14 * s, cy + s, 0.04 * s, GOLD, a)
    d.ellipse((X(cx - 0.75 * s), X(cy - 0.95 * s), X(cx - 0.05 * s), X(cy - 0.5 * s)), fill=col(GOLD, a))
    d.ellipse((X(cx + 0.05 * s), X(cy - 0.95 * s), X(cx + 0.75 * s), X(cy - 0.5 * s)), fill=col(GOLD, a))
    circle(d, cx, cy - 0.6 * s, 0.14 * s, GOLD_D, a)


def icon_gift(d, cx, cy, p):
    gift(d, cx, cy + 20, 140 * p)
    if p > 0.6:
        heart(d, cx + 150, cy - 140, 60, CORAL)


def silhouette(d, cx, cy, sc, c=TEAL_L, a=1.0):
    k = lambda v: v * sc
    rrect(d, cx - k(85), cy - k(30), cx + k(85), cy + k(160), k(60), c, a)
    circle(d, cx, cy - k(110), k(68), c, a)


def locked_doc(d, cx, cy, s, a=1.0):
    rrect(d, cx - 0.8 * s, cy - s, cx + 0.8 * s, cy + s, 0.12 * s, WHITE, a)
    for k in range(4):
        rrect(d, cx - 0.55 * s, cy - 0.7 * s + k * 0.3 * s, cx + 0.55 * s - (0.3 * s if k == 3 else 0),
              cy - 0.6 * s + k * 0.3 * s, 0.05 * s, TEAL_L, a)
    lx, ly = cx + 0.65 * s, cy + 0.6 * s
    d.arc((X(lx - 0.3 * s), X(ly - 0.65 * s), X(lx + 0.3 * s), X(ly - 0.05 * s)), 180, 360, fill=col(INK, a),
          width=X(0.1 * s))
    rrect(d, lx - 0.42 * s, ly - 0.32 * s, lx + 0.42 * s, ly + 0.32 * s, 0.08 * s, CORAL, a)
    circle(d, lx, ly - 0.02 * s, 0.07 * s, WHITE, a)


def family(d, cx, cy, p, mood="happy", with_father=True):
    if with_father:
        person(d, cx - 120, cy, 0.9 * p, mood, shirt=TEAL)
        person(d, cx + 110, cy + 10, 0.85 * p, mood, shirt=CORAL, hijab=TEAL_D)
    else:
        person(d, cx, cy + 10, 0.9 * p, mood, shirt=CORAL, hijab=TEAL_D)
    person(d, cx - (20 if with_father else 150), cy + 95, 0.55 * p, mood, shirt=GOLD)
    person(d, cx + (60 if with_father else 150), cy + 105, 0.5 * p, mood, shirt=(120, 110, 200))


# ---------------------------------------------------------------- babak cerita utama
def scene_family(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    circle(d, 540, 780, 330 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.6)
    if p > 0:
        family(d, 540, 760, p * 1.25)
    for i, (sx, sy) in enumerate([(260, 480), (820, 470)]):
        sparkle(d, sx, sy, 28 * ease(prog(lt, 0.8 + 0.2 * i, 0.5)) * (1 + 0.15 * math.sin(lt * 4 + i)))
    atext(d, "Ini Ali, ketua keluarga.", 540, 1180, F("xb", 78), INK, lt, 0.6, maxw=940)
    atext(d, "Isteri dan anak-anak bergantung pada pendapatan Ali setiap bulan.", 540, 1300, F("m", 50), SOFT,
          lt, 1.0, maxw=860)


def scene_loss(d, lt, D):
    rrect(d, 0, 0, 1080, 1920, 0, (90, 80, 90), 0.06 * ease(prog(lt, 0, 0.8)))
    atext(d, "Tapi ajal tiada siapa tahu...", 540, 260, F("xb", 64), INK, lt, 0.2, maxw=980)
    sa = ease(prog(lt, 0.6, 1.2))
    if sa > 0:
        silhouette(d, 400, 800, 1.05, TEAL_L, 0.9 * sa)
    p = ease_back(prog(lt, 1.0, 0.7))
    if p > 0:
        person(d, 640, 840, 1.0 * p, "sad", shirt=CORAL, hijab=TEAL_D)
        person(d, 470, 960, 0.6 * p, "sad", shirt=GOLD)
        person(d, 800, 975, 0.55 * p, "sad", shirt=(120, 110, 200))
    atext(d, "Bila ketua keluarga meninggal dunia, keluarga perlu meneruskan hidup.", 540, 1250, F("sb", 54),
          INK, lt, 1.6, maxw=880)
    atext(d, "Siapa yang akan menanggung mereka?", 540, 1500, F("m", 48), SOFT, lt, 2.6, maxw=880)


PROBLEMS = ["Tuntutan harta pusaka boleh ambil masa berbulan, malah bertahun",
            "Akaun & harta si mati mungkin dibekukan sementara",
            "Sedangkan keluarga perlukan wang segera untuk belanja harian"]


def scene_problems(d, lt, D):
    atext(d, "Tanpa perancangan...", 540, 220, F("xb", 74), CORAL, lt, 0.2)
    p = ease_back(prog(lt, 0.4, 0.7))
    if p > 0:
        locked_doc(d, 540, 510, 150 * p)
    for i, item in enumerate(PROBLEMS):
        e = ease(prog(lt, 1.2 + i * 0.9, 0.6))
        if e <= 0:
            continue
        o = (1 - e) * 500
        y0 = 760 + i * 200
        card(d, 90 + o, y0, 990 + o, y0 + 170, 32, e)
        x_icon(d, 165 + o, y0 + 85, 36, e)
        f = F("sb", 42)
        n = len(wrap(item, f, 720))
        text(d, item, 225 + o, y0 + 85 - n * 42 * 1.2 / 2, f, INK, e, maxw=720, align="left", lh=1.2)
    atext(d, "Keluarga mungkin terpaksa berhutang atau bergantung pada orang lain.", 540, 1400, F("m", 46), SOFT,
          lt, 4.2, maxw=860)


def scene_what(d, lt, D):
    pill(d, 540, 200, "HIBAH = HADIAH", F("xb", 42), WHITE, TEAL, ease(prog(lt, 0.1, 0.4)), h=88)
    atext(d, "Apa itu Hibah Takaful?", 540, 320, F("xb", 72), INK, lt, 0.3, maxw=900)
    p = ease_back(prog(lt, 0.6, 0.6))
    if p > 0:
        person(d, 230, 720, 0.9 * p, "happy", shirt=TEAL)
        person(d, 830, 730, 0.85 * p, "happy", shirt=CORAL, hijab=TEAL_D)
        person(d, 950, 820, 0.5 * p, "happy", shirt=GOLD)
        d.text((X(230), X(900)), "Anda", font=F("b", 36), fill=col(INK, p), anchor="mm")
        d.text((X(860), X(920)), "Penerima hibah", font=F("b", 36), fill=col(INK, p), anchor="mm")
    m = ease(prog(lt, 1.4, 1.6))
    if lt > 1.2:
        d.line([(X(340), X(640)), (X(720), X(640))], fill=col(TEAL_L), width=X(10))
        d.polygon([(X(740), X(640)), (X(712), X(620)), (X(712), X(660))], fill=col(TEAL_L))
        gx = 340 + 330 * m
        gift(d, gx, 600 - 60 * math.sin(math.pi * m), 62 * ease_back(prog(lt, 1.2, 0.4)))
    atext(d, "Anda menamakan penerima hibah, contohnya isteri atau anak.", 540, 1020, F("sb", 52), INK, lt, 1.8,
          maxw=880)
    atext(d, "Bila berlaku kematian, manfaat takaful dibayar terus kepada mereka sebagai hadiah.", 540, 1250,
          F("m", 48), SOFT, lt, 3.2, maxw=860)


def make_checklist(title, sub, items, foot, extra=None):
    def scene(d, lt, D):
        atext(d, title, 540, 220, F("xb", 74), INK, lt, 0.2, maxw=920)
        atext(d, sub, 540, 330, F("m", 42), SOFT, lt, 0.4, maxw=900)
        for i, label in enumerate(items):
            e = ease(prog(lt, 1.0 + i * 0.85, 0.6))
            if e <= 0:
                continue
            o = (1 - e) * 500
            y0 = 450 + i * 170
            card(d, 90 + o, y0, 990 + o, y0 + 140, 32, e)
            check_icon(d, 165 + o, y0 + 70, 36, e)
            f = F("sb", 42)
            n = len(wrap(label, f, 720))
            text(d, label, 225 + o, y0 + 70 - n * 42 * 1.2 / 2, f, INK, e, maxw=720, align="left", lh=1.2)
        y_foot = 450 + len(items) * 170 + 10
        atext(d, foot, 540, y_foot, F("r", 32), SOFT, lt, 1.0 + len(items) * 0.85, maxw=880)
        if extra:
            extra(d, lt, y_foot + 120)
    return scene


def benefits_extra(d, lt, y):
    s = ease_back(prog(lt, 5.4, 0.7))
    if s > 0:
        gift(d, 540, y + 140, 110 * s)


def scene_hope(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    circle(d, 540, 760, 330 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.6)
    if p > 0:
        family(d, 540, 760, p * 1.2, "happy", with_father=False)
        gift(d, 540, 400, 58 * p)
    hp = ease_back(prog(lt, 1.0, 0.6))
    if hp > 0:
        heart(d, 300, 520 + 8 * math.sin(lt * 3), 60 * hp, TEAL)
        heart(d, 790, 500 + 8 * math.sin(lt * 3 + 1), 48 * hp, CORAL)
    atext(d, "Walaupun Ali telah tiada, keluarganya tetap terbela.", 540, 1170, F("xb", 66), INK, lt, 0.8,
          maxw=900)
    atext(d, "Hibah: tanda kasih yang berterusan.", 540, 1400, F("sb", 54), TEAL, lt, 1.8, maxw=900)


def make_tips(title, items, foot):
    def scene(d, lt, D):
        atext(d, title, 540, 240, F("xb", 72), INK, lt, 0.2, maxw=920)
        for i, tip in enumerate(items):
            e = ease(prog(lt, 0.9 + i * 0.8, 0.6))
            if e <= 0:
                continue
            y0 = 440 + i * 215
            o = (1 - e) * 60
            card(d, 90, y0 + o, 990, y0 + 180 + o, 32, e)
            circle(d, 175, y0 + 90 + o, 46, TEAL, e)
            d.text((X(175), X(y0 + 90 + o)), str(i + 1), font=F("xb", 50), fill=col(WHITE, e), anchor="mm")
            f = F("sb", 42)
            n = len(wrap(tip, f, 700))
            text(d, tip, 255, y0 + 90 + o - n * 42 * 1.22 / 2, f, INK, e, maxw=700, align="left", lh=1.22)
        atext(d, foot, 540, 440 + len(items) * 215 + 30, F("m", 42), SOFT, lt, 0.9 + len(items) * 0.8, maxw=860)
    return scene


def scene_cta(d, lt, D):
    s = ease(prog(lt, 0.2, 0.8))
    if s > 0:
        shield(d, 540, 790, 330 * (0.8 + 0.2 * s), 0.25 * s, fill=TEAL, inner=TEAL_L, cross=False)
    p = ease_back(prog(lt, 0.4, 0.7))
    if p > 0:
        family(d, 540, 800, p * 1.1)
    hp = ease_back(prog(lt, 1.0, 0.6))
    if hp > 0:
        heart(d, 540, 520 + 8 * math.sin(lt * 3), 90 * hp, TEAL)
    atext(d, "Sayangi keluarga,", 540, 1150, F("xb", 84), INK, lt, 1.2)
    atext(d, "rancang dari sekarang.", 540, 1260, F("xb", 84), TEAL, lt, 1.5, maxw=940)


# ---------------------------------------------------------------- variasi: tanpa vs dengan hibah
def make_compare(heading, rows, footer):
    def scene(d, lt, D):
        atext(d, heading, 540, 170, F("xb", 64), INK, lt, 0.1, maxw=940)
        cols = [(70, 525, "TANPA HIBAH", GREY, "sad", 0.4), (555, 1010, "DENGAN HIBAH", TEAL, "happy", 0.7)]
        for side, (x0, x1, hdr, c, mood, st) in enumerate(cols):
            cx = (x0 + x1) / 2
            p = ease_back(prog(lt, st, 0.6))
            if p > 0:
                person(d, cx - 45, 480, 0.85 * p, mood, shirt=c, hijab=TEAL_D)
                person(d, cx + 85, 545, 0.5 * p, mood, shirt=GOLD if side else GREY)
            e = ease(prog(lt, st + 0.2, 0.5))
            if e > 0:
                rrect(d, x0, 670, x1, 765, 30, c, e)
                d.text((X(cx), X(717)), hdr, font=F("xb", 40), fill=col(WHITE, e), anchor="mm")
        for i, (left, right) in enumerate(rows):
            y0 = 800 + i * 250
            for side, (x0, x1, txt, st) in enumerate([(70, 525, left, 1.5 + i * 1.5),
                                                      (555, 1010, right, 2.1 + i * 1.5)]):
                e = ease(prog(lt, st, 0.5))
                if e <= 0:
                    continue
                o = (1 - e) * 40
                cx = (x0 + x1) / 2
                card(d, x0, y0 + o, x1, y0 + 225 + o, 30, e)
                if side == 0:
                    x_icon(d, cx, y0 + 52 + o, 30, e, GREY)
                else:
                    check_icon(d, cx, y0 + 52 + o, 30, e)
                f = F("sb", 40)
                hh = len(wrap(txt, f, 390)) * 40 * 1.22
                text(d, txt, cx, y0 + 150 + o - hh / 2, f, INK, e, maxw=390, lh=1.22)
        atext(d, footer, 540, 1590, F("xb", 58), TEAL_D, lt, 6.6, maxw=900)
    return scene


def scene_gift_close(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    pulse_rings(d, 540, 640, 220, lt)
    circle(d, 540, 640, 220 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.7)
    if p > 0:
        gift(d, 540, 660, 120 * p)
    y = atext(d, "Hibah takaful: hadiah terakhir untuk orang tersayang.", 540, 960, F("xb", 70), INK, lt, 0.6,
              maxw=900)
    atext(d, "Kasih anda terus melindungi mereka.", 540, y + 50, F("sb", 54), TEAL, lt, 1.2, maxw=900)


# ---------------------------------------------------------------- senarai
HIBAH_MYTHS = [
    ("“Harta saya sikit, tak perlu hibah.”",
     "Hibah bukan untuk orang kaya sahaja. Ia menyediakan wang tunai segera supaya keluarga tidak terbeban."),
    ("“Keluarga boleh tuntut harta pusaka nanti.”",
     "Proses pusaka boleh mengambil masa yang lama. Manfaat hibah takaful dibayar terus kepada penerima yang "
     "dinamakan."),
    ("“Hibah sama je dengan faraid.”",
     "Faraid membahagikan harta pusaka mengikut hukum. Manfaat hibah pula diberikan sebagai hadiah kepada penerima "
     "yang anda pilih."),
    ("“Saya masih muda, nanti-nanti la.”",
     "Ajal tak kenal usia. Caruman biasanya lebih rendah bila mula awal, semasa muda dan sihat."),
]

HIBAH_BENEFITS = ["Wang tunai terus kepada penerima yang anda pilih", "Tak perlu tunggu proses harta pusaka",
                  "Manfaat hibah tidak termasuk dalam pembahagian faraid",
                  "Boleh langsaikan hutang & kos pengurusan jenazah", "Jamin pendidikan & masa depan anak-anak"]

HIBAH_TIPS = ["Pastikan penamaan dibuat sebagai penerima hibah", "Kemas kini penama bila berkahwin atau dapat anak",
              "Pilih jumlah perlindungan ikut keperluan keluarga", "Beritahu keluarga tentang pelan anda"]

HIBAH_ROWS = [("Tunggu proses pusaka yang lama", "Wang dibayar terus kepada penerima"),
              ("Susah nak tampung belanja harian", "Ada dana segera untuk keluarga"),
              ("Hutang jadi beban waris", "Boleh langsaikan hutang")]

NEW = {
    "hibah_cerita": ("hibah_1_cerita.mp4",
                     [(4.5, make_intro("TAHUKAH ANDA?", "Apa itu", "Hibah Takaful?",
                                       "Hadiah terakhir untuk orang tersayang", icon_gift)),
                      (5.5, scene_family), (6.0, scene_loss), (7.0, scene_problems), (7.5, scene_what),
                      (9.0, make_checklist("Kelebihan Hibah Takaful", "Kenapa ramai memilih hibah:", HIBAH_BENEFITS,
                                           "*Tertakluk kepada terma & syarat pelan serta penamaan yang sah.",
                                           benefits_extra)),
                      (6.0, scene_hope),
                      (7.5, make_tips("Perkara penting:", HIBAH_TIPS,
                                      "Bincang dengan ejen untuk pilih pelan yang sesuai.")),
                      (5.5, scene_cta), (7.5, scene_agent)],
                     ["C", "Am", "F", "Am", "Dm", "F", "E", "Am", "F", "G", "C", "Am", "F", "G", "C", "Am", "F", "G",
                      "C", "Am", "F", "G", "C"]),
    "hibah_mitos": ("hibah_2_mitos_fakta.mp4",
                    [(4.0, make_intro("MITOS vs FAKTA", "Hibah", "Takaful", "Yang mana pernah anda dengar?",
                                      va.icon_myth))]
                    + [(7.0, make_myth(i + 1, m, f)) for i, (m, f) in enumerate(HIBAH_MYTHS)]
                    + [(7.5, scene_agent)],
                    ["Am", "F", "C", "G"] * 4),
    "hibah_banding": ("hibah_3_tanpa_vs_dengan.mp4",
                      [(4.0, make_intro("TANPA vs DENGAN", "Bila ketua keluarga tiada, apa", "bezanya?",
                                        "Ada dan tiada hibah takaful", va.icon_versus)),
                       (11.0, make_compare("Bila ketua keluarga tiada...", HIBAH_ROWS, "Bezanya besar, bukan?")),
                       (5.0, scene_gift_close), (7.5, scene_agent)],
                      ["Am", "F", "Dm", "E", "F", "G", "C", "Am", "F", "G", "C", "C"]),
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
