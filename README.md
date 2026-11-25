# edit---video---claude

Toolkit edit video:

| Alat | Versi | Cara pakai |
|---|---|---|
| ffmpeg / ffprobe | 6.1.1 (bawaan sistem) | `ffmpeg ...` |
| Remotion | 4.0.547 | `npx remotion studio`, `npx remotion render <entry> <id> out.mp4` |
| HyperFrames | 0.9.92 | `npx hyperframes init <nama>`, `npx hyperframes render` |
| Whisper (faster-whisper) | 1.2.1 | `.venv/bin/python` → `from faster_whisper import WhisperModel` |

## Setup

```bash
npm install
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

`remotion.config.ts` mengarahkan Remotion ke Chromium bawaan container cloud.
Model Whisper diunduh dari Hugging Face saat pertama kali dipakai.
