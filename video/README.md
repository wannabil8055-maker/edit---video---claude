# "Satu Masjid Gelak": Video Animasi 2D (9:16, 55s)

Video animasi ini dihasilkan sepenuhnya oleh kod, ikut `../BLUEPRINT.md`.

| Fail | Kegunaan |
|---|---|
| `output/satu-masjid-gelak.mp4` | Video akhir 1080×1920, 30fps, dengan muzik + SFX (belum ada suara Ustaz) |
| `output/music_sfx.wav` | Trek muzik + SFX sahaja (untuk mixing di CapCut/Premiere) |
| `anim.html` | Enjin animasi (Canvas 2D). Semua babak, watak dan teks ada di sini |
| `render.js` | Render frame demi frame ke MP4 (Playwright + ffmpeg) |
| `audio.py` | Sintesis muzik latar, SFX dan gelak jemaah (numpy) |

## Slot suara Ustaz (VO)

Muzik sengaja direndahkan (ducking) dalam slot ini supaya klip audio kuliah boleh terus diletakkan di atasnya.

| Slot | Masa | Babak | Audio yang perlu diletak |
|---|---|---|---|
| VO-1 | 4.6–9.0s | Kertas soalan terbang ke Ustaz | Soalan jemaah (dibaca oleh Ustaz) |
| VO-2 | 9.0–12.0s | Close-up Ustaz bercakap | Jawapan lucu / punchline |
| — | 12.0–15.0s | Satu masjid gelak | (gelak sintetik sudah ada) |
| VO-3 | 17.6–25s | Kad Ilmu #1 | Penerangan Ustaz (pilihan) |
| VO-4 | 25–33s | Kad Ilmu #2 (dalil Arab) | Penerangan Ustaz (pilihan) |
| VO-5 | 33–41s | Montaj 3 panel | Nasihat praktikal (pilihan) |
| VO-6 | 42–49s | Senja + petikan | Kata penutup yang menyentuh (pilihan) |

## Kandungan ilmu dalam video

Teks pada kad ilmu adalah hadis sahih tentang senyum dan ketawa, **bukan petikan kata-kata Ustaz**:
1. Aisyah r.a.: Rasulullah SAW tidak ketawa terbahak-bahak, baginda hanya tersenyum (HR Bukhari).
2. "Senyumanmu di hadapan saudaramu adalah sedekah" (HR Tirmizi).
3. "Jangan banyak ketawa, kerana banyak ketawa mematikan hati" (HR Ibnu Majah).

Jika isi klip rujukan berbeza, tukar teks dalam fungsi `card1`, `card2`, `montage` dan `sceneDusk` di `anim.html`, kemudian render semula.

## Render semula

```bash
npm install                                  # fon (Baloo 2, Poppins, Amiri)
node render.js stills /tmp/st 1.9 10 20      # pratonton gambar pada saat tertentu
node render.js video out/silent.mp4 30       # video senyap
python3 audio.py out/music_sfx.wav           # trek audio
ffmpeg -i out/silent.mp4 -i out/music_sfx.wav -c:v copy -c:a aac -b:a 192k -shortest output/satu-masjid-gelak.mp4
```
