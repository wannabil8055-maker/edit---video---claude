import os, subprocess, sys, wave, numpy as np

SRC = "/root/.claude/uploads/ffb22ac1-847d-548f-85f3-a6d14c35e14b/f1a1f2ac-525f7482-5cc2-441f-bc0b-e616bcc25e8f.mov"
W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(W, "out"); os.makedirs(OUT, exist_ok=True)
SR = 48000
FPS = 30

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)

WARM = "colorbalance=rs=0.04:bs=-0.05:rm=0.03:bm=-0.03,eq=saturation=0.92:contrast=1.04"
COLD = "colorbalance=rs=-0.05:bs=0.08:rm=-0.03:bm=0.05,eq=saturation=0.6:brightness=-0.04"
DARK = "colorbalance=rs=0.02:bs=-0.02,eq=saturation=0.72:brightness=-0.07"
VIG, VIGH = "PI/5", "PI/3.2"

# (name, src_start, src_end, zoom_start, zoom_end, grade, vignette, extra)
SEGS = [
    ("hook",  8.30, 11.05, 1.15, 1.25, WARM, VIG, ""),
    ("s2",    0.00,  2.40, 1.00, 1.04, WARM, VIG, ""),
    ("s3",    2.40,  4.90, 1.12, 1.15, WARM, VIG, ""),
    ("s4",    5.30,  7.00, 1.00, 1.04, WARM, VIG, ""),
    ("s5",    7.00, 11.90, 1.20, 1.30, WARM, VIG, ""),
    ("s6",   12.30, 15.40, 1.08, 1.14, WARM, VIG, ""),
    ("s7",   17.00, 20.00, 1.00, 1.08, COLD, VIGH, ""),
    ("s8",   20.00, 22.90, 1.15, 1.22, COLD, VIGH, ""),
    ("s9",   23.00, 24.40, 1.30, 1.40, WARM, VIG, ""),
    ("s10",  26.30, 28.40, 1.05, 1.10, WARM, VIG, ""),
    ("s11",  28.50, 31.90, 1.10, 1.22, DARK, VIGH, "reverb"),
    ("s12",  32.30, 35.90, 1.00, 1.07, WARM, VIG, ""),
    ("s13",  36.60, 37.50, 1.22, 1.24, WARM, VIG, ""),
    ("s14",  37.50, 41.40, 1.00, 1.16, DARK, VIGH, ""),
    ("s15",  41.50, 46.10, 1.08, 1.18, WARM, VIG, "freeze"),
]
CARD = 8 / 30
def q(x): return round(x * 30) / 30
FREEZE = 0.8
CTA = 9.0

# ---------- timeline ----------
starts = {}
t = CARD
for s in SEGS:
    starts[s[0]] = t
    t += q(s[2] - s[1])
    if s[7] == "freeze":
        starts["freeze"] = t; t += FREEZE
starts["cta"] = t
TOTAL = t + CTA
print("total", round(TOTAL, 2), {k: round(v, 2) for k, v in starts.items()})

# ---------- video segments ----------
CROP = "crop=320:292:20:20"
MASK = os.path.join(OUT, "mask.png")
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=white:s=1080x986:d=1", "-vf",
     "format=gray,geq=lum='255*min(1,min(min(Y/90,(H-1-Y)/90),min(X/40,(W-1-X)/40)))'", "-frames:v", "1", MASK])
files = []

