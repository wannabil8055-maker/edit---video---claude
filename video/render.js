// Usage:
//   node render.js stills out_dir 0.5 1.7 ...   -> PNG snapshots at given seconds
//   node render.js video out.mp4 [fps]            -> silent video via ffmpeg
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
  await page.goto('file://' + path.join(__dirname, 'anim.html'));
  await page.evaluate(() => window.ready);

  const grab = (t, fmt, q) => page.evaluate(([t, fmt, q]) => { window.render(t); return document.getElementById('cv').toDataURL(fmt, q).split(',')[1]; }, [t, fmt, q]);

  if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    for (const s of rest) {
      const b = await grab(parseFloat(s), 'image/jpeg', .85);
      fs.writeFileSync(path.join(out, `t${String(s).padStart(5, '0')}.jpg`), Buffer.from(b, 'base64'));
    }
  } else if (mode === 'video') {
    const fps = parseInt(rest[0] || '30', 10), dur = await page.evaluate(() => window.DUR), n = Math.round(dur * fps);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      const b = await grab(i / fps, 'image/jpeg', .95);
      if (!ff.stdin.write(Buffer.from(b, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
