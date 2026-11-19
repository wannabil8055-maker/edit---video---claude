# Animation Blueprint: "8:40" (Your Dua Reaches Them That Same Second)

**Format:** 9:16, 1080×1920, 30fps · **Length:** ~53s · **Audio:** Ustadz Wadi Anuar's voice from the lecture (credited). There is **no live-action footage of him**.
The voice cuts and timings are the same as the live-action edit (`tools/build_doa_anak_video.py`), so you can reuse the audio track as it is.

---

## 1. Visual style and look

**Style: "Ethereal Paper-Light".** Layered 2D paper-cut silhouettes with soft depth and slow parallax, lit by glowing gold light particles. Think of a moonlit Malay kampung and city at night drawn as cut paper, with prayer shown as **threads of light**.

- **People:** silhouettes only, with **no faces**. Parents are never shown. They appear only as memories (hands, a chair, a photo).
- **Barzakh:** shown abstractly, as a **misty veil on the horizon**. Never draw souls, angels, or the inside of the grave.
- **Central visual metaphor:** a dua leaves the child's raised hands as a **gold thread of light**. It crosses the night sky, passes through the veil, and lands *at the same instant* on the parents' grave, where a **kemboja (frangipani) blossom glows**.
- **Repeated motif:** a clock reading **8:40**. It opens the video, comes back in the middle, and closes it, so the end loops into the start.
- **Camera:** slow drifting moves with 3–5 parallax layers. Every 2–3s there is a change: a push-in, a reveal, or a text hit.
- **Texture:** fine paper grain, soft bloom on all light, slow floating dust particles.

| Role | Colour | Hex |
|---|---|---|
| Night sky (base) | Midnight navy | `#0B1A2F` |
| Depth layers | Deep teal | `#12343B` |
| Dusk gradient | Indigo dusk | `#2A2550` |
| **Dua light / accents** | Soft gold | `#F2C14E` |
| Text / moonlight | Warm ivory | `#F7F1E3` |
| Emotion (memories) | Faded rose | `#D9A5A0` |
| "Tak ramai" desaturate | Ash grey | `#8A8F98` |

**Type:** Inter Display Black or Montserrat ExtraBold for punch text, Inter Medium for English subtitles, and **Amiri** for Arabic calligraphy. Captions go word by word in ivory, with the word being spoken turning gold.

**Master AI prompt for style frames (Midjourney, Firefly or similar):**
`layered paper-cut illustration, Malay kampung at night, silhouette without face, glowing golden light threads rising to the sky, midnight navy and deep teal palette, soft gold bloom, misty horizon, kemboja tree, cinematic, minimalist, peaceful, 9:16`

---

## 2. The hook (0:00–0:03)

| Time | Visual | Text | SFX |
|---|---|---|---|
| 0.00–0.40 | Pure black. A thin gold clock hand **ticks onto 8:40**. | Huge ivory **8:40** | Sharp **clock tick** |
| 0.40–1.20 | The clock face **shatters into gold particles** that streak upward. | — | Reverse whoosh into a **deep bass impact** |
| 1.20–3.00 | The particles reform into the words, which **slam in one at a time** with a small camera shake. Behind them, a faint moonlit graveyard fades up. | **DOA KAU SAMPAI KE KUBUR MAK AYAH…** then **SAAT ITU JUGA.** in gold, scaling 120%→100% | Soft chime on "SAAT ITU JUGA" |

**Voice:** *"8:40 juga mak dengan ayah terima pahala itu."*
**Why it works:** the scroll-stopping elements land in the first 0.4s (a ticking clock, a shatter, and the word "kubur"). The 8:40 line gets its full context at 0:08.

---

## 3. Scene-by-scene animation blueprint

