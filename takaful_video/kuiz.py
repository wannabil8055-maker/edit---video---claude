"""Kuiz 'Adakah anda perlukan ...?' untuk kad perubatan, penyakit kritikal & hibah.

Guna:  python3 kuiz.py                  -> render semua
       python3 kuiz.py --preview kuiz_medical 3 7
"""
import math
import os
import sys

import variasi as va
from make_video import (F, X, col, prog, ease, ease_back, wrap, text, atext, rrect, card, circle, check_icon,
                        person, pill, scene_agent, INK, SOFT, TEAL, TEAL_D, TEAL_L, WHITE)
from variasi import make_intro, GREY
from hibah import icon_gift
from ci import icon_heartbeat
from versi_chat import icon_medical

HERE = os.path.dirname(os.path.abspath(__file__))


def icon_quiz(d, cx, cy, p):
    rrect(d, cx - 150 * p, cy - 180 * p, cx + 150 * p, cy + 190 * p, 30 * p, WHITE)
    rrect(d, cx - 70 * p, cy - 210 * p, cx + 70 * p, cy - 150 * p, 20 * p, TEAL)
    for k in range(3):
        y = cy - 90 * p + k * 100 * p
        rrect(d, cx - 110 * p, y - 28 * p, cx - 54 * p, y + 28 * p, 10 * p, TEAL_L)
        rrect(d, cx - 30 * p, y - 10 * p, cx + 110 * p - (40 * p if k == 2 else 0), y + 10 * p, 8 * p, TEAL_L)
        if k < 2 and p > 0.7:
            d.line([(X(cx - 100), X(y)), (X(cx - 85), X(y + 15)), (X(cx - 60), X(y - 18))], fill=col(TEAL),
                   width=X(9), joint="curve")


def make_question(n, total, q):
    def scene(d, lt, D):
        pill(d, 540, 200, f"SOALAN {n}/{total}", F("xb", 40), WHITE, TEAL, ease(prog(lt, 0.05, 0.3)), h=84)
        tapped = lt > 2.3
        for k in range(total):
            filled = k < n - 1 or (k == n - 1 and tapped)
            circle(d, 540 - (total - 1) * 30 + k * 60, 330, 14, TEAL if filled else TEAL_L)
        e = ease(prog(lt, 0.15, 0.5))
        if e > 0:
            o = (1 - e) * 50
            card(d, 90, 430 + o, 990, 880 + o, 44, e)
            circle(d, 540, 430 + o, 56, TEAL, e)
            d.text((X(540), X(432 + o)), "?", font=F("xb", 70), fill=col(WHITE, e), anchor="mm")
            f = F("xb", 58)
            hh = len(wrap(q, f, 800)) * 58 * 1.25
            text(d, q, 540, 670 + o - hh / 2, f, INK, e, maxw=800)
        b = ease(prog(lt, 0.6, 0.4))
        if b > 0:
            pop = 1 + 0.08 * math.sin(math.pi * prog(lt, 2.3, 0.3)) if tapped else 1
            cx, cy, hw, hh = 315, 1075, 195 * pop, 75 * pop
            rrect(d, cx - hw, cy - hh, cx + hw, cy + hh, 40, TEAL_D if tapped else TEAL, b)
            d.text((X(cx), X(cy)), "YA", font=F("xb", 58), fill=col(WHITE, b), anchor="mm")
            rrect(d, 570, 1000, 960, 1150, 40, WHITE, b, outline=GREY, width=4)
            d.text((X(765), X(1075)), "TIDAK", font=F("xb", 52), fill=col(SOFT, b), anchor="mm")
            if tapped:
                check_icon(d, cx + hw - 10, cy - hh + 10, 34 * ease_back(prog(lt, 2.35, 0.4)), 1.0, bg=(46, 170, 90))
        # penunjuk jari bergerak & tekan YA
        m = ease(prog(lt, 1.4, 0.9))
        if 1.2 < lt < 3.1:
            px, py = 820 + (420 - 820) * m, 1500 + (1130 - 1500) * m
            a = min(1.0, (lt - 1.2) / 0.3) * min(1.0, (3.1 - lt) / 0.3)
            if tapped:
                r = prog(lt, 2.3, 0.6)
                circle(d, px, py, 40 + 90 * r, None, a=(1 - r) * a, outline=WHITE, width=8)
            circle(d, px, py + 6, 42, INK, 0.15 * a)
            circle(d, px, py, 40, WHITE, a)
            circle(d, px, py, 26, TEAL_L, a)
        pa = ease_back(prog(lt, 0.4, 0.6))
        if pa > 0:
            person(d, 540, 1560, 0.85 * pa, "happy")
            if not tapped:
                circle(d, 660, 1360, 40 * pa, WHITE)
                d.text((X(660), X(1362)), "?", font=F("xb", 52), fill=col(TEAL, pa), anchor="mm")
            else:
                circle(d, 660, 1360, 40, (46, 170, 90))
                check_icon(d, 660, 1360, 40, 1.0, bg=(46, 170, 90))
    return scene


