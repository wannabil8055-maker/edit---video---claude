# AI Image Prompts — "Who Will Answer For You?"

Works with **Midjourney v6/v7**, **Leonardo**, **Ideogram**, **Flux**, and **DALL·E**. Every prompt is 9:16 vertical.

---

## How to keep every scene consistent

1. **Generate the character sheet first** (Prompt 0). Pick the best result and use it as the reference for every scene:
   - Midjourney: `--cref <image URL> --cw 80`
   - Leonardo: Character Reference
   - Flux: IP-Adapter
2. **Always paste the STYLE BLOCK** at the end of each prompt, along with that act's palette line.
3. Use the same seed for scenes in the same act (Midjourney: `--seed 7777`).
4. **Don't let AI write text on the image.** Add all text and captions in CapCut or After Effects. AI text comes out messy.
5. Generate a clean background plate plus the character separately when you can, so you can animate with parallax.

### STYLE BLOCK (paste into every prompt)
```
flat 2D cut-paper illustration, layered paper depth with soft drop shadows, subtle paper grain texture, thick rounded outlines, simple faceless characters with no eyes no mouth, minimalist shapes, cinematic lighting, motion-graphics style, vertical composition, centered subject, clean negative space at top and bottom for captions
```

### PALETTE LINES (pick one per act)
- **ACT 1 – Dunya:** `neon magenta #FF2E88, electric cyan #22D3EE, glitter gold #F5C542, deep navy background #0B1026, flashy and glossy`
- **ACT 2/3 – Death & Grave:** `desaturated ash grey #6B7280, bone white #E8E4D9, bruise blue #1E3A8A, ink black #05060A, single deep red accent #B91C1C, cold and empty`
- **ACT 4 – Hope:** `dawn peach #F7B79B, soft teal #5EC4B6, warm gold #E9B949, ivory #FFF8EC, warm sunrise glow, peaceful`

### NEGATIVE PROMPT (Leonardo / SD / Flux)
```
text, letters, watermark, logo, brand logo, realistic face, detailed face, eyes, lips, nudity, revealing clothing, gore, blood, injury, 3D render, photorealistic, extra limbs, deformed hands, cluttered background
```

### Midjourney suffix
```
--ar 9:16 --style raw --stylize 250 --no text, letters, logo, face details, gore
```

---

## PROMPT 0 — Character reference sheet (do this first)

```
Character turnaround sheet of a faceless young Muslim man, simple rounded head with no facial features, short neat dark hair silhouette, slim build, wearing a modern dark hoodie and jeans, front view, side view, back view, three-quarter view, plus a version in a white kafan shroud, plus a translucent glowing white ghost version of the same character, a thin glowing golden thread coming out of his chest, plain light grey background, [STYLE BLOCK]
```
Also make these supporting characters the same way:
- **Son:** `faceless little boy, about 7 years old, holding a small Qur'an iqra book, round simple shapes, [STYLE BLOCK]`
- **Wife:** `elegant soft silhouette of a woman made only of a warm glowing outline, no body details, no face, modest and respectful, [STYLE BLOCK]`

---

## HOOK (0:00 – 0:03)

**H1 — Fake social feed**
```
Close-up of a smartphone screen filling the whole frame, showing a colourful social media video feed with floating heart icons and like bubbles, a cartoon thumb swiping up, motion blur on the feed, glowing screen light, [STYLE BLOCK], [ACT 1 palette]
```
**H2 — Flatline**
```
Pure black smartphone screen with a single thin white heart-rate monitor line running across the middle, flatlining, faint glow, empty and ominous, minimal, [STYLE BLOCK]
```
**H3 — Cracked screen revealing grave**
```
Black smartphone screen shattered with glass cracks spreading from the centre, through the cracks a dark grave pit and a faint eerie blue light glowing from below, dramatic, [STYLE BLOCK], [ACT 2/3 palette]
```
**H4 — Pull back to his hand**
```
Over-the-shoulder shot of a faceless young man in a dark hoodie sitting on a bed at night scrolling his phone, phone light illuminating his blank face, neon city light through the window, [STYLE BLOCK], [ACT 1 palette]
```

---

## ACT 1 — DUNYA