def seg_video(i, s):
    name, a, b, z0, z1, grade, vig, extra = s
    d = q(b - a)
    nf = round(d * FPS); ns = nf * (SR // FPS)
    if extra == "freeze":
        nf_tot = nf + round(FREEZE * FPS); ns_tot = nf_tot * (SR // FPS)
    else:
        nf_tot, ns_tot = nf, ns
    zs = f"({z0}+({z1 - z0})*t/{d})"
    vtail, atail = "", ""
    if extra == "freeze":
        vtail = f",tpad=stop_mode=clone:stop_duration={FREEZE},hue=s=0:enable='gte(t,{d - 0.04})'"
    if extra == "reverb":
        atail = ",aecho=0.85:0.6:70|130:0.22|0.12"
    fc = (f"[0:v]fps={FPS},trim=end_frame={nf},setpts=PTS-STARTPTS,{CROP},split[a][b];"
          f"[a]scale=2104:1920,crop=1080:1920,boxblur=40:3,eq=brightness=-0.2:saturation=0.65[bg];"
          f"[b]scale=w='2*trunc(540*{zs})':h='2*trunc(493*{zs})':eval=frame:flags=lanczos,"
          f"crop=1080:986,unsharp=5:5:0.7,format=yuva420p[fg0];[1:v]format=gray,scale=1080:986[mk];"
          f"[fg0][mk]alphamerge[fg];"
          f"[bg][fg]overlay=0:330,{grade},vignette=angle={vig}{vtail},trim=end_frame={nf_tot},format=yuv420p[v];"
          f"[0:a]aresample={SR},aformat=channel_layouts=stereo,atrim=end_sample={ns},asetpts=PTS-STARTPTS,"
          f"afade=t=in:d=0.03,afade=t=out:st={d - 0.04:.3f}:d=0.04{atail},apad=whole_len={ns_tot},atrim=end_sample={ns_tot}[au]")
    out = os.path.join(OUT, f"{i:02d}_{name}.mkv")
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(a), "-t", f"{d + 0.4:.3f}", "-i", SRC, "-loop", "1", "-i", MASK,
         "-filter_complex", fc, "-map", "[v]", "-map", "[au]", "-r", str(FPS), "-frames:v", str(nf_tot),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", out])
    return out

def card(path, dur):
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=black:s=1080x1920:r={FPS}:d={dur}",
         "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-frames:v", str(round(dur * FPS)),
         "-af", f"atrim=end_sample={round(dur * FPS) * (SR // FPS)}", "-pix_fmt", "yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", path])
    return path

def cta(path, dur):
    still = os.path.join(OUT, "last.png")
    run(["ffmpeg", "-y", "-v", "error", "-ss", "45.9", "-i", SRC, "-frames:v", "1", still])
    zs = f"(1.0+0.08*t/{dur})"
    fc = (f"[0:v]fps={FPS},{CROP},scale=w='2*trunc(1052*{zs})':h='2*trunc(960*{zs})':eval=frame,"
          f"crop=2104:1920,crop=1080:1920,boxblur=30:3,hue=s=0,eq=brightness=-0.33,"
          f"vignette=angle=PI/3,format=yuv420p,fade=t=in:d=0.6[v]")
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(dur), "-i", still,
         "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-filter_complex", fc,
         "-map", "[v]", "-map", "1:a", "-frames:v", str(round(dur * FPS)), "-r", str(FPS),
         "-af", f"atrim=end_sample={round(dur * FPS) * (SR // FPS)}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", path])
    return path

if "--skip-video" not in sys.argv:
    files.append(card(os.path.join(OUT, "00_card.mkv"), CARD))
    for i, s in enumerate(SEGS, 1):
        files.append(seg_video(i, s)); print("rendered", s[0])
    files.append(cta(os.path.join(OUT, "99_cta.mkv"), CTA))
    with open(os.path.join(OUT, "list.txt"), "w") as f:
        for p in files: f.write(f"file '{p}'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "list.txt"),
         "-c", "copy", os.path.join(OUT, "base.mkv")])

# ---------- captions (ASS) ----------
GOLD, WHITE = "&H004EC1F2", "&H00FFFFFF"
def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

ev = []
def add(st, a, b, text, layer=0):
    ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{st},,0,0,0,,{text}")

POP = r"{\fscx55\fscy55\t(0,110,\fscx112\fscy112)\t(110,200,\fscx100\fscy100)}"