def make_result(plan, sub, icon):
    def scene(d, lt, D):
        atext(d, "Jawab YA walaupun sekali?", 540, 260, F("sb", 58), SOFT, lt, 0.2, maxw=920)
        circle(d, 540, 700, 270 * ease_back(prog(lt, 0.3, 0.6)), WHITE, 0.7)
        p = ease_back(prog(lt, 0.5, 0.7))
        if p > 0:
            icon(d, 540, 700, p)
        y = atext(d, "Anda perlukan", 540, 1040, F("xb", 72), INK, lt, 0.9)
        y = atext(d, plan, 540, y, F("xb", 92), TEAL, lt, 1.2, maxw=960)
        atext(d, sub, 540, y + 40, F("m", 48), SOFT, lt, 1.7, maxw=860)
    return scene


QUIZZES = {
    "kuiz_medical": ("kuiz_1_kad_perubatan.mp4", "Kad Perubatan?", "Kad Perubatan",
                     "Supaya bil hospital tak jadi beban anda & keluarga.", icon_medical,
                     ["Anda bergantung pada medical card majikan sahaja?",
                      "Simpanan anda tak cukup untuk bil hospital puluhan ribu?",
                      "Anda mahu pilihan hospital swasta bila sakit?",
                      "Ada keluarga yang bergantung pada anda?",
                      "Anda tak mahu risau soal bil ketika sakit?"],
                     ["F", "G", "C", "Am"] * 4),
    "kuiz_ci": ("kuiz_2_penyakit_kritikal.mp4", "Pelan Penyakit Kritikal?", "Pelan Penyakit Kritikal",
                "Supaya pendapatan & komitmen anda terus terjaga semasa pulih.", icon_heartbeat,
                ["Anda ada ansuran rumah atau kereta?",
                 "Pendapatan anda terhenti jika tak boleh bekerja?",
                 "Ada sejarah penyakit kritikal dalam keluarga?",
                 "Simpanan anda tak cukup untuk setahun tanpa gaji?",
                 "Anda mahu fokus sembuh tanpa tekanan kewangan?"],
                ["C", "G", "Am", "F"] * 4),
    "kuiz_hibah": ("kuiz_3_hibah.mp4", "Hibah Takaful?", "Hibah Takaful",
                   "Supaya orang tersayang terus terbela, walaupun anda tiada.", icon_gift,
                   ["Anda sudah berkahwin atau ada anak?",
                    "Ada orang yang bergantung pada pendapatan anda?",
                    "Anda ada hutang seperti pinjaman rumah atau kereta?",
                    "Anda mahu keluarga terima wang tanpa tunggu proses pusaka?",
                    "Anda mahu pendidikan anak-anak terjamin?"],
                   ["Am", "F", "C", "G"] * 4),
}

NEW = {}
for key, (fname, accent, plan, sub, icon, qs, chords) in QUIZZES.items():
    NEW[key] = (fname,
                [(4.0, make_intro("KUIZ 30 SAAT", "Adakah anda perlukan", accent, "Jawab 5 soalan ringkas ini",
                                  icon_quiz))]
                + [(4.0, make_question(i + 1, len(qs), q)) for i, q in enumerate(qs)]
                + [(5.5, make_result(plan, sub, icon)), (7.5, scene_agent)],
                chords)
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