**S1 — Scroll addiction & dusty prayer mat**
```
Faceless young man lying in a messy bedroom at night staring at his glowing phone, earbuds in, small neon music-note shapes circling his head like a cage, in the corner a rolled-up prayer mat covered in dust under a soft spotlight, wall clock, [STYLE BLOCK], [ACT 1 palette]
```
**S2 — Heart distracted, son ignored**
```
Faceless young man on a sofa absorbed in his phone, a rain of pink heart emojis and chat bubbles floating out of the screen, behind him a small faceless boy holding an iqra Qur'an book, waiting with drooping shoulders, the man waving him away without looking, a thin golden thread from the man's chest starting to fray with a small spark, [STYLE BLOCK], [ACT 1 palette]
```
**S3 — Climbing for rank**
```
Faceless man in a suit running up a tall staircase made of trophies and office name plates, stepping on other faceless office workers, dynamic upward perspective, city skyscrapers behind, golden light at the top, [STYLE BLOCK], [ACT 1 palette]
```
**S4a — Hypercar drop**
```
A sleek generic hypercar with no logos crashing down from the sky onto the street, a big dust cloud and ground cracks on impact, faceless man posing proudly next to it, comic impact lines, [STYLE BLOCK], [ACT 1 palette]
```
**S4b — Luxury car drop**
```
A long elegant generic luxury limousine with no logos landing heavily beside a hypercar, dust burst, shiny chrome, faceless man in sunglasses-shaped silhouette smiling arrogantly with arms crossed, [STYLE BLOCK], [ACT 1 palette]
```
**S4c — Villa drop**
```
A grand modern hilltop villa with infinity pool and palm trees slamming down from the sky behind a faceless man, huge dust shockwave, ground cracking, gold glitter in the air, [STYLE BLOCK], [ACT 1 palette]
```
**S4d — Travel montage**
```
Spinning suitcase covered in travel stickers, surrounded by floating paper-cut landmarks: Eiffel tower silhouette, Dubai skyline, tropical island, Tokyo tower, airplane flying past, passport stamps floating, [STYLE BLOCK], [ACT 1 palette]
```
**S5 — Everywhere except Makkah**
```
A paper-cut globe with glowing location pins lighting up across every country, except one dark empty spot in Arabia where a small Kaaba silhouette sits unlit, a dusty unopened envelope on a luxury table in the foreground, moody quiet lighting, [STYLE BLOCK], colours fading from neon to muted
```
**S5b — Wife waiting alone**
```
Long luxury dinner table at night, a soft glowing silhouette of a woman sitting alone at one end, at the other end a faceless man looking at his phone, empty plates, cold distance between them, [STYLE BLOCK], muted navy and gold
```

---

## ACT 2 — DEATH

**S6 — Texting while driving**
```
Point-of-view from inside a sports car at night in heavy rain, a hand holding a glowing phone near the steering wheel, through the windshield the blinding white headlights of a big truck approaching, rain streaks, tension, [STYLE BLOCK], [ACT 2/3 palette] with white glare
```
**S6b — Slow-motion glass & phone**
```
Shards of broken glass frozen in mid-air in slow motion against black, a smartphone spinning in the centre with its screen cracking, no people visible, no blood, dramatic white rim light, [STYLE BLOCK], [ACT 2/3 palette]
```
**S7 — Soul sees its body**
```
A translucent glowing white ghost of a faceless man kneeling on a wet road at night, looking down at a still body covered by a white sheet beside an ambulance, red ambulance light as the only colour, grey desaturated world, the ghost's hand passing through the sheet, despair, [STYLE BLOCK], [ACT 2/3 palette]
```
**S8a — Ghusl (washing)**
```
Top-down view of a body fully covered with a cloth on a washing table, two kind hands with sleeves pouring water from a jug, glowing water droplets, a translucent ghost of the man watching from the corner trembling, soft respectful lighting, [STYLE BLOCK], [ACT 2/3 palette]
```
**S8b — Kafan**
```
A body wrapped neatly in layered white kafan cloth, folds drawn like origami paper, the only bright white in a grey room, calm and solemn, [STYLE BLOCK], [ACT 2/3 palette]
```
**S8c — Janazah procession**
```
Silhouettes of men carrying a covered funeral bier through a misty Muslim graveyard with simple headstones, in the far background a tiny villa and cars fading into fog, overcast sky, [STYLE BLOCK], [ACT 2/3 palette]
```
**S8d — View from inside the grave**
```
View from the bottom of a grave looking up at a narrow rectangle of grey sky, soil falling in from a shovel above, the opening getting dark, roots in the soil walls, claustrophobic, [STYLE BLOCK], [ACT 2/3 palette]
```

---

## ACT 3 — THE GRAVE

