// ---------- Part 2 scenes ----------
const PIECES = () => TL.pieces;
function lightLeak(t, t0, d = 0.45, seed = 1) { const u = (t - t0) / d; if (u < 0 || u > 1) return; const R = rng(seed);
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 3; i++) { const x = lerp(-200, 1300, u) + (R() - 0.5) * 500, y = R() * H, r = 500 + R() * 400; const a = 0.55 * Math.sin(Math.PI * u);
    const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(255,170,60,${a})`); g.addColorStop(0.5, `rgba(255,90,30,${a * 0.4})`); g.addColorStop(1, 'rgba(255,90,30,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  ctx.restore(); }
function cutFX(t, seg) { PIECES().forEach((p, i) => { if (p.seg !== seg || !p.impact) return; flash(t, p.t0, 0.55, 0.08); if (i % 2 === 0) lightLeak(t, p.t0, 0.45, i + 3); }); }
function pill(text, x, y, bg, fg = DK, size = 40, a = 1, s = 1) { ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s); ctx.font = `900 ${size}px "Inter Display"`; const w = ctx.measureText(text).width + size * 1.2;
  rr(-w / 2, -size * 0.8, w, size * 1.6, size * 0.8, bg); txt(text, 0, 2, { font: `900 ${size}px "Inter Display"`, fill: fg, shadow: false }); ctx.restore(); }
function viewfinder(t, a) { if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 6;
  const m = 60, L = 90; [[m, m + 60, 1, 1], [W - m, m + 60, -1, 1], [m, H - 300, 1, -1], [W - m, H - 300, -1, -1]].forEach(([x, y, sx, sy]) => { ctx.beginPath(); ctx.moveTo(x, y + sy * L); ctx.lineTo(x, y); ctx.lineTo(x + sx * L, y); ctx.stroke(); });
  if (Math.floor(t * 2) % 2 === 0) { ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(m + 40, m + 115, 14, 0, 7); ctx.fill(); }
  txt('REC', m + 100, m + 116, { font: '800 38px Inter', align: 'left' });
  const tc = Math.max(0, t - SEG.montage.t0) + 12.4; const ff = Math.floor((tc % 1) * 30);
  txt(`00:00:${String(Math.floor(tc)).padStart(2, '0')}:${String(ff).padStart(2, '0')}`, W - m - 20, m + 116, { font: '700 34px "JetBrains Mono"', align: 'right' });
  txt('SITE UPDATE · NETING, TUMPAT', 540, H - 330, { font: '800 32px Inter', ls: 4, alpha: 0.9 });
  ctx.restore(); }
function lowerThird(t, t0, t1, text) { const a = win(t, t0 + 0.05, t1, 0.08, 0.12); if (a <= 0 || !text) return; const x = lerp(-900, 0, easeOut((t - t0 - 0.05) / 0.25));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, 0); ctx.font = '900 54px "Inter Display"'; const w = ctx.measureText(text).width + 90;
  rr(50, 1110, w, 100, 14, 'rgba(255,255,255,0.96)'); rr(50, 1110, 16, 100, [14, 0, 0, 14], G); txt(text, 90, 1162, { font: '900 54px "Inter Display"', fill: DK, align: 'left', shadow: false }); ctx.restore(); }
function miniMap(t, a, prog, carT, hiMain) { if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; ctx.translate(W - 330, 560); const s = pop(a < 1 ? a * 0.22 : 1, 0.22); ctx.scale(s, s);
  rr(-250, -250, 500, 500, 30, 'rgba(10,30,15,0.85)', 'rgba(255,255,255,0.6)', 3);
  ctx.fillStyle = hiMain ? '#8a8a8a' : '#5c5c5c'; ctx.fillRect(-250, 150, 500, 60); ctx.setLineDash([22, 16]); ctx.strokeStyle = WH; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-250, 180); ctx.lineTo(250, 180); ctx.stroke(); ctx.setLineDash([]);
  for (let k = 0; k < 3; k++) { const x = ((carT * 160 + k * 180) % 560) - 280; ctx.fillStyle = [GOLD, RED, WH][k]; rr(x, k % 2 ? 182 : 158, 40, 20, 5, ctx.fillStyle); }
  txt('JALAN UTAMA', 0, 235, { font: '800 26px Inter', alpha: 0.9, shadow: false });
  ctx.lineCap = 'round'; const pts = [[-60, 150], [-60, 40], [10, -40], [10, -130]]; const n = clamp(prog);
  const tot = 3; const seg = Math.min(tot - 1, Math.floor(n * tot)); const fr = n * tot - seg;
  ctx.strokeStyle = G2; ctx.lineWidth = 26; ctx.shadowColor = G2; ctx.shadowBlur = 20; ctx.beginPath(); ctx.moveTo(...pts[0]);
  for (let i = 1; i <= seg; i++) ctx.lineTo(...pts[i]); if (n > 0) ctx.lineTo(lerp(pts[seg][0], pts[seg + 1][0], fr), lerp(pts[seg][1], pts[seg + 1][1], fr)); ctx.stroke(); ctx.shadowBlur = 0;
  if (n > 0.95) { drawIcon('house', 10, -175, 1.6); }
  txt('JALAN MASUK', 120, 40, { font: '800 26px Inter', fill: G2, alpha: clamp(n * 3), shadow: false }); txt('TAPAK', 10, -235, { font: '900 28px "Inter Display"', alpha: n > 0.95 ? 1 : 0, shadow: false });
  ctx.restore(); }
function hook2(t) { cutFX(t, 'hook'); const hp = PIECES().filter(p => p.seg === 'hook');
  if (t < hp[1].t0) txt('PART 2', 540, 960, { font: '900 230px "Inter Display"', fill: GOLD, scale: pop(t, 0.18) * (1 + 0.15 * t), stroke: '#000', lw: 20, rot: -0.04 });
  else pill('PART 2', 150, 110, GOLD, DK, 44, 1, pop(t - hp[1].t0, 0.2));
  const c2 = hp[1].t0, c3 = hp[2].t0, vo = TL.hookVO;
  if (t > c2) { const [a, b] = shakeOff(t, c2, 12, 0.3); txt('JALAN MASUK', 540 + a, 330 + b, { font: '900 120px "Inter Display"', scale: pop(t - c2, 0.2), stroke: '#000', lw: 16 }); }
  if (t > c3) txt('SEDANG DIBINA!', 540, 460, { font: '900 104px "Inter Display"', fill: G2, scale: pop(t - c3, 0.2), stroke: '#000', lw: 14 });
  if (t > vo) { const [a, b] = shakeOff(t, vo + 0.5, 16, 0.35); txt('KASI LUNCUR!', 540 + a, 1400 + b, { font: '900 150px "Inter Display"', fill: GOLD, scale: pop(t - vo, 0.24), stroke: '#000', lw: 18, rot: -0.05 }); } }
function logo2(t) { logo(t); const lt = t - SEG.logo.t0; if (lt > 1.6) pill('PART 2', 540, 1580, GOLD, DK, 46, clamp((lt - 1.6) / 0.15), pop(lt - 1.6, 0.2)); }
function recap(t) { const s = SEG.recap, lt = t - s.t0; const a = win(t, s.t0, s.t1, 0.15, 0.2);
  pill('RECAP PART 1', 540, 470, G, WH, 46, a, pop(lt, 0.2));
  const rows = [['house', '5 LOT · RUMAH + TANAH'], ['rm', 'RM420K · SEBELUM SIAP'], ['pin', 'NETING, TUMPAT']];
  rows.forEach(([ic, tx], i) => { const u = lt - 0.25 - i * 0.22; if (u < 0) return; const x = lerp(-900, 0, easeOut(u / 0.3)); ctx.save(); ctx.globalAlpha = a; ctx.translate(x, 0);
    rr(110, 600 + i * 170, 860, 140, 30, 'rgba(255,255,255,0.97)');
    if (ic === 'rm') { ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(200, 670 + i * 170, 40, 0, 7); ctx.fill(); txt('RM', 200, 672 + i * 170, { font: '900 30px "Inter Display"', fill: DK, shadow: false }); } else drawIcon(ic, 200, 672 + i * 170, 1.3);
    txt(tx, 270, 672 + i * 170, { font: '900 56px "Inter Display"', fill: DK, align: 'left', shadow: false }); ctx.restore(); }); }
function voiceScenes(t, k) { const s = SEG[k];
  const mapIn = SEG.v2.t0, mapOut = SEG.v5.t0 + 0.2; const ma = win(t, mapIn, mapOut, 0.2, 0.25);
  miniMap(t, ma, clamp((t - SEG.v2.t0) / (SEG.v3.t1 - SEG.v2.t0)), t, k === 'v4');
  if (k === 'v1') pinLabel(t, s.t0 + 0.1, s.t1, 'PART 2: JALAN MASUK', 'Tapak 5 lot · Neting, Tumpat', 300, 'road');
  if (k === 'v2') pinLabel(t, s.t0 + 0.1, s.t1, 'JALAN MASUK BAHARU', 'Sampai ke hujung tapak', 300, 'road');
  if (k === 'v3') pinLabel(t, s.t0 + 0.05, s.t1, 'INILAH JALANNYA', 'Proses menambun bermula', 300, 'pin');
  if (k === 'v4') pinLabel(t, s.t0 + 0.05, s.t1, 'JALAN UTAMA', 'Kereta lalu-lalang', 300, 'arrows');
  if (k === 'v5') { const lt = t - s.t0; ctx.save(); ctx.globalAlpha = win(t, s.t0, s.t1 + 0.3, 0.08, 0.2); ctx.translate(540, 420); ctx.scale(pop(lt, 0.24), pop(lt, 0.24)); ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 30;
    rr(-430, -110, 860, 220, 40, G); ctx.shadowColor = 'transparent'; drawIcon('check', -330, 0, 1.6); ctx.restore(); ctx.save(); ctx.globalAlpha = win(t, s.t0, s.t1 + 0.3, 0.08, 0.2);
    txt('DEKAT JALAN UTAMA', 600, 420, { font: '900 60px "Inter Display"', scale: pop(lt, 0.24), shadow: false }); ctx.restore(); }
  if (k === 'v6') { const lt = t - s.t0; banner(t, s.t0 + 0.1, s.t1, 'FOOTAGE', 'KERJA DI TAPAK ⬇', G, 380, false); } }
function tanah(t) { const s = SEG.tanah, lt = t - s.t0, B = TL.beat;
  const lp = easeOut(lt / 0.6); ctx.save(); ctx.globalAlpha = lp * win(t, s.t0, s.t1, 0.1, 0.3); ctx.lineWidth = 5; ctx.strokeStyle = G2; ctx.setLineDash([16, 10]);
  [125, 332, 540, 748, 955].forEach((x, i) => { const hl = lt > 0.3 + i * 0.12; ctx.fillStyle = hl ? 'rgba(60,203,90,0.22)' : 'rgba(60,203,90,0)'; ctx.beginPath(); ctx.moveTo(x - 90, 1215); ctx.lineTo(x + 90, 1215); ctx.lineTo(x + 102, 1420); ctx.lineTo(x - 102, 1420); ctx.closePath(); ctx.fill(); ctx.stroke();
    if (hl) txt(`LOT ${i + 1}`, x, 1318, { font: '900 34px "Inter Display"', stroke: '#000', lw: 6 }); }); ctx.restore();
  const cards = [[0, 'KAWASAN TAPAK', '5 LOT', 'land'], [4 * B, 'KELUASAN TANAH', '±5,700 KP', 'land'], [7 * B, 'KELUASAN RUMAH', '±1,500 KP', 'house']];
  cards.forEach(([o, l, v, ic], i) => { const t0 = s.t0 + o, t1 = i < 2 ? s.t0 + cards[i + 1][0] : s.t0 + 10 * B; statCard(t, t0, t1, ic, l, v, 360); });
  const ct = s.t0 + 10 * B; if (t > ct - 0.05) { const items = ['DEKAT JALAN UTAMA', 'AKSES LORI & KERETA', 'TAPAK SEDANG DITAMBUN'];
    pill('POTENSI TAPAK', 540, 250, GOLD, DK, 46, win(t, ct, s.t1 + 0.2, 0.1, 0.2), pop(t - ct, 0.2));
    items.forEach((x, i) => { const u = t - ct - i * B * 0.5; if (u < 0) return; const xx = lerp(-900, 0, easeOut(u / 0.25)); ctx.save(); ctx.globalAlpha = win(t, ct, s.t1 + 0.2, 0.1, 0.2); ctx.translate(xx, 0);
      rr(130, 330 + i * 140, 820, 110, 55, 'rgba(255,255,255,0.96)'); drawIcon('check', 200, 385 + i * 140, 1.0); txt(x, 260, 387 + i * 140, { font: '900 52px "Inter Display"', fill: DK, align: 'left', shadow: false }); ctx.restore(); }); } }
function tanahStrip(t) { const s = SEG.tanah; const a = win(t, s.t0 + 0.2, s.t1, 0.2, 0.2); txt('TAPAK PROJEK AA LAND', 540, 1500, { font: '900 64px "Inter Display"', alpha: a, stroke: '#000', lw: 10 }); txt('Neting, Tumpat · Kelantan', 540, 1580, { font: '700 44px Inter', fill: G2, alpha: a, stroke: '#000', lw: 8 }); }
function montage(t) { const s = SEG.montage; viewfinder(t, win(t, s.t0, SEG.siap.t1, 0.1, 0.15)); cutFX(t, 'montage');
  PIECES().filter(p => p.seg === 'montage').forEach(p => { if (t < p.t0 || t >= p.t0 + p.d) return; lowerThird(t, p.t0, p.t0 + p.d + (p.label ? 0.6 : 0), p.label);
    if (p.speed > 1.01) pill(`▶▶ x${p.speed.toFixed(1)}`, 900, 300, 'rgba(0,0,0,0.6)', WH, 36);
    if (p.slow) pill('SLOW-MO', 900, 300, 'rgba(0,0,0,0.6)', GOLD, 36); });
  // keep previous label visible across short unlabeled shots
  const prev = PIECES().filter(p => p.seg === 'montage' && p.label && t >= p.t0 && t < p.t0 + p.d + TL.beat * 2);
  prev.forEach(p => { if (!(t >= p.t0 && t < p.t0 + p.d)) lowerThird(t, p.t0, p.t0 + p.d + TL.beat * 2, p.label); }); }
function split(t) { const s = SEG.split, lt = t - s.t0; const w = easeOut(lt / 0.35);
  ctx.fillStyle = WH; ctx.fillRect(0, 954, W * w, 12); ctx.save(); ctx.shadowColor = G2; ctx.shadowBlur = 25; ctx.fillStyle = G2; ctx.fillRect(0, 957, W * w, 6); ctx.restore();
  pill('SEBELUM', 200, 120, 'rgba(0,0,0,0.7)', WH, 50, clamp(lt / 0.2), pop(lt, 0.2)); pill('SELEPAS', 200, 1040, G, WH, 50, clamp((lt - 0.35) / 0.2), pop(lt - 0.35, 0.2));
  txt('LALUAN RUMPUT', 540, 860, { font: '900 64px "Inter Display"', alpha: clamp((lt - 0.2) / 0.2), stroke: '#000', lw: 10 });
  txt('JALAN TANAH MERAH', 540, 1780, { font: '900 64px "Inter Display"', fill: G2, alpha: clamp((lt - 0.55) / 0.2), stroke: '#000', lw: 10 });
  ctx.save(); ctx.translate(540, 960); const vs = pop(lt - 0.3, 0.2); ctx.scale(vs, vs); ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(0, 0, 70, 0, 7); ctx.fill(); txt('VS', 0, 4, { font: '900 64px "Inter Display"', fill: DK, shadow: false }); ctx.restore(); }
function siap(t) { const s = SEG.siap, lt = t - s.t0; cutFX(t, 'siap'); viewfinder(t, win(t, s.t0, s.t1, 0.1, 0.15));
  banner(t, s.t0 + 0.1, s.t1, 'JALAN MASUK', 'HAMPIR SIAP ✅', G, 420, false);
  if (lt > 0.4 && lt < 1.2) { const x = lerp(-300, 1400, (lt - 0.4) / 0.8); const gg = ctx.createLinearGradient(x - 150, 0, x + 150, 0); gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(0.5, 'rgba(255,255,255,0.35)'); gg.addColorStop(1, 'rgba(255,255,255,0)'); ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = gg; ctx.fillRect(0, 280, W, 280); ctx.restore(); } }
function end2(t) { endCard(t); const lt = t - SEG.end.t0; pill('PART 3 AKAN DATANG', 540, 90, GOLD, DK, 40, clamp((lt - 0.2) / 0.2), pop(lt - 0.2, 0.2));
  if (lt > 1.5) txt('FOLLOW UNTUK UPDATE PROJEK', 540, 1690, { font: '800 44px Inter', alpha: clamp((lt - 1.5) / 0.3) }); }
function render(t) {
  ctx.clearRect(0, 0, W, H); const k = TL.segs.find(s => t >= s.t0 && t < s.t1)?.key || 'end';
  if (k === 'hook') hook2(t); else if (k === 'logo') logo2(t); else if (k === 'end') end2(t); else if (k === 'recap') recap(t);
  else if (k[0] === 'v') voiceScenes(t, k); else if (k === 'tanah') { tanah(t); tanahStrip(t); } else if (k === 'montage') montage(t); else if (k === 'split') split(t); else if (k === 'siap') siap(t);
  if (k[0] === 'v') captions(t);
  if (k !== 'logo') progress(t);
}
window.render = render;
window.ready = () => Promise.all([...document.images].filter(i => i.src).map(i => i.decode()));
</script>
</body></html>
