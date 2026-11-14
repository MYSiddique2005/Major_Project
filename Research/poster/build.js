// The FYP poster (A1 landscape). Writes out/poster.html, out/poster.pdf (print, 841 x 594 mm) and
// out/poster.png (preview), and copies the PDF and PNG to ~/Documents/IntelliERP/1-Final-Submission.
//   node build.js
// Every number is taken from the final evaluation (LLM/evaluation/results); see Research/report/src/ch6.js.
// Cover details come from ../report/src/meta.js, which reads the uncommitted meta.local.js for personal numbers.
// Header: the full university logo at inti-logo.png if present, otherwise the mark inti-mark.png with the name.
// The QR code (qr-github.svg) links to the public repository.
const fs = require('fs');
const os = require('os');
const path = require('path');
const puppeteer = require('../report/node_modules/puppeteer-core');
const META = require('../report/src/meta');

const OUT = path.join(__dirname, 'out');
const ASSETS = path.join(__dirname, '..', 'report', 'assets');
fs.mkdirSync(OUT, { recursive: true });

const NAME = 'Mohammad Yasin Naeemuddin Siddique';  // as on the presentation list
const logo = fs.existsSync(path.join(__dirname, 'inti-logo.png'))
  ? `<img class="logo" src="file://${path.join(__dirname, 'inti-logo.png')}" alt="INTI International University">`
  : `<div class="uni">${fs.existsSync(path.join(__dirname, 'inti-mark.png')) ? `<img class="mark" src="file://${path.join(__dirname, 'inti-mark.png')}" alt="">` : ''}<b>INTI</b><span>International<br>University</span></div>`;
const REPO = 'github.com/MYSiddique2005/Major_Project';
const qr = fs.existsSync(path.join(__dirname, 'qr-github.svg')) ? fs.readFileSync(path.join(__dirname, 'qr-github.svg'), 'utf8') : '';
const img = name => `file://${path.join(ASSETS, name)}`;
// A screenshot cropped to the region (x, y, w, h) of its 1440 x 900 image, scaled to the column width.
const crop = (name, x, y, w, h) => `<div class="shot" style="aspect-ratio:${w}/${h}"><img src="${img(name)}" alt="" style="width:${(1440 / w) * 100}%;margin-left:${(-x / w) * 100}%;margin-top:${(-y / w) * 100}%"></div>`;

// Held-out test (102 model-written errors, 103 correct paraphrases), final results.
const HELDOUT = [
  ['Pattern verifier', 15, 2, false],
  ['MiniCheck', 37, 21, false],
  ['TRACE (ours)', 69, 4, true],
  ['Gemma judge', 75, 7, false],
  ['Gemini judge', 78, 17, false],
];
const NAVY = '#1F4E9C', ORANGE = '#E8833A', INK = '#1B2433', MUTED = '#5B6577', GRID = '#E3E7EE';

function heldoutChart() {
  const W = 980, rowH = 86, top = 62, left = 250, right = 60, plotW = W - left - right, barH = 30, gap = 4;
  const H = top + HELDOUT.length * rowH + 46;
  const x = v => left + (v / 100) * plotW;
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Held-out test: errors detected and false alarms by method">`;
  // legend
  s += `<rect x="10" y="10" width="28" height="28" rx="4" fill="${NAVY}"/><text x="50" y="33" class="lg">Errors detected (of 102)</text>`;
  s += `<rect x="470" y="10" width="28" height="28" rx="4" fill="${ORANGE}"/><text x="510" y="33" class="lg">False alarms (of 103)</text>`;
  for (const v of [0, 25, 50, 75, 100]) {
    s += `<line x1="${x(v)}" x2="${x(v)}" y1="${top - 10}" y2="${top + HELDOUT.length * rowH}" stroke="${GRID}" stroke-width="2"/>`;
    s += `<text x="${x(v)}" y="${top + HELDOUT.length * rowH + 36}" text-anchor="middle" class="ax">${v}%</text>`;
  }
  HELDOUT.forEach(([name, det, fa, mine], i) => {
    const y = top + i * rowH + 18;
    if (mine) s += `<rect x="6" y="${y - 14}" width="${W - 12}" height="${2 * barH + gap + 28}" rx="10" fill="#FDECEC"/>`;
    s += `<text x="${left - 18}" y="${y + barH + 2}" text-anchor="end" class="${mine ? 'nm b' : 'nm'}">${name}</text>`;
    s += `<rect x="${left}" y="${y}" width="${x(det) - left}" height="${barH}" rx="4" fill="${NAVY}"/>`;
    s += `<text x="${x(det) + 10}" y="${y + barH - 8}" class="vl">${det}%</text>`;
    s += `<rect x="${left}" y="${y + barH + gap}" width="${Math.max(x(fa) - left, 4)}" height="${barH}" rx="4" fill="${ORANGE}"/>`;
    s += `<text x="${x(fa) + 10}" y="${y + 2 * barH + gap - 8}" class="vl">${fa}%</text>`;
  });
  return s + '</svg>';
}

const html = require('./layout')({ logo, qr, META, NAME, crop, heldoutChart, NAVY, ORANGE, INK, MUTED });

fs.writeFileSync(path.join(OUT, 'poster.html'), html);

(async () => {
  const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox', '--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 3179, height: 2245, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(OUT, 'poster.html'), { waitUntil: 'networkidle0' });
  // report any box whose content overflows, so nothing is cut off silently
  const overflow = await page.evaluate(() => [...document.querySelectorAll('section, .col, main')]
    .filter(el => el.scrollHeight > el.clientHeight + 2)
    .map(el => (el.querySelector('h2') || el).textContent.slice(0, 40) + ` (+${el.scrollHeight - el.clientHeight}px)`));
  console.log(overflow.length ? 'OVERFLOW: ' + overflow.join('; ') : 'no overflow');
  await page.pdf({ path: path.join(OUT, 'poster.pdf'), width: '841mm', height: '594mm', printBackground: true, pageRanges: '1' });
  await page.screenshot({ path: path.join(OUT, 'poster.png') });
  await browser.close();
  const docs = path.join(os.homedir(), 'Documents', 'IntelliERP', '1-Final-Submission');
  fs.copyFileSync(path.join(OUT, 'poster.pdf'), path.join(docs, 'IntelliERP-FYP-Poster.pdf'));
  fs.copyFileSync(path.join(OUT, 'poster.png'), path.join(docs, 'IntelliERP-FYP-Poster.png'));
  console.log('written ~/Documents/IntelliERP/1-Final-Submission/IntelliERP-FYP-Poster.pdf and .png');
})();
