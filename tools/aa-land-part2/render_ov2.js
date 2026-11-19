// node render_ov.js preview t1,t2 outdir   |   node render_ov.js chunk f0 f1 out.mov
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [mode, a, b, c] = process.argv.slice(2);
  const tl = JSON.parse(fs.readFileSync(path.join(__dirname, 'out/timeline.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; page.on('pageerror', e => errs.push(String(e))); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto('file://' + path.join(__dirname, 'overlay2.html'));
  await page.waitForFunction(() => window.render && window.ready);
  const imgs = { house: 'house.png', logo: 'logo_full.png' };
  for (const [id, f] of Object.entries(imgs)) {
    const d = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, 'assets', f)).toString('base64');
    await page.evaluate(([id, d]) => { document.getElementById(id).src = d; }, [id, d]);
  }
  await page.evaluate(() => window.ready());
  await page.evaluate(j => window.setTimeline(j), tl);
  const grab = t => page.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t);
  if (mode === 'preview') {
    fs.mkdirSync(b, { recursive: true });
    for (const t of a.split(',').map(Number)) fs.writeFileSync(path.join(b, `o_${t.toFixed(2).padStart(6, '0')}.png`), Buffer.from(await grab(t), 'base64'));
  } else {
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', '-c:v', 'png', '-pix_fmt', 'rgba', c], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = +a; f < +b; f++) { const buf = Buffer.from(await grab((f + 0.5) / 30), 'base64'); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  if (errs.length) console.log('PAGE ERRORS:\n' + errs.slice(0, 8).join('\n'));
  await browser.close();
})();