**S9 — Munkar & Nakir arrive**
```
Inside a dark narrow grave, a small figure wrapped in a white kafan curled at the bottom of the frame, behind him two gigantic towering abstract forms made of swirling deep blue and black smoke and light rising out of the cracked soil walls, no faces, only two pairs of piercing lightning-white glowing eyes, blue electric veins pulsing through the smoke, overwhelming scale, awe and fear, [STYLE BLOCK], [ACT 2/3 palette]
```
**S10 — The questioning shockwave**
```
A blue light shockwave bursting through a dark grave, pushing a small kafan-wrapped figure back against the soil wall, broken glitching floating screens around his head showing faded images of a car, a villa, a phone, all dissolving into static, [STYLE BLOCK], [ACT 2/3 palette]
```
**S11a — The iron hammer (swing only)**
```
A giant abstract arm of blue-black smoke raising a massive dark iron hammer with blue fire edges above a dark grave, dramatic low angle, the moment before the strike, no impact shown, [STYLE BLOCK], [ACT 2/3 palette]
```
**S11b — Peaceful world above**
```
A calm sunny Muslim graveyard, green grass, birds on a branch, faceless people walking past casually looking at their phones and laughing, peaceful and unaware, [STYLE BLOCK], soft natural colours
```
**S11c — Thread snaps**
```
Close-up of a thin frayed golden thread snapping in the darkness, the broken end floating away and fading like a dying spark, deep black background, [STYLE BLOCK], [ACT 2/3 palette] with gold accent
```
**S12 — Split screen: no du'a, sins falling**
```
Vertical split composition: top half shows a faceless grown young man scrolling his phone in a bright modern room, ignoring everything; bottom half shows a dark grave with a kafan-wrapped figure looking up waiting, small black ink drops falling onto him from above, cold blue light, [STYLE BLOCK], top bright, bottom [ACT 2/3 palette]
```
**S13 — Pull back over graves**
```
High aerial view rising above hundreds of dark grave rectangles in grey mist, one grave faintly highlighted in the centre, an hourglass silhouette with frozen sand floating in the sky, lonely and vast, [STYLE BLOCK], [ACT 2/3 palette]
```

---

## ACT 4 — HOPE

**S14a — Fajr, phone face down**
```
Soft dawn light through a window, a faceless man placing his phone face down on a table and unrolling a prayer mat, dust lifting off it as golden sparkles, warm peaceful room, [STYLE BLOCK], [ACT 4 palette]
```
**S14b — Teaching his son**
```
A faceless father and his small son sitting together on the floor reading an iqra Qur'an book, warm lamp light, a gentle golden thread rising from both of them into the air, [STYLE BLOCK], [ACT 4 palette]
```
**S14c — Gift for his wife**
```
A faceless man gently handing a folded beautiful scarf as a gift to a warm glowing silhouette of a woman, respectful and tender, soft sunrise light, [STYLE BLOCK], [ACT 4 palette]
```
**S14d — Sadaqah**
```
A faceless man handing a food package to an elderly poor man outside a small masjid, coins dropping into a wooden donation box, golden threads of light rising from the act toward the sky, [STYLE BLOCK], [ACT 4 palette]
```
**S14e — Ticket to Makkah**
```
A paper plane ticket glowing in a man's hand, a soft silhouette of the Kaaba on the horizon at dawn, golden threads forming a glowing web of light across the sky, hopeful, [STYLE BLOCK], [ACT 4 palette]
```

---

## CTA

**CTA1 — Phone made of light, 3% battery**
```
Golden threads of light weaving together into the outline of a smartphone floating in a soft dark-to-dawn gradient, a small battery icon glowing red at the top, light particles drifting, centred with empty space for text, [STYLE BLOCK], [ACT 4 palette] with a red accent
```
**CTA2 — Share as a paper plane of light**
```
A glowing paper plane made of golden light flying upward and splitting into hundreds of tiny light particles spreading across a dawn sky, magical and hopeful, [STYLE BLOCK], [ACT 4 palette]
```

---

## Turning images into motion (optional)

Feed each still into **Kling, Runway Gen-4, Pika or Luma** with short motion prompts:

| Scene | Motion prompt |
|---|---|
| S4a–c | `object falls fast from top and slams down, dust burst, camera shake` |
| S7 | `ghost slowly rises from body, flickering, slow camera push-in` |
| S8d | `soil falls from above, the light opening slowly shrinks to black` |
| S9 | `giant smoke forms rise slowly, eyes open with a lightning flash, camera shakes` |
| S11c | `golden thread snaps in slow motion, the end drifts away and fades` |
| S14e | `golden light threads spread across the sky, gentle sunrise` |

Keep clips to 2–5 s each and cut them in CapCut/Premiere to the timing in `subtitles.srt`.