| Time | Voice | Visual animation | On-screen text and motion | SFX / transition |
|---|---|---|---|---|
| **0:03–0:08** | "Amalan-amalan ibadah dan kebaikan daripada anak…" | A teen's silhouette in a dim bedroom at night. A phone screen **switches off**, then they kneel on a sejadah and raise their hands. Through the window, a moonlit city. Slow push-in. | Word-by-word captions fade up 8px. English sits small underneath. | Ambient pad fades in; soft phone-lock "click" |
| **0:08–0:14** | "Kalau anak itu sebut pukul 8:40… 8:40 juga mak dengan ayah terima pahala itu" | **Split screen, top and bottom.** Top: the praying teen with a wall clock at 8:40. Bottom: a quiet graveyard under the *same moon*, two nisan, with a ghostly clock also at 8:40. A **gold thread leaves the hands, cuts through the dividing line, and touches the graves**. | **8:40** appears in both halves and **pulses in sync**. | Two chimes, perfectly in sync |
| **0:14–0:17** | "Takdak pending-pending, takdak." | A frosted-glass UI card **"PENDING…"** with a loading bar at 70%. The gold light **pierces it** and the card shatters into particles. | **TAKDA "PENDING".** snaps in with an overshoot bounce | Glass crack, then shimmer |
| **0:17–0:23** | "Transaksi ibadah yang dilakukan oleh anak dan cucu…" | **Crane up** above the neighbourhood. Windows light up one by one, and from each a thin gold thread rises. The threads braid into a **river of light** flowing toward the misty veil on the horizon. | Floating labels drift along the threads: *anak*, *cucu*, *cicit*. | Rising airy whoosh; humming swells |
| **0:23–0:25** | **"terus masuk saat itu juga"** | The river of light **pierces the veil**. Everything holds still for 6 frames, then there is a **warm bloom flash**. | **SAAT ITU JUGA.** huge in gold, centred, light glowing off the letters | **Music cuts to silence**, then a heartbeat and a soft bass impact. This is the emotional peak |
| **0:25–0:27** | "Seorang anak soleh kalau dia kata…" | Close-up of silhouetted hands and tasbih beads sliding, warm lantern glow. | Captions | Music returns softly |
| **0:27–0:30** | (the dua is recited) | **Arabic calligraphy writes itself** in gold, stroke by stroke. When it finishes, the letters lift off as particles and rise. | **رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ** · *Rabbighfir li wa li walidayya* · "My Lord, forgive me and my parents." (**match the dua actually recited**) | Light reverb on the voice, gentle chime |
| **0:30–0:34** | "Pukul 9 pagi… sampai dekat ayah dengan mak dia dalam kubur." | **Time-lapse from night to dawn** over the graveyard while the clock spins to 9:00. A single light orb descends gently onto the nisan, and a **kemboja blossom falls and glows**. | **9:00 PAGI → TERUS SAMPAI.** slides in from the left | Faint morning birds, shimmer |
| **0:34–0:35** | "Tuan-tuan, bukan susah pun." | A flat ivory background, with one gold thread underlining the text. | **BUKAN SUSAH PUN.** slams in | Soft bass hit |
| **0:35–0:39** | (pause or recitation) | **Memory montage** in faded rose, about 0.8s per shot: a mother's hands stirring a pot, a father carrying a child on his shoulders, an **empty chair** at the dinner table, an old photo that fades away. | **Bila kali terakhir kau doakan mereka?** fades in slowly | Humming rises, no SFX |
| **0:39–0:43** | "Tapi berapa ramai yang boleh sebut 5 kali, 10 kali… tak ramai." | Back to the neighbourhood view, but now **most windows are dark**. Only one or two threads rise. A counter ticks "1… 2…" and stops. Colour **drains to ash grey**. | **…TAK RAMAI.** freezes centre-screen | Hard mute for 0.4s |

---

## 4. Pacing and vibe

- **Background music:** a **vocal-only humming nasheed** with a light ambient bed (soft airy pads, no drums). It suits a Muslim audience and fits the dreamy animation. If you prefer instruments, use a **soft felt piano with a slow ambient pulse** (about 60–70 BPM, minor key).
  - Search terms: "nasheed humming emotional", "ambient vocal pad sad".
  - Mix: music at **-20 to -24 dB** under the voice, with auto-ducking. Voice at about -6 dB. Master to **-14 LUFS**.
- **Shape:** quiet and intimate → curiosity (8:40) → reassurance ("no pending") → **wonder** (river of light) → **silence peak** ("saat itu juga") → nostalgia (memories) → sadness ("tak ramai") → hope (the CTA).
- **Motion rules:** all easing is *ease-in-out sine*, so nothing moves too sharply except the four "slam" moments (hook, TAKDA PENDING, SAAT ITU JUGA, TAK RAMAI). Text never stays on screen longer than the voice line it belongs to.
- **Light:** the gold light is always the hero. Every scene must have one gold element moving **upward**.

---

## 5. Call-to-action animation (0:43–0:53)

| Time | Visual | Text | SFX |
|---|---|---|---|
| 0:43–0:46 | In the grey, dark neighbourhood, **one window lights up again**: yours. | **Mak ayah kau tengah tunggu.** / *Your parents are waiting.* | A single soft piano note or hum |
| 0:46–0:49 | A gold thread rises from that window, and the **Arabic dua writes itself** along the thread. Colour slowly returns. | **Doakan mereka SEKARANG.** with "SEKARANG" pulsing gold · رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ | Rising shimmer |
| 0:49–0:52 | The thread reaches the veil, and a kemboja blossom glows on the grave in the distance. | **Tulis "Ameen" 🤲 & share pada yang dah kehilangan mak/ayah.** Small text under it: *"…atau anak soleh yang mendoakannya." HR Muslim 1631* | Music swells, then softens |
| 0:52–0:53 | Particles form a clock, and it **ticks to 8:40**, matching the first frame. | **8:40** | Clock tick, so the video loops to the start |

**Pinned comment:** *"Berhenti sekejap. Hadiahkan Al-Fatihah untuk mak ayah kita semua. 🤲"* (Stop for a moment and gift Al-Fatihah to all our parents.)
**Credit (on screen and in the caption):** *Audio: Ustadz Wadi Anuar.* Also link the original source.

---

## Production notes
- **Tools:**
  - After Effects (with Saber or Trapcode Particular for the threads) or Blender (Grease Pencil for the paper-cut look).
  - Low-budget route: AI style frames + CapCut keyframe parallax + a light-leak/particle overlay pack.
- **Assets to build:** the teen silhouette (kneeling and hands raised), a graveyard with nisan and a kemboja tree, a city/kampung skyline (3 layers), the clock, the PENDING card, the light-thread system, 4 memory vignettes.
- **Sensitivities:** no faces, and no depiction of the deceased, angels, or the inside of the grave. Show the Arabic text correctly (proofread it with an ustaz).
