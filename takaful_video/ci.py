"""Video kesedaran: Kepentingan Perlindungan Penyakit Kritikal (cerita utama + 2 variasi).

Guna:  python3 ci.py                    -> render semua
       python3 ci.py ci_cerita          -> render satu
       python3 ci.py --preview ci_cerita 3.0 12.0
"""
import math
import os
import sys

import variasi as va
from make_video import (F, X, col, prog, ease, ease_back, wrap, text, atext, rrect, card, circle, check_icon, shield,
                        heart, sparkle, person, pill, hospital, scene_agent, INK, SOFT, TEAL, TEAL_D, TEAL_L, CORAL,
                        GOLD, WHITE)
from variasi import x_icon, pulse_rings, make_intro, make_myth, coin_stack, GREY
from hibah import make_checklist, make_tips, make_compare, family
import hibah  # noqa: F401  (daftar variasi hibah juga, tidak dirender di sini)

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- ikon
def ecg_line(d, cx, cy, w, h, a=1.0, c=WHITE, width=12):
    pts = [(-0.5, 0), (-0.2, 0), (-0.12, -0.35), (-0.04, 0.45), (0.06, -0.7), (0.15, 0), (0.5, 0)]
    d.line([(X(cx + px * w), X(cy + py * h)) for px, py in pts], fill=col(c, a), width=X(width), joint="curve")


def icon_heartbeat(d, cx, cy, p):
    heart(d, cx, cy - 20, 280 * p, TEAL)
    if p > 0.6:
        ecg_line(d, cx, cy + 10, 300, 110)


def house(d, cx, cy, s, a=1.0):
    rrect(d, cx - s, cy - 0.25 * s, cx + s, cy + s, 0.08 * s, WHITE, a)
    d.polygon([(X(cx - 1.25 * s), X(cy - 0.15 * s)), (X(cx), X(cy - 1.1 * s)), (X(cx + 1.25 * s), X(cy - 0.15 * s))],
              fill=col(TEAL, a))
    rrect(d, cx - 0.25 * s, cy + 0.35 * s, cx + 0.25 * s, cy + s, 0.06 * s, TEAL_D, a)
    rrect(d, cx + 0.45 * s, cy + 0.05 * s, cx + 0.8 * s, cy + 0.4 * s, 0.05 * s, TEAL_L, a)


def car(d, cx, cy, s, a=1.0):
    rrect(d, cx - 0.7 * s, cy - 0.7 * s, cx + 0.55 * s, cy - 0.05 * s, 0.25 * s, CORAL, a)
    rrect(d, cx - 0.55 * s, cy - 0.58 * s, cx + 0.42 * s, cy - 0.15 * s, 0.12 * s, TEAL_L, a)
    rrect(d, cx - 1.2 * s, cy - 0.25 * s, cx + 1.2 * s, cy + 0.4 * s, 0.22 * s, CORAL, a)
    circle(d, cx - 0.65 * s, cy + 0.42 * s, 0.25 * s, INK, a)
    circle(d, cx + 0.65 * s, cy + 0.42 * s, 0.25 * s, INK, a)


def report(d, cx, cy, s, a=1.0):
    rrect(d, cx - 0.8 * s, cy - s, cx + 0.8 * s, cy + s, 0.12 * s, WHITE, a)
    rrect(d, cx - 0.8 * s, cy - s, cx + 0.8 * s, cy - 0.55 * s, 0.12 * s, TEAL, a)
    rrect(d, cx - 0.06 * s, cy - 0.92 * s, cx + 0.06 * s, cy - 0.63 * s, 0.02 * s, WHITE, a)
    rrect(d, cx - 0.2 * s, cy - 0.83 * s, cx + 0.2 * s, cy - 0.72 * s, 0.02 * s, WHITE, a)
    for k in range(4):
        rrect(d, cx - 0.55 * s, cy - 0.3 * s + k * 0.3 * s, cx + 0.55 * s - (0.35 * s if k == 3 else 0),
              cy - 0.2 * s + k * 0.3 * s, 0.05 * s, TEAL_L, a)


