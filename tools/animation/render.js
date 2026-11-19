// usage: node render.js preview t1,t2,...  outdir
//        node render.js chunk startFrame endFrame out.mp4
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const FPS = 30;

(async () => {
  const [mode, a, b, c] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto('file://' + path.join(__dirname, 'anim.html'));
  await page.waitForFunction(() => window.render);
  const grab = async (t, q) => page.evaluate(([t, q]) => { render(t); return document.getElementById('c').toDataURL(q ? 'image/jpeg' : 'image/png', q || undefined).split(',')[1]; }, [t, q]);
  if (mode === 'preview') {
    fs.mkdirSync(b, { recursive: true });
    for (const t of a.split(',').map(Number)) fs.writeFileSync(path.join(b, `p_${t.toFixed(2)}.png`), Buffer.from(await grab(t, 0), 'base64'));
  } else {
    const s = +a, e = +b;
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), c], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = s; f < e; f++) {
      const buf = Buffer.from(await grab((f + 0.5) / FPS, 0.95), 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - s) % 150 === 0) console.log(`chunk ${s}: frame ${f}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  if (errs.length) console.log('PAGE ERRORS:\n' + errs.slice(0, 10).join('\n'));
  await browser.close();
})();