def cap(seg, chunks, eng=None, lead=0.05, tail=0.05, eng_style="Eng"):
    a = starts[seg] + lead
    seg_len = dict((s[0], q(s[2] - s[1])) for s in SEGS)[seg]
    b = starts[seg] + seg_len - tail
    total = sum(len(c) for c in chunks)
    t0 = a
    for c in chunks:
        d = (b - a) * len(c) / total
        words = c.split(" ")
        wl = sum(len(w) for w in words)
        k = "".join("{\\k%d}%s " % (max(1, round(d * 100 * len(w) / wl * 0.85)), w) for w in words).strip()
        add("Cap", t0, t0 + d, r"{\fad(40,0)}" + k)
        t0 += d
    if eng:
        add(eng_style, a, b, r"{\fad(80,80)}" + eng)

def segend(seg):
    return starts[seg] + dict((s[0], q(s[2] - s[1])) for s in SEGS)[seg]

# Card + hook
add("Huge", 0, CARD + 0.25, r"{\fad(60,0)}8:40", 2)
H = starts["hook"]
add("Title", H, segend("hook"), r"{\fad(80,0)}" + POP + "DOA KAU SAMPAI KE\\NKUBUR MAK AYAH…")
add("TitleGold", H + 1.25, segend("hook") + 0.2, POP + "SAAT ITU JUGA.")
cap("hook", ["8:40 juga", "mak dengan ayah", "terima pahala itu"], "It reaches their grave — that same second.")

cap("s2", ["Amalan-amalan", "ibadah"], "The worship and good deeds…")
cap("s3", ["dan kebaikan", "daripada anak…"], "…that come from a child")
cap("s4", ["Kalau anak itu", "sebut pukul 8:40…"], "If the child says it at 8:40…")
add("Big", starts["s5"], starts["s5"] + 2.2, POP + r"{\fad(0,200)}8:40", 1)
cap("s5", ["8:40 juga", "mak dengan ayah", "terima pahala itu"], "…at 8:40 the parents receive that reward")

# pending bar then TAKDA PENDING
p = starts["s6"]
add("Label", p, p + 1.45, r"{\fad(80,0)}PENDING…")
add("Shape", p, p + 1.45, r"{\an7\pos(240,215)\bord4\3c&HFFFFFF&\1a&HFF&\shad0\p1}m 0 0 l 600 0 600 44 0 44{\p0}")
add("Shape", p, p + 1.45, r"{\an7\pos(240,215)\bord0\shad0\1c" + GOLD + r"&\clip(240,215,240,259)\t(0,1300,\clip(240,215,830,259))\p1}m 0 0 l 600 0 600 44 0 44{\p0}", 1)
add("Title", p + 1.45, segend("s6"), POP + "TAKDA “PENDING”.")
cap("s6", ["Takdak", "pending-pending,", "takdak."], "No “pending”. None.")

cap("s7", ["Transaksi ibadah", "yang dilakukan"], "Every act of worship done…")
cap("s8", ["oleh anak", "dan cucu…"], "…by children and grandchildren…")
add("HugeGold", starts["s9"], segend("s9") + 0.1, POP + "SAAT ITU\\NJUGA.", 2)
add("EngMid", starts["s9"] + 0.2, segend("s9"), r"{\fad(100,0)}…goes in that very moment")
cap("s10", ["Seorang anak soleh", "kalau dia kata…"], "If a righteous child says…")

d = starts["s11"]
add("Arabic", d + 0.1, segend("s11"), r"{\fad(300,200)}رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ")
add("Rumi", d + 0.4, segend("s11"), r"{\fad(300,200)}Rabbighfir lī wa li wālidayya")
add("EngMid2", d + 0.6, segend("s11"), r"{\fad(300,200)}“My Lord, forgive me and my parents.”")