# ---------------------------------------------------------------- babak cerita utama
def scene_ali(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    circle(d, 540, 780, 330 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.6)
    if p > 0:
        person(d, 540, 800, 1.45 * p, "happy", wave_ang=math.radians(60 + 25 * math.sin(lt * 7)))
    hp = ease_back(prog(lt, 0.8, 0.6))
    if hp > 0:
        house(d, 210, 560, 85 * hp)
    cp = ease_back(prog(lt, 1.1, 0.6))
    if cp > 0:
        car(d, 880, 600, 80 * cp)
    atext(d, "Ini Ali, 35 tahun.", 540, 1180, F("xb", 84), INK, lt, 0.6)
    atext(d, "Bekerja keras, bayar ansuran rumah & kereta, dan sara keluarga.", 540, 1300, F("m", 50), SOFT, lt,
          1.0, maxw=860)


def scene_diagnosis(d, lt, D):
    rrect(d, 0, 0, 1080, 1920, 0, CORAL, 0.05 * ease(prog(lt, 0, 0.6)))
    atext(d, "Satu hari, doktor memberi berita...", 540, 230, F("xb", 66), INK, lt, 0.2, maxw=940)
    p = ease_back(prog(lt, 0.5, 0.6))
    if p > 0:
        report(d, 540, 560, 150 * p)
    for i, (lbl, x) in enumerate([("Kanser", 230), ("Serangan jantung", 540), ("Strok", 850)]):
        e = ease_back(prog(lt, 1.2 + i * 0.35, 0.5))
        if e > 0:
            f = F("b", 36)
            w = (f.getlength(lbl) / 2 + 60) * e
            rrect(d, x - w / 2, 800, x + w / 2, 876, 38, CORAL, 1.0)
            if e > 0.8:
                d.text((X(x), X(838)), lbl, font=f, fill=col(WHITE), anchor="mm")
    pp = ease_back(prog(lt, 1.6, 0.6))
    if pp > 0:
        person(d, 540, 1150, 1.05 * pp, "sad")
        circle(d, 640, 1010 + 30 * ((lt * 0.8) % 1), 13 * pp, (120, 190, 235), 0.9)
    atext(d, "Penyakit kritikal boleh menimpa sesiapa sahaja, pada bila-bila masa.", 540, 1440, F("sb", 50), INK,
          lt, 2.2, maxw=880)


CI_PROBLEMS = ["Perlu berhenti kerja berbulan-bulan untuk rawatan & pemulihan",
               "Pendapatan terhenti, tapi ansuran & bil tetap perlu dibayar",
               "Kos ubat, terapi & penjagaan di rumah"]


def scene_problems(d, lt, D):
    atext(d, "Bukan sekadar bil hospital...", 540, 220, F("xb", 68), CORAL, lt, 0.2, maxw=940)
    p = ease_back(prog(lt, 0.4, 0.6))
    if p > 0:
        n = max(1, 7 - int(max(0, lt - 1.5) * 1.6))
        coin_stack(d, 460, 640, n)
        coin_stack(d, 610, 640, max(1, n - 2))
        if lt > 1.5:
            x_icon(d, 720, 430, 40 * ease_back(prog(lt, 1.5, 0.4)))
    for i, item in enumerate(CI_PROBLEMS):
        e = ease(prog(lt, 1.2 + i * 0.9, 0.6))
        if e <= 0:
            continue
        o = (1 - e) * 500
        y0 = 760 + i * 200
        card(d, 90 + o, y0, 990 + o, y0 + 170, 32, e)
        x_icon(d, 165 + o, y0 + 85, 36, e)
        f = F("sb", 42)
        n_l = len(wrap(item, f, 720))
        text(d, item, 225 + o, y0 + 85 - n_l * 42 * 1.2 / 2, f, INK, e, maxw=720, align="left", lh=1.2)
    atext(d, "Simpanan bertahun boleh habis dalam masa singkat.", 540, 1400, F("m", 46), SOFT, lt, 4.2, maxw=860)


def scene_what(d, lt, D):
    pill(d, 540, 200, "WANG TUNAI SEKALIGUS", F("xb", 40), WHITE, TEAL, ease(prog(lt, 0.1, 0.4)), h=88)
    atext(d, "Apa itu perlindungan penyakit kritikal?", 540, 320, F("xb", 64), INK, lt, 0.3, maxw=940)
    p = ease_back(prog(lt, 0.6, 0.6))
    if p > 0:
        report(d, 230, 720, 110 * p)
        person(d, 840, 740, 0.9 * p, "happy")
        d.text((X(230), X(880)), "Disahkan", font=F("b", 36), fill=col(INK, p), anchor="mm")
        d.text((X(840), X(920)), "Anda", font=F("b", 36), fill=col(INK, p), anchor="mm")
    if lt > 1.3:
        d.line([(X(340), X(640)), (X(700), X(640))], fill=col(TEAL_L), width=X(10))
        d.polygon([(X(720), X(640)), (X(692), X(620)), (X(692), X(660))], fill=col(TEAL_L))
        for k in range(3):
            ph = ((lt - 1.4 - k * 0.35) % 1.2) / 1.2
            if lt - 1.4 - k * 0.35 < 0:
                continue
            gx = 340 + 360 * ease(ph)
            va.coin(d, gx, 600 - 60 * math.sin(math.pi * ease(ph)), 26, 1 - ph ** 4)
        n = int(1 + 5 * prog(lt, 1.6, 2.0))
        coin_stack(d, 650, 880, n, w=100)
    atext(d, "Bila disahkan menghidap penyakit kritikal yang dilindungi, anda menerima wang tunai sekaligus.", 540,
          1020, F("sb", 50), INK, lt, 1.8, maxw=880)
    atext(d, "Wang ini milik anda. Guna untuk apa sahaja keperluan.", 540, 1290, F("m", 48), SOFT, lt, 3.4,
          maxw=860)


CI_USES = ["Ganti pendapatan semasa berehat & pulih", "Bayar ansuran rumah, kereta & bil bulanan",
           "Rawatan tambahan yang tidak dilindungi kad perubatan", "Ubat, terapi & penjagaan di rumah",
           "Perbelanjaan harian keluarga"]


def uses_extra(d, lt, y):
    s = ease_back(prog(lt, 5.4, 0.7))
    if s > 0:
        coin_stack(d, 470, y + 230, max(1, int(6 * s)), w=110)
        coin_stack(d, 610, y + 230, max(1, int(4 * s)), w=110)


def scene_vs_medical(d, lt, D):
    atext(d, "Beza dengan kad perubatan?", 540, 220, F("xb", 70), INK, lt, 0.2, maxw=940)
    rows = [(420, "KAD PERUBATAN", "Bayar bil hospital, terus kepada hospital panel.", "hosp", 0.6),
            (880, "PENYAKIT KRITIKAL", "Bayar wang tunai sekaligus, terus kepada anda.", "coin", 1.6)]
    for y0, lbl, desc, ic, st in rows:
        e = ease(prog(lt, st, 0.6))
        if e <= 0:
            continue
        o = (1 - e) * 60
        card(d, 90, y0 + o, 990, y0 + 380 + o, 40, e)
        circle(d, 250, y0 + 190 + o, 115, TEAL_L, e)
        if ic == "hosp":
            hospital(d, 250, y0 + 280 + o, 0.5, e)
        else:
            coin_stack(d, 250, y0 + 255 + o, 4, w=110)
        f = F("xb", 40)
        w = f.getlength(lbl) / 2 + 60
        rrect(d, 400, y0 + 80 + o, 400 + w, y0 + 156 + o, 38, TEAL, e)
        d.text((X(400 + w / 2), X(y0 + 118 + o)), lbl, font=f, fill=col(WHITE, e), anchor="mm")
        text(d, desc, 400, y0 + 190 + o, F("sb", 44), INK, e, maxw=550, align="left", lh=1.22)
    y = atext(d, "Kedua-duanya saling melengkapi.", 540, 1350, F("xb", 60), TEAL_D, lt, 3.0, maxw=900)
    atext(d, "Satu untuk bil hospital, satu untuk kehidupan anda.", 540, max(y, 1430) + 20, F("m", 46), SOFT, lt, 3.5, maxw=860)


def scene_hope(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    circle(d, 540, 780, 330 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.6)
    if p > 0:
        family(d, 540, 760, p * 1.2)
    for i, (sx, sy) in enumerate([(250, 500), (830, 480)]):
        sparkle(d, sx, sy, 30 * ease(prog(lt, 0.8 + 0.2 * i, 0.5)) * (1 + 0.15 * math.sin(lt * 4 + i)))
    y = atext(d, "Ali boleh fokus pada rawatan, tanpa risau soal kewangan.", 540, 1170, F("xb", 64), INK, lt,
              0.7, maxw=900)
    atext(d, "Keluarganya juga tetap stabil.", 540, max(y, 1360) + 40, F("sb", 54), TEAL, lt, 1.6, maxw=900)


def scene_cta(d, lt, D):
    s = ease(prog(lt, 0.2, 0.8))
    if s > 0:
        shield(d, 540, 760, 330 * (0.8 + 0.2 * s), 0.25 * s, fill=TEAL, inner=TEAL_L, cross=False)
    p = ease_back(prog(lt, 0.4, 0.7))
    if p > 0:
        heart(d, 540, 760, 300 * p, TEAL)
        if p > 0.6:
            ecg_line(d, 540, 790, 320, 120)
    atext(d, "Jangan tunggu sakit,", 540, 1150, F("xb", 84), INK, lt, 1.0)
    atext(d, "lindungi diri dari sekarang.", 540, 1260, F("xb", 78), TEAL, lt, 1.3, maxw=940)


def scene_close(d, lt, D):
    p = ease_back(prog(lt, 0.2, 0.7))
    pulse_rings(d, 540, 640, 220, lt)
    circle(d, 540, 640, 220 * ease_back(prog(lt, 0.1, 0.6)), WHITE, 0.7)
    if p > 0:
        icon_heartbeat(d, 540, 650, p * 0.8)
    y = atext(d, "Penyakit tak boleh dijangka.", 540, 960, F("xb", 74), INK, lt, 0.6, maxw=900)
    atext(d, "Tapi kewangan anda boleh dilindungi.", 540, y + 50, F("sb", 56), TEAL, lt, 1.2, maxw=900)


# ---------------------------------------------------------------- senarai
CI_MYTHS = [
    ("“Saya dah ada kad perubatan, cukuplah.”",
     "Kad perubatan bayar bil hospital. Perlindungan penyakit kritikal pula beri wang tunai untuk ganti pendapatan "
     "& komitmen semasa anda pulih."),
    ("“Penyakit kritikal untuk orang tua saja.”",
     "Penyakit kritikal juga boleh menyerang pada usia muda. Gaya hidup, tekanan & faktor keturunan memainkan "
     "peranan."),
    ("“Saya ada simpanan, boleh tanggung sendiri.”",
     "Rawatan & pemulihan boleh ambil masa lama. Simpanan bertahun boleh habis dalam masa yang singkat."),
    ("“Nanti dah sakit, baru daftar.”",
     "Penyakit sedia ada biasanya tidak dilindungi. Daftar semasa sihat supaya anda layak dilindungi."),
]

CI_TIPS = ["Semak senarai penyakit kritikal yang dilindungi", "Faham tempoh menunggu sebelum perlindungan bermula",
           "Pilih jumlah perlindungan ikut pendapatan & komitmen", "Daftar awal, semasa masih sihat"]

CI_ROWS = [("Pendapatan terhenti semasa rawatan", "Wang tunai ganti pendapatan"),
           ("Simpanan habis untuk komitmen", "Ansuran & bil tetap dibayar"),
           ("Tertekan memikirkan kewangan", "Fokus pada rawatan & pemulihan")]

NEW = {
    "ci_cerita": ("ci_1_cerita.mp4",
                  [(4.5, make_intro("TAHUKAH ANDA?", "Kenapa perlu perlindungan", "Penyakit Kritikal?",
                                    "Bila sakit serius, pendapatan pun terjejas", icon_heartbeat)),
                   (5.5, scene_ali), (5.5, scene_diagnosis), (7.0, scene_problems), (7.5, scene_what),
                   (9.0, make_checklist("Guna wang ini untuk:", "Contoh kegunaan bayaran penyakit kritikal:",
                                        CI_USES, "*Tertakluk kepada senarai penyakit, terma & syarat pelan.",
                                        uses_extra)),
                   (7.5, scene_vs_medical), (5.5, scene_hope),
                   (7.5, make_tips("Perkara penting:", CI_TIPS, "Bincang dengan ejen untuk pilih pelan yang sesuai.")),
                   (5.5, scene_cta), (7.5, scene_agent)],
                  ["C", "Am", "F", "G", "Am", "Dm", "E", "Am", "F", "G", "C", "Am", "F", "G", "C", "Am", "F", "G",
                   "C", "Am", "F", "G", "C", "C", "C"]),
    "ci_mitos": ("ci_2_mitos_fakta.mp4",
                 [(4.0, make_intro("MITOS vs FAKTA", "Perlindungan", "Penyakit Kritikal",
                                   "Yang mana pernah anda dengar?", va.icon_myth))]
                 + [(7.0, make_myth(i + 1, m, f)) for i, (m, f) in enumerate(CI_MYTHS)] + [(7.5, scene_agent)],
                 ["Am", "F", "C", "G"] * 4),
    "ci_banding": ("ci_3_tanpa_vs_dengan.mp4",
                   [(4.0, make_intro("TANPA vs DENGAN", "Bila disahkan penyakit kritikal, apa", "bezanya?",
                                     "Ada dan tiada perlindungan penyakit kritikal", va.icon_versus)),
                    (11.0, make_compare("Bila disahkan penyakit kritikal...", CI_ROWS, "Bezanya besar, bukan?",
                                        labels=("TIADA PELAN", "ADA PELAN"), single=True)),
                    (5.0, scene_close), (7.5, scene_agent)],
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
