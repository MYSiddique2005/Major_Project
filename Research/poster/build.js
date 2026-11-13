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
  const W = 980, rowH = 112, top = 120, left = 250, right = 60, plotW = W - left - right, barH = 34, gap = 4;
  const H = top + HELDOUT.length * rowH + 50;
  const x = v => left + (v / 100) * plotW;
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Held-out test: errors detected and false alarms by method">`;
  // legend
  s += `<rect x="10" y="10" width="28" height="28" rx="4" fill="${NAVY}"/><text x="50" y="33" class="lg">Errors detected (of 102)</text>`;
  s += `<rect x="10" y="56" width="28" height="28" rx="4" fill="${ORANGE}"/><text x="50" y="79" class="lg">False alarms (of 103 correct texts)</text>`;
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

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>IntelliERP poster</title>
<style>
  @page { size: 841mm 594mm; margin: 0; }
  :root { --red: #C8102E; --navy: ${NAVY}; --ink: ${INK}; --muted: ${MUTED}; --bg: #EEF2F7; --card: #FFFFFF; --soft: #F4F7FB; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 3179px; height: 2245px; }
  body { background: var(--bg); color: var(--ink); font-family: 'Noto Sans', 'DejaVu Sans', sans-serif; font-size: 29px; line-height: 1.38; overflow: hidden; }
  header { height: 300px; display: grid; grid-template-columns: 560px 1fr 860px; align-items: center; padding: 0 60px; background: #fff; border-bottom: 14px solid var(--red); }
  .uni { display: flex; align-items: center; gap: 18px; } .uni .mark { height: 170px; margin: 0 -14px 0 -20px; }
  .uni b { font-size: 120px; color: var(--red); letter-spacing: 4px; line-height: 1; }
  .uni span { font-size: 38px; font-weight: 600; color: #333; line-height: 1.15; }
  .logo { max-height: 200px; max-width: 520px; }
  .title { text-align: center; }
  .title h1 { font-size: 104px; color: var(--navy); letter-spacing: 1px; line-height: 1.05; }
  .title p { font-size: 44px; font-weight: 600; color: var(--ink); margin-top: 14px; line-height: 1.2; }
  .fac { text-align: right; font-size: 34px; font-weight: 700; color: var(--ink); line-height: 1.3; }
  .fac small { display: block; white-space: nowrap; font-size: 26px; font-weight: 500; color: var(--muted); margin-top: 10px; }
  main { display: grid; grid-template-columns: 640px 760px 860px 1fr; gap: 36px; padding: 36px 44px 0; height: 1945px; }
  .col { display: flex; flex-direction: column; gap: 30px; min-height: 0; }
  section { background: var(--card); border-radius: 22px; box-shadow: 0 3px 10px rgba(20,40,80,.08); overflow: hidden; }
  section > h2 { background: var(--red); color: #fff; font-size: 40px; padding: 14px 30px; letter-spacing: .5px; }
  .body { padding: 24px 30px 28px; }
  .body p + p, .body p + ul, .body ul + p { margin-top: 14px; }
  ul { padding-left: 34px; } li { margin: 8px 0; } li::marker { color: var(--red); }
  b, strong { color: var(--ink); }
  .grow { flex: 1; }
  .rq { display: grid; grid-template-columns: 96px 1fr; gap: 6px 18px; align-items: start; }
  .rq .tag { background: var(--navy); color: #fff; font-weight: 700; border-radius: 10px; text-align: center; padding: 6px 0; font-size: 28px; }
  .rq div:not(.tag) { margin-bottom: 14px; }
  .data { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-top: 8px; }
  .data div { background: var(--soft); border-radius: 14px; padding: 10px 14px; font-size: 23px; line-height: 1.2; color: var(--muted); }
  .data b { display: block; font-size: 38px; color: var(--navy); line-height: 1.15; }
  .flow { display: flex; flex-direction: column; gap: 0; }
  .step { display: grid; grid-template-columns: 70px 1fr; gap: 18px; align-items: center; background: var(--soft); border-radius: 16px; padding: 16px 20px; border-left: 10px solid var(--navy); }
  .step.llm { border-left-color: ${ORANGE}; }
  .step .n { width: 62px; height: 62px; border-radius: 50%; background: var(--navy); color: #fff; font-weight: 700; font-size: 32px; display: grid; place-items: center; }
  .step.llm .n { background: ${ORANGE}; }
  .step b { font-size: 31px; } .step span { display: block; font-size: 25px; color: var(--muted); line-height: 1.3; }
  .arrow { text-align: center; color: var(--muted); font-size: 34px; line-height: 1.1; }
  code { font-family: 'DejaVu Sans Mono', monospace; font-size: 23px; background: #fff; border: 2px solid #DCE3EE; border-radius: 8px; padding: 2px 8px; color: var(--ink); }
  .outcomes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 4px; }
  .outcomes div { border-radius: 14px; padding: 12px 10px; text-align: center; font-size: 24px; line-height: 1.25; border: 3px solid; background: #fff; }
  .ok { border-color: #2E7D4F !important; } .ok b { color: #2E7D4F; }
  .bad { border-color: var(--red) !important; } .bad b { color: var(--red); }
  .unk { border-color: #8A93A3 !important; } .unk b { color: #5B6577; }
  .key { margin-top: 18px; background: var(--navy); color: #fff; border-radius: 16px; padding: 18px 24px; font-size: 30px; font-weight: 600; text-align: center; }
  .defs { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .def { background: var(--soft); border-radius: 16px; padding: 18px 20px; }
  .def h3 { font-size: 32px; color: var(--navy); margin-bottom: 6px; }
  .def p { font-size: 25px; line-height: 1.32; }
  .stack { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .stack div { background: var(--soft); border-radius: 12px; padding: 10px 14px; font-size: 23px; color: var(--muted); line-height: 1.25; }
  .stack b { display: block; font-size: 26px; color: var(--ink); }
  .heroes { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .hero { background: var(--soft); border-radius: 18px; padding: 18px 22px; }
  .hero .big { font-size: 60px; font-weight: 800; color: var(--navy); line-height: 1; white-space: nowrap; }
  .hero .big small { font-size: 40px; font-weight: 700; color: var(--muted); }
  .hero p { font-size: 25px; margin-top: 10px; line-height: 1.3; }
  svg .lg { font-size: 26px; fill: ${INK}; } svg .ax { font-size: 24px; fill: ${MUTED}; }
  svg .nm { font-size: 27px; fill: ${INK}; } svg .nm.b { font-weight: 800; }
  svg .vl { font-size: 26px; font-weight: 700; fill: ${INK}; }
  .note { font-size: 23px; color: var(--muted); line-height: 1.32; margin-top: 10px; }
  .honest { border: 4px dashed ${ORANGE}; border-radius: 16px; padding: 16px 22px; background: #FFF6EE; margin-top: 18px; font-size: 26px; line-height: 1.34; }
  .shot { border-radius: 14px; border: 3px solid #D5DCE7; width: 100%; overflow: hidden; } .shot img { display: block; }
  .cap { font-size: 23px; color: var(--muted); margin: 8px 0 18px; line-height: 1.3; }
  .me { display: grid; grid-template-columns: 190px 1fr; gap: 4px 12px; font-size: 24px; }
  .me span { color: var(--muted); }
  .right { display: flex; align-items: center; justify-content: flex-end; gap: 28px; }
  .repo { text-align: center; } .repo svg { width: 210px; height: 210px; display: block; }
  .repo span { font-size: 22px; font-weight: 700; color: var(--ink); }
  .ack { font-size: 24px; line-height: 1.34; }
</style></head><body>
<header>
  <div>${logo}</div>
  <div class="title"><h1>IntelliERP</h1><p>Evidence-Grounded Hallucination Detection and Verification<br>for LLM-Based ERP Decision Support</p></div>
  <div class="right"><div class="fac">Faculty of Data Science and<br>Information Technology (FDSIT)<small>Final Year Project · ${META.session}<br>Project ID ${META.projectId}</small></div>${qr ? `<div class="repo">${qr}<span>Code on GitHub</span></div>` : ''}</div>
</header>
<main>
  <div class="col">
    <section><h2>Problem Statement</h2><div class="body">
      <p>Companies are connecting <b>large language models (LLMs)</b> to their ERP systems to answer questions, explain risks and suggest orders. But an LLM can <b>state false facts with confidence</b>:</p>
      <ul>
        <li>a wrong stock level or demand figure,</li>
        <li>an invented company rule or threshold,</li>
        <li>a permission the user does not have.</li>
      </ul>
      <p>A wrong figure can lead to a <b>wrong purchase order</b>. Today's ERP agents control what the model may <i>do</i>, not whether what it <i>says</i> is true.</p>
    </div></section>
    <section><h2>Objectives</h2><div class="body rq">
      <div class="tag">RQ1</div><div><b>Prevent</b> errors: build an ERP system with a grounded AI assistant; measure the effect of grounding.</div>
      <div class="tag">RQ2</div><div><b>Detect</b> errors: design <b>TRACE</b>, a typed run-time verifier; test it against other checkers.</div>
      <div class="tag">RQ3</div><div>Measure the <b>effect and cost</b>: harm, time and repeatability.</div>
    </div></section>
    <section class="grow"><h2>System and Data</h2><div class="body">
      <p>Sales, inventory and procurement with four user roles, approvals and an audit log, on the <b>Wide World Importers</b> dataset.</p>
      <div class="data">
        <div><b>72,696</b>sales lines</div><div><b>5,443</b>purchase orders</div>
        <div><b>227</b>products</div><div><b>7</b>suppliers</div>
        <div><b>15</b>AI tools</div><div><b>269</b>tests pass</div>
      </div>
      <p class="note" style="font-size:24px;margin-top:14px"><b>Built with</b> React 19 + TypeScript · Python FastAPI · PostgreSQL · Gemini 3.5 Flash-Lite and Gemma 4 31B (free API)</p>
    </div></section>
  </div>

  <div class="col">
    <section><h2>Solution: Two Defences</h2><div class="body">
      <div class="defs">
        <div class="def"><h3>1 · Prevent by grounding</h3><p>Rule-based analytics decide what is wrong. The model reads data only through tools that check the user's role, and gets the company's rules from a <b>knowledge base</b> of 41 passages generated partly from the code.</p></div>
        <div class="def"><h3>2 · Detect by verification</h3><p><b>TRACE</b> turns each statement of an answer into a typed assertion and checks it with the system's own code <b>before the user sees it</b>.</p></div>
      </div>
    </div></section>
    <section class="grow"><h2>How TRACE Works</h2><div class="body">
      <div class="flow">
        <div class="step"><div class="n">1</div><div><b>Assistant writes a draft answer</b><span>"P082 has 120 units in stock, so no reorder is needed."</span></div></div>
        <div class="arrow">▼</div>
        <div class="step llm"><div class="n">2</div><div><b>LLM extracts typed assertions</b><span><code>P082 · stock_on_hand · = 120</code><br>64 attributes, 24 rule keys, 21 actions: state, derived results and company policy</span></div></div>
        <div class="arrow">▼</div>
        <div class="step"><div class="n">3</div><div><b>Schema and grounding checks</b><span>Is the subject named in the text? Units, dates and ambiguous terms resolved.</span></div></div>
        <div class="arrow">▼</div>
        <div class="step"><div class="n">4</div><div><b>Deterministic verifier</b><span>The system's own tested code computes the true value: <code>stock_on_hand(P082) = 0</code></span></div></div>
        <div class="arrow">▼</div>
        <div class="outcomes">
          <div class="ok"><b>✓ Supported</b><br>shown as checked</div>
          <div class="bad"><b>✗ Contradicted</b><br>sent back once to correct, then a warning</div>
          <div class="unk"><b>? Unverifiable</b><br>outside the language</div>
        </div>
      </div>
      <div class="key">The model only extracts. Code decides what is true.</div>
      <p class="note">TRACE was frozen (file hashes recorded) before the held-out test was created, so the test could not influence its design.</p>
    </div></section>
  </div>

  <div class="col">
    <section><h2>Key Results</h2><div class="body">
      <div class="heroes">
        <div class="hero"><div class="big">25.9% <small>→</small> 2.4%</div><p>False statements in the assistant's own answers, <b>without → with</b> the knowledge base</p></div>
        <div class="hero"><div class="big">8–9 <small>→</small> 32<small>/32</small></div><p>Paired questions answered correctly, <b>without → with</b> grounding (p &lt; 0.0001)</p></div>
        <div class="hero"><div class="big">69% <small>/</small> 4%</div><p>Unseen errors detected by TRACE / false alarms on correct text</p></div>
        <div class="hero"><div class="big">0</div><p>Misses or false alarms caused by a verification function: every failure is <b>explainable</b></p></div>
      </div>
    </div></section>
    <section class="grow"><h2>Held-out Test: TRACE vs Others</h2><div class="body">
      <p style="font-size:26px">102 model-written errors and 103 correct paraphrases, written after TRACE was frozen. Higher blue is better; lower orange is better.</p>
      ${heldoutChart()}
      <p class="note">TRACE detected <b>70 errors against 15</b> for the pattern verifier (p &lt; 10<sup>−15</sup>). The two LLM judges detected slightly more, but not significantly (p = 0.36). The Gemini judge raised <b>4× as many false alarms</b> (p = 0.036); the Gemma judge about as many as TRACE.</p>
      <div class="honest"><b>Honest limit:</b> on the assistant's <i>own</i> mistakes TRACE found only <b>4 of 19</b>. Most were wrong definitions ("what a status means"), which its language cannot express yet. A false alarm can also make a correct answer wrong when it is corrected automatically.</div>
    </div></section>
  </div>

  <div class="col">
    <section><h2>The System in Use</h2><div class="body">
      ${crop('ui-ai-assistant.png', 290, 236, 880, 520)}
      <p class="cap">The AI assistant: every answer shows the data used, the company rules consulted and the check results.</p>
      ${crop('ui-po-ai-draft.png', 286, 566, 1110, 300)}
      <p class="cap" style="margin-bottom:0">The AI can only <b>draft</b> a purchase order. A different person must review and approve it, and every step is in the audit log.</p>
    </div></section>
    <section><h2>Conclusion</h2><div class="body">
      <p><b>The facts in an AI answer should be decided by the system that owns them, not by the model.</b> Grounding was the largest factor in correctness; typed verification makes the remaining mistakes visible and explainable.</p>
      <p style="font-size:24px"><b>Next:</b> a user study, a wider assertion language for definitions, and warnings instead of automatic correction.</p>
    </div></section>
    <section class="grow"><h2>Acknowledgement</h2><div class="body ack">
      I sincerely thank my supervisor <b>Dr. Zeyad Ahmed</b> for continuous guidance, <b>INTI International University</b> for the resources to complete this project, and <b>Prof. Ashish K. Soni</b> (G H Raisoni College of Engineering, Nagpur) for support during my mobility semester.
      <div class="me" style="margin-top:18px">
        <span>Name</span><b>${NAME}</b>
        <span>Student ID</span><b>${META.studentId}</b>
        <span>Programme</span><b>BCSI-M (mobility student)</b>
        <span>Home institution</span><b>G H Raisoni College of Engineering, Nagpur</b>
      </div>
    </div></section>
  </div>
</main>
</body></html>`;

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