add("Title", starts["s12"], segend("s12"), POP + "9:00 PAGI →\\NTERUS SAMPAI.")
cap("s12", ["Pukul 9 pagi,", "9 pagi lah sampai", "dekat ayah dengan mak", "dalam kubur."], "At 9am, it reaches his parents in the grave")
add("BigWhite", starts["s13"], segend("s13"), POP + "BUKAN SUSAH PUN.", 1)
add("Eng", starts["s13"], segend("s13"), "It's not even hard.")
add("Title", starts["s14"] + 0.3, segend("s14"), r"{\fad(400,200)}Bila kali terakhir\Nkau doakan mereka?")
add("EngTop2", starts["s14"] + 0.6, segend("s14"), r"{\fad(400,200)}When did you last make dua for them?")
cap("s15", ["Tapi berapa ramai", "yang boleh sebut", "5 kali, 10 kali", "kepada mak ayah dia?", "…Tak ramai."],
    "But how many say it 5, 10 times for their parents?")
add("HugeWhite", starts["freeze"], starts["freeze"] + FREEZE, POP + "…TAK RAMAI.", 2)

c = starts["cta"]
add("CtaBig", c + 0.3, c + 3.0, r"{\fad(500,300)}Mak ayah kau\Ntengah tunggu.")
add("CtaEng", c + 0.6, c + 3.0, r"{\fad(500,300)}Your parents are waiting.")
add("CtaBig", c + 3.1, c + 6.2, r"{\fad(300,300)}Doakan mereka\N{\c" + GOLD + r"&}SEKARANG.")
add("ArabicCta", c + 3.5, c + 6.2, r"{\fad(400,300)}رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ")
add("CtaEng2", c + 3.7, c + 6.2, r"{\fad(400,300)}Rabbighfir lī wa li wālidayya")
add("CtaBig", c + 6.3, c + 8.4, r"{\fad(300,200)}Tulis “Ameen”\N& share pada yang\Ndah kehilangan mak/ayah.")
add("Ref", c + 6.6, c + 8.4, r"{\fad(300,200)}“…atau anak soleh yang mendoakannya.” — HR Muslim 1631")
add("Huge", c + 8.45, TOTAL, r"{\fad(150,0)}8:40", 2)
add("Credit", H, c + 8.4, "Ustadz Wadi Anuar")

HDR = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,84,{GOLD},{WHITE},&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,3,2,60,60,450,1
Style: Eng,Inter Medium,42,&H20FFFFFF,&H20FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,70,70,385,1
Style: Title,Inter Display Black,80,{WHITE},{WHITE},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,6,3,8,50,50,95,1
Style: TitleGold,Inter Display Black,96,{GOLD},{GOLD},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,6,3,8,50,50,290,1
Style: EngTop,Inter Medium,38,&H20FFFFFF,&H20FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,1305,1
Style: EngTop2,Inter Medium,38,&H20FFFFFF,&H20FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,8,60,60,300,1
Style: Label,Inter ExtraBold,48,{WHITE},{WHITE},&H00000000,&H80000000,0,0,0,0,100,100,6,0,1,4,2,8,50,50,130,1
Style: Shape,Inter,20,{WHITE},{WHITE},&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Big,Inter Display Black,200,{GOLD},{GOLD},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,9,5,8,50,50,90,1
Style: BigWhite,Inter Display Black,110,{WHITE},{WHITE},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,8,4,5,50,50,0,1
Style: Huge,Inter Display Black,280,{WHITE},{WHITE},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,0,5,50,50,0,1
Style: HugeGold,Inter Display Black,170,{GOLD},{GOLD},&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,10,6,5,50,50,0,1
Style: HugeWhite,Inter Display Black,140,{WHITE},{WHITE},&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,10,6,5,50,50,0,1
Style: EngMid,Inter Medium,46,&H10FFFFFF,&H10FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,2,2,60,60,560,1
Style: Arabic,FreeSerif,104,{GOLD},{GOLD},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,5,3,2,40,40,520,1
Style: Rumi,Inter SemiBold,48,{WHITE},{WHITE},&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,4,2,2,60,60,445,1
Style: EngMid2,Inter Medium,40,&H20FFFFFF,&H20FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,385,1
Style: CtaBig,Inter Display Black,92,{WHITE},{WHITE},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,70,70,0,1
Style: CtaEng,Inter Medium,44,&H30FFFFFF,&H30FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,70,70,700,1
Style: ArabicCta,FreeSerif,110,{GOLD},{GOLD},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,40,40,560,1
Style: CtaEng2,Inter Medium,46,&H30FFFFFF,&H30FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,70,70,480,1
Style: Ref,Inter Medium,34,&H50FFFFFF,&H50FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,80,80,520,1
Style: Credit,Inter SemiBold,32,&H30FFFFFF,&H30FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,2,1,1,44,44,640,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(os.path.join(OUT, "caps.ass"), "w", encoding="utf-8") as f:
    f.write(HDR + "\n".join(ev) + "\n")

