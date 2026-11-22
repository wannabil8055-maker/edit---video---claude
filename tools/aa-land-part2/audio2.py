"""Part 2 music + SFX (same instruments as Part 1) and mix."""
import os, json, wave, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
lib = open(os.path.join(HERE, "..", "land", "audio.py")).read()
SR = 48000
exec(lib[lib.index("rng = np.random.default_rng(3)"):lib.index("# ---------- music ----------")])      # instruments + helpers from Part 1
TL = json.load(open(os.path.join(OUT, "timeline.json"))); SEG = {s["key"]: s for s in TL["segs"]}; PCS = TL["pieces"]
TOTAL = TL["total"]; N = int(TOTAL * SR) + SR
BPM = 140; BEAT = 60 / BPM; BAR = 4 * BEAT; G0 = TL["grid0"]

# ---------- music ----------
mus = np.zeros(N)
notes = [41.2, 41.2, 49.0, 36.7]; arp = [329.6, 392.0, 493.9, 587.3, 493.9, 392.0, 329.6, 293.7]
t = G0; bar = 0
while t < TOTAL - 0.1:
    root = notes[bar % 4]; hookbar = t < SEG["hook"]["t1"]
    for b in range(16):
        tt = t + b * BEAT / 4
        if tt >= TOTAL: continue
        if b in (0, 6, 10) or (bar % 2 == 1 and b == 14) or (hookbar and b in (3, 8, 12)): place(mus, kick(), tt)
        if b in (4, 12): place(mus, clap(), tt)
        if b % 2 == 0 or (bar % 4 == 3 and b >= 12) or hookbar: place(mus, hat(0.2 if b % 4 == 0 else 0.13), tt)
        if b in (0, 6, 10): place(mus, bass808(root, BEAT * (1.5 if b == 0 else 1.0)), tt)
        if b % 2 == 0: place(mus, pluck(arp[(b // 2 + bar) % 8]), tt, 0.8)
        if hookbar and b % 4 == 2: place(mus, anvil(0.18), tt)
    if bar % 2 == 1: place(mus, anvil(0.25), t + 3 * BEAT)
    t += BAR; bar += 1
gain = np.full(N, 0.32)
def gseg(a, b, g): gain[int(a * SR):int(b * SR)] = g
gseg(0, SEG["hook"]["t1"], 0.6); gseg(SEG["logo"]["t0"], SEG["recap"]["t1"], 0.85)
gseg(SEG["tanah"]["t0"], SEG["siap"]["t1"], 0.9); gseg(SEG["end"]["t0"], TOTAL + 1, 0.8)
k = int(0.08 * SR); gain = np.convolve(gain, np.ones(k) / k, mode="same"); mus *= gain

# ---------- SFX ----------
sfx = np.zeros(N)
place(sfx, riser(G0, 0.5), 0.0); place(sfx, boom(0.9), 0.0)
for p in PCS:
    if p["impact"]:
        place(sfx, boom(0.75 if p["seg"] == "hook" else 0.45, 0.9), p["t0"]); place(sfx, whoosh(0.3, 0.35), p["t0"] - 0.18)
        if p["seg"] == "hook": place(sfx, anvil(0.35), p["t0"]); place(sfx, debris(0.3), p["t0"])
    if p.get("label"): place(sfx, pop(0.3), p["t0"] + 0.05)
place(sfx, boom(0.9), TL["hookVO"] + 0.5); place(sfx, debris(0.35), TL["hookVO"] + 0.5)
L0 = SEG["logo"]["t0"]
place(sfx, anvil(0.35), L0 + 0.05); place(sfx, anvil(0.3), L0 + 0.3); place(sfx, drill(0.4), L0 + 0.32)
place(sfx, whoosh(0.4, 0.4), L0 + 0.55); place(sfx, boom(1.0), L0 + 0.95); place(sfx, anvil(0.4), L0 + 0.97)
place(sfx, ding(2400, 0.2), L0 + 1.5); place(sfx, pop(0.35), L0 + 1.6)
R0 = SEG["recap"]["t0"]; place(sfx, whoosh(0.4, 0.4), R0 - 0.1)
for i in range(3): place(sfx, pop(0.3), R0 + 0.25 + i * 0.22)
place(sfx, chaching(0.25), R0 + 0.5)
for k2 in ("v1", "v2", "v3", "v4"): place(sfx, pop(0.28), SEG[k2]["t0"] + 0.1)
place(sfx, whoosh(0.4, 0.3), SEG["v2"]["t0"]); place(sfx, ding(2093, 0.25), SEG["v5"]["t0"]); place(sfx, boom(0.5, 0.8), SEG["v5"]["t0"])
place(sfx, riser(SEG["v6"]["t1"] - SEG["v6"]["t0"], 0.3), SEG["v6"]["t0"]); place(sfx, whoosh(0.45, 0.5), SEG["tanah"]["t0"] - 0.2); place(sfx, boom(0.9), SEG["tanah"]["t0"])
T0 = SEG["tanah"]["t0"]
for o in (0, 4 * BEAT, 7 * BEAT): place(sfx, pop(0.35), T0 + o); place(sfx, ding(1760, 0.2), T0 + o + 0.1)
for i in range(3): place(sfx, ding(2093 + i * 200, 0.2), T0 + 10 * BEAT + i * BEAT * 0.5)
S0 = SEG["split"]["t0"]; place(sfx, whoosh(0.4, 0.45), S0 - 0.15); place(sfx, boom(0.6), S0 + 0.3)
place(sfx, ding(2637, 0.25), SEG["siap"]["t0"] + 0.15)
E0 = SEG["end"]["t0"]
place(sfx, whoosh(0.4, 0.45), E0 - 0.15); place(sfx, boom(1.0, 2.0), E0 + 0.35); place(sfx, debris(0.35), E0 + 0.36)
place(sfx, ding(2637, 0.25), E0 + 0.9); place(sfx, pop(0.3), E0 + 1.1); place(sfx, pop(0.3), E0 + 1.25)

# ---------- voice / machine + hook VO ----------
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(OUT, "base.mkv"), "-vn", "-af",
                "highpass=f=90,afftdn=nf=-25:nr=16,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,"
                f"aresample={SR}", "-ac", "1", os.path.join(OUT, "voice_clean.wav")], check=True)
def readwav(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = readwav(os.path.join(OUT, "voice_clean.wav")); voice = np.zeros(N); voice[:min(len(v), N)] = v[:N]
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(OUT, "hookvo.wav"), "-af", "highpass=f=90,afftdn=nf=-25:nr=14,acompressor=threshold=-20dB:ratio=3:makeup=4", "-ar", str(SR), os.path.join(OUT, "hookvo_c.wav")], check=True)
place(voice, readwav(os.path.join(OUT, "hookvo_c.wav")) * 1.3, TL["hookVO"])
h = int(0.02 * SR); e = np.sqrt(np.convolve(voice ** 2, np.ones(h) / h, mode="same"))
act = np.clip((20 * np.log10(e + 1e-9) + 40) / 10, 0, 1); act = np.convolve(act, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
vo_mask = np.zeros(N)
for kk in ("v1", "v2", "v3", "v4", "v5", "v6"): vo_mask[int(SEG[kk]["t0"] * SR):int(SEG[kk]["t1"] * SR)] = 1
hv = TL["hookVO"]; vo_mask[int(hv * SR):int((hv + 1.3) * SR)] = 1
duck = 1 - 0.55 * np.clip(act * 1.5, 0, 1) * vo_mask
mix = voice + mus * duck * 0.55 + sfx * 0.6
i1 = int(TOTAL * SR); mix[i1:] = 0; fo = int(0.4 * SR); mix[i1 - fo:i1] *= np.linspace(1, 0, fo)
mix /= max(1.0, np.abs(mix).max() / 0.95)
with wave.open(os.path.join(OUT, "mix.wav"), "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
print("mix ok", TOTAL)
