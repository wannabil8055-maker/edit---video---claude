# Video source

Re-renders `output/who-will-answer-for-you.mp4` (1080×1920, 24 fps).

1. `pip install kokoro-onnx soundfile numpy`, then download `kokoro-v1.0.onnx` and `voices-v1.0.bin`
   from the kokoro-onnx GitHub releases into `$WORK/tts/`.
2. Copy `script.py`, `tts.py`, `audio.py` to `$WORK/build/`, and `anim.html`, `render.js` to `$WORK/render/`
   (run `npm i @fontsource/montserrat@5.1.0 @fontsource/amiri@5.1.0 playwright` there).
3. `python3 build/tts.py $WORK` → voiceover (Kokoro, blended am_michael + am_onyx male voice)
4. `python3 build/audio.py $WORK` → timeline.json + synthesized SFX/music + mix.wav
5. `node render/render.js $WORK full out.mp4` → renders the canvas animation frame by frame and muxes audio.

Edit narration in `script.py`; all visuals are in `anim.html` (one function per scene).