# ---------- audio: SFX + pad ----------
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(7)

def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))

def tick():
    n = int(0.06 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * 2400 * tt) * env_exp(n, 0.008) + 0.4 * rng.standard_normal(n) * env_exp(n, 0.002)
    return 0.5 * s

def boom(dur=1.6, f0=85, f1=32, amp=0.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt / 0.25)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * env_exp(n, dur / 3.5) * np.minimum(1, tt / 0.004)

def thump(amp=0.8):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 45 + 40 * np.exp(-tt / 0.03)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.07) * np.minimum(1, tt / 0.003)

def heartbeat():
    a = thump(0.9); b = thump(0.6)
    out = np.zeros(int(0.9 * SR)); out[:len(a)] += a; o = int(0.28 * SR); out[o:o + len(b)] += b
    return out

def lp(x, a):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def whoosh(dur=0.7):
    n = int(dur * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    from numpy.fft import rfft, irfft
    spec = rfft(noise); fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((fr - 1500) / 1200) ** 2)
    s = irfft(spec, n)
    e = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 2
    return 0.35 * s / (np.abs(s).max() + 1e-9) * e

def crack():
    n = int(0.5 * SR)
    s = rng.standard_normal(n) * env_exp(n, 0.06)
    s = s - np.concatenate([[0], s[:-1]])  # highpass-ish
    for k in range(6):
        o = int(rng.uniform(0, 0.25) * SR); m = int(0.03 * SR)
        s[o:o + m] += rng.standard_normal(m) * env_exp(m, 0.006) * 1.5
    return 0.18 * s / np.abs(s).max()

def shimmer(dur=1.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * tt + p) for f, p in [(1760, 0), (2217, 1), (2637, 2), (3520, .5)])
    e = np.minimum(1, tt / 0.15) * env_exp(n, dur / 3)
    return 0.05 * s * e

sfx = np.zeros(N)
def place(sig, at, gain=1.0):
    i = int(at * SR); sfx[i:i + len(sig)] += gain * sig[:max(0, N - i)]

place(tick(), 0.0, 1.0); place(boom(), 0.0, 0.9)
place(tick(), starts["s4"] + 1.25, 0.6)
place(tick(), starts["s5"], 0.8); place(boom(0.9, 70, 40, 0.5), starts["s5"])
place(whoosh(), starts["s5"] + 1.6, 0.8)
place(tick(), starts["s6"] + 0.4, 0.3); place(tick(), starts["s6"] + 0.85, 0.3)
place(crack(), starts["s6"] + 1.42, 1.0); place(whoosh(0.4), starts["s6"] + 1.4, 0.6)
place(whoosh(0.9), starts["s7"] - 0.2, 0.5)
place(boom(1.2, 60, 30, 0.6), starts["s9"])
place(heartbeat(), starts["s9"] + 0.25, 1.0); place(heartbeat(), starts["s9"] + 1.05, 0.7)
place(tick(), starts["s12"], 0.6); place(shimmer(), starts["s12"], 1.0)
place(boom(1.0, 60, 35, 0.5), starts["s13"])
place(boom(1.8, 70, 28, 0.85), starts["freeze"])
place(boom(2.0, 55, 28, 0.5), starts["cta"] + 0.3)
place(shimmer(2.0), starts["cta"] + 3.1, 0.8)
place(tick(), starts["cta"] + 8.45, 1.0)

# Pad: soft hummed minor chords (Am - F - C - Em)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
CH = [[45, 57, 60, 64], [41, 53, 57, 60], [48, 55, 60, 64], [40, 52, 55, 59]]
CL = 4.4
tt = np.arange(N) / SR
pad = np.zeros(N)
for ci in range(int(TOTAL / CL) + 2):
    a0 = ci * CL; notes = CH[ci % 4]
    i0 = int(max(0, a0 - 0.8) * SR); i1 = min(N, int((a0 + CL + 1.6) * SR))
    if i0 >= N: break
    seg_t = tt[i0:i1] - a0
    e = np.clip((seg_t + 0.8) / 1.4, 0, 1) * np.clip((CL + 1.6 - seg_t) / 1.8, 0, 1)
    e = np.sin(e * np.pi / 2) ** 2
    for j, m in enumerate(notes):
        f = hz(m + 12)
        vib = 1 + 0.004 * np.sin(2 * np.pi * (4.6 + 0.3 * j) * seg_t + j) * np.clip(seg_t / 1.5, 0, 1)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph) + 0.05 * np.sin(4 * ph)
        pad[i0:i1] += (0.25 if j else 0.32) * tone * e
# reverb via FFT convolution with decaying noise IR
L = int(2.2 * SR); ir = rng.standard_normal(L) * env_exp(L, 0.55); ir[0] = 3
nfft = 1 << int(np.ceil(np.log2(N + L)))
wet = np.fft.irfft(np.fft.rfft(pad, nfft) * np.fft.rfft(ir, nfft), nfft)[:N]
pad = 0.55 * pad / np.abs(pad).max() + 0.45 * wet / np.abs(wet).max()
pad = pad / np.abs(pad).max()

# gain automation (dB) for the pad
pts = [(0, -60), (0.25, -40), (3.0, -27), (starts["s9"] - 0.15, -27), (starts["s9"], -70),
       (segend("s9") - 0.1, -70), (segend("s9") + 0.6, -27), (starts["s14"], -27), (starts["s14"] + 1.0, -19),
       (segend("s14"), -19), (segend("s14") + 0.6, -27), (starts["freeze"] - 0.05, -27), (starts["freeze"], -80),
       (starts["freeze"] + 0.45, -80), (starts["cta"] + 0.5, -15), (TOTAL - 1.5, -15), (TOTAL, -60), (TOTAL + 1, -80)]
gdb = np.interp(tt, [p[0] for p in pts], [p[1] for p in pts])
pad *= 10 ** (gdb / 20)

def wav(path, x):
    x = np.clip(x, -1, 1); st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
wav(os.path.join(OUT, "sfx.wav"), sfx * 0.8)
wav(os.path.join(OUT, "pad.wav"), pad)

# ---------- final renders ----------
base = os.path.join(OUT, "base.mkv")
ass = os.path.join(OUT, "caps.ass")
for tag, use_pad in [("with_nasheed_pad", True), ("clean_no_music", False)]:
    inputs = ["-i", base, "-i", os.path.join(OUT, "sfx.wav")]
    if use_pad: inputs += ["-i", os.path.join(OUT, "pad.wav")]
    n = 3 if use_pad else 2
    af = (f"[0:a]volume=1.0[v0];" + ("[1:a][2:a]amix=inputs=2:normalize=0[m];" if use_pad else "[1:a]anull[m];") +
          f"[v0][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample={SR}[a]")
    out = os.path.join(W, f"doa-anak-sampai-saat-itu-juga_{tag}.mp4")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex",
         f"[0:v]subtitles='{ass}'[v];" + af, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.2f}", out])
    print("wrote", out)
