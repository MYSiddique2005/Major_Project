// The poster's page (HTML), A1 landscape at 3179 x 2245 px. Called by build.js with the pieces it prepares.
// Layout: header (logo, title, people, QR) and three columns:
//   left   - problem, objectives, the two defences, the system in use
//   centre - the research methodology diagram and how TRACE works
//   right  - key results, the held-out chart, the honest limit, conclusion and acknowledgement
module.exports = ({ logo, qr, META, NAME, crop, heldoutChart, NAVY, ORANGE, INK, MUTED }) => `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>IntelliERP poster</title>
<style>
  @page { size: 841mm 594mm; margin: 0; }
  :root { --red: #C8102E; --navy: ${NAVY}; --ink: ${INK}; --muted: ${MUTED}; --bg: #EEF2F7; --soft: #F3F6FB;
          --green: #2E7D4F; --orange: ${ORANGE}; --purple: #6D3FC0; --teal: #0F766E; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 3179px; height: 2245px; }
  body { background: var(--bg); color: var(--ink); font-family: 'Noto Sans', 'DejaVu Sans', sans-serif; font-size: 30px;
         line-height: 1.33; overflow: hidden; }
  b, strong { font-weight: 700; }

  /* ---------------- header */
  header { height: 330px; display: grid; grid-template-columns: 680px 1fr 700px; align-items: center; gap: 30px;
           padding: 0 56px; background: #fff; border-bottom: 16px solid var(--red); }
  .logo { width: 640px; display: block; }
  .uni { display: flex; align-items: center; gap: 18px; } .uni b { font-size: 110px; color: var(--red); }
  .title { text-align: center; }
  .title h1 { font-size: 100px; color: var(--navy); line-height: 1; letter-spacing: 1px; }
  .title .sub { font-size: 46px; font-weight: 700; margin-top: 12px; line-height: 1.18; }
  .title .who { font-size: 27px; color: var(--muted); margin-top: 16px; }
  .title .who b { color: var(--ink); }
  .right { display: flex; align-items: center; justify-content: flex-end; gap: 26px; }
  .fac { text-align: right; font-size: 31px; font-weight: 700; line-height: 1.3; }
  .fac small { display: block; font-size: 26px; font-weight: 500; color: var(--muted); margin-top: 8px; white-space: nowrap; }
  .repo { text-align: center; } .repo svg { width: 200px; height: 200px; display: block; }
  .repo span { font-size: 22px; font-weight: 700; }

  /* ---------------- columns and cards */
  main { display: grid; grid-template-columns: 860px 1fr 960px; gap: 40px; padding: 38px 48px 0; height: 1899px; }
  .col { display: flex; flex-direction: column; gap: 32px; min-height: 0; }
  section { background: #fff; border-radius: 24px; box-shadow: 0 3px 12px rgba(20,40,80,.08); overflow: hidden; }
  section > h2 { background: var(--red); color: #fff; font-size: 46px; padding: 16px 32px; letter-spacing: .5px; }
  section > h2 small { font-size: 30px; font-weight: 500; opacity: .9; margin-left: 12px; }
  .body { padding: 20px 30px 24px; }
  .grow { flex: 1; }
  ul.clean { list-style: none; } ul.clean li { position: relative; padding-left: 40px; margin: 6px 0; }
  ul.clean li::before { content: ''; position: absolute; left: 6px; top: 13px; width: 20px; height: 20px; border-radius: 50%; background: var(--red); }

  /* problem */
  .lead { font-size: 30px; margin-bottom: 4px; }
  /* objectives */
  .obj { display: grid; grid-template-columns: 64px 1fr; gap: 10px 18px; align-items: start; }
  .obj .n { width: 58px; height: 58px; border-radius: 50%; background: var(--navy); color: #fff; font-weight: 800; font-size: 34px;
            display: grid; place-items: center; }
  .obj p { padding-top: 6px; }
  /* defences */
  .def { display: grid; grid-template-columns: 1fr; gap: 12px; }
  .def div { border-radius: 18px; padding: 12px 22px; border-left: 14px solid; background: var(--soft); }
  .def .p { border-color: var(--green); } .def .d { border-color: var(--purple); } .def .a { border-color: var(--orange); }
  .def h3 { font-size: 32px; margin-bottom: 2px; }
  .def .p h3 { color: var(--green); } .def .d h3 { color: var(--purple); } .def .a h3 { color: #B4570F; }
  .def p { font-size: 27px; line-height: 1.3; }
  .shot { border-radius: 14px; border: 3px solid #D5DCE7; width: 100%; overflow: hidden; } .shot img { display: block; }
  .tiles { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .tiles div { background: var(--soft); border-radius: 14px; padding: 10px 14px; font-size: 24px; color: var(--muted); line-height: 1.2; }
  .tiles b { display: block; font-size: 42px; color: var(--navy); }
  .cap { font-size: 26px; color: var(--muted); margin-top: 10px; line-height: 1.3; }

  /* ---------------- methodology diagram: two rows, left to right then right to left, with a feedback arrow */
  .method { padding: 24px 30px 28px; }
  .ds { font-size: 27px; color: var(--muted); margin: 0 0 18px; }
  .snake { display: grid; grid-template-columns: minmax(0,1fr) 56px minmax(0,1fr) 56px minmax(0,1fr); grid-template-rows: auto 84px auto; }
  .stage { border-radius: 18px; overflow: hidden; background: var(--soft); border: 3px solid #DCE3EE; display: flex; flex-direction: column; }
  .stage .h { color: #fff; padding: 12px 18px; }
  .stage .h .k { display: block; font-size: 23px; font-weight: 700; opacity: .9; letter-spacing: 1px; }
  .stage .h b { font-size: 33px; line-height: 1.12; }
  .stage .t { padding: 12px 18px 14px; font-size: 26px; line-height: 1.3; }
  .s1 .h { background: #1F4E9C; } .s2 .h { background: #2563A8; } .s3 .h { background: var(--green); }
  .s4 .h { background: var(--purple); } .s5 .h { background: #B4570F; } .s6 .h { background: var(--teal); }
  .ar, .al, .ad, .au { display: grid; place-items: center; }
  .ar::after { content: ''; border-top: 24px solid transparent; border-bottom: 24px solid transparent; border-left: 34px solid #8A93A3; }
  .al::after { content: ''; border-top: 24px solid transparent; border-bottom: 24px solid transparent; border-right: 34px solid #8A93A3; }
  .ad::after { content: ''; border-left: 24px solid transparent; border-right: 24px solid transparent; border-top: 34px solid #8A93A3; }
  .au { position: relative; }
  .au::before { content: ''; position: absolute; top: 34px; bottom: 0; left: 50%; border-left: 6px dashed #8A93A3; }
  .au::after { content: ''; position: absolute; top: 0; border-left: 22px solid transparent; border-right: 22px solid transparent;
               border-bottom: 32px solid #8A93A3; }
  .au span { position: absolute; left: calc(50% + 24px); top: 26px; z-index: 1; font-size: 25px; font-weight: 700; color: var(--muted);
             white-space: nowrap; }
  .phases { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
  .phases div { border-radius: 10px; padding: 4px 10px; font-size: 23px; background: #fff; border: 2px solid #DCE3EE; }
  .phases b { color: var(--green); }

  /* ---------------- TRACE flow */
  .flow { display: grid; grid-template-columns: 1fr 50px 1fr 50px 1fr 50px 1.05fr; align-items: stretch; }
  .fbox { border-radius: 16px; padding: 16px 16px; text-align: center; font-size: 26px; line-height: 1.28; border: 4px solid; background: #fff; }
  .fbox b { display: block; font-size: 30px; margin-bottom: 4px; }
  .f1 { border-color: var(--navy); } .f2 { border-color: var(--orange); } .f3 { border-color: var(--navy); }
  .ra { display: grid; place-items: center; } .ra::after { content: ''; border-top: 22px solid transparent; border-bottom: 22px solid transparent;
        border-left: 32px solid #8A93A3; }
  .verd { display: flex; flex-direction: column; gap: 10px; justify-content: center; }
  .verd div { border-radius: 12px; padding: 8px 12px; font-size: 25px; line-height: 1.22; border: 4px solid; background: #fff; }
  .v1 { border-color: var(--green) !important; } .v1 b { color: var(--green); }
  .v2 { border-color: var(--red) !important; } .v2 b { color: var(--red); }
  .v3 { border-color: #8A93A3 !important; } .v3 b { color: var(--muted); }
  code { font-family: 'DejaVu Sans Mono', monospace; font-size: 24px; background: var(--soft); border-radius: 8px; padding: 2px 8px; }
  .key { margin-top: 22px; background: var(--navy); color: #fff; border-radius: 16px; padding: 18px 24px; font-size: 34px; font-weight: 700;
         text-align: center; }

  /* ---------------- results */
  .heroes { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .hero { background: var(--soft); border-radius: 18px; padding: 14px 20px; }
  .hero .big { font-size: 58px; font-weight: 800; color: var(--navy); line-height: 1; white-space: nowrap; }
  .hero .big small { font-size: 40px; color: var(--muted); }
  .hero p { font-size: 25px; margin-top: 8px; line-height: 1.28; }
  svg .lg { font-size: 30px; fill: ${INK}; } svg .ax { font-size: 26px; fill: ${MUTED}; }
  svg .nm { font-size: 31px; fill: ${INK}; } svg .nm.b { font-weight: 800; } svg .vl { font-size: 29px; font-weight: 700; fill: ${INK}; }
  .note { font-size: 26px; color: var(--muted); line-height: 1.32; margin-top: 8px; }
  .honest { border: 4px dashed var(--orange); border-radius: 16px; padding: 14px 22px; background: #FFF6EE; margin-top: 16px;
            font-size: 28px; line-height: 1.3; }
  .concl { font-size: 31px; font-weight: 700; color: var(--navy); line-height: 1.3; }
  .ack { font-size: 25px; line-height: 1.32; color: var(--muted); margin-top: 12px; }
</style></head><body>
<header>
  <div>${logo}</div>
  <div class="title">
    <h1>IntelliERP</h1>
    <p class="sub">Evidence-Grounded Hallucination Detection and Verification<br>for LLM-Based ERP Decision Support</p>
    <p class="who"><b>${NAME}</b> · Supervisor: <b>${META.supervisor}</b> · Home supervisor: <b>${META.homeSupervisor}</b></p>
  </div>
  <div class="right">
    <div class="fac">Faculty of Data Science and<br>Information Technology (FDSIT)<small>Final Year Project · ${META.session}</small>
      <small>Project ID ${META.projectId}</small></div>
    ${qr ? `<div class="repo">${qr}<span>Code on GitHub</span></div>` : ''}
  </div>
</header>
<main>
  <!-- ======================= LEFT ======================= -->
  <div class="col">
    <section><h2>Problem Statement</h2><div class="body">
      <p class="lead">AI assistants (LLMs) inside ERP systems answer questions about stock, demand and suppliers, but they can
      <b>state false facts with confidence</b>:</p>
      <ul class="clean">
        <li>a wrong stock figure: <i>“P082 has 120 units”</i> (the system has 0)</li>
        <li>an invented rule: <i>“rising demand means +20%”</i> (the rule is 15%)</li>
        <li>a false permission: <i>“I can approve this order”</i></li>
      </ul>
      <p>A wrong statement can lead to a <b>wrong purchase order</b>.</p>
    </div></section>

    <section><h2>Objectives</h2><div class="body obj">
      <div class="n">1</div><p><b>Prevent</b> false statements with an ERP assistant grounded in the company's data and rules.</p>
      <div class="n">2</div><p><b>Detect</b> the rest with <b>TRACE</b>, which checks every statement with the system's own code.</p>
      <div class="n">3</div><p><b>Measure</b> it honestly: frozen tests, strong baselines, real errors.</p>
    </div></section>

    <section class="grow"><h2>Proposed Solution</h2><div class="body def">
      <div class="p"><h3>1 · Prevent: grounding</h3><p>Rules decide risks; the AI reads data only through <b>15 permission-checked
      tools</b> and gets company rules from a <b>knowledge base of 41 passages</b>.</p></div>
      <div class="d"><h3>2 · Detect: TRACE</h3><p>Every statement becomes a typed assertion, checked by code
      <b>before the user sees it</b>.</p></div>
      <div class="a"><h3>3 · Human control</h3><p>The AI can only <b>draft</b> a purchase order; a different person must approve it.</p></div>
      <p class="cap">ERP for sales, inventory and procurement on Wide World Importers data (227 products, 72,696 sales lines),
      built with React, FastAPI, PostgreSQL and Gemini/Gemma; 272 automated tests pass.</p>
    </div></section>

  </div>

  <!-- ======================= CENTRE ======================= -->
  <div class="col">
    <section><h2>Research Methodology <small>design science, iterative development</small></h2>
    <div class="method">
      <p class="ds">Build an artefact for a real problem, evaluate it rigorously, and let what the evaluation teaches shape
      the next increment.</p>
      <div class="snake">
        <div class="stage s1"><div class="h"><span class="k">STAGE 1</span><b>Problem &amp; literature</b></div>
          <div class="t">61 papers reviewed. Gap: ERP assistants are checked for what they <i>do</i>, rarely for what they <i>say</i>.</div></div>
        <div class="ar"></div>
        <div class="stage s2"><div class="h"><span class="k">STAGE 2</span><b>Requirements</b></div>
          <div class="t">11 functional and 8 non-functional requirements, e.g. <i>truth is decided by code, never by a model</i>.</div></div>
        <div class="ar"></div>
        <div class="stage s3"><div class="h"><span class="k">STAGE 3</span><b>Build in 9 phases</b></div>
          <div class="t">Each phase ends with working, tested software.
            <div class="phases"><div><b>1–3</b> ERP core, PostgreSQL, analytics</div><div><b>4–7</b> AI tools, knowledge base, AI drafts</div>
            <div><b>8–9</b> evaluation, TRACE</div></div></div></div>

        <div class="au"><span>lessons learnt feed the next increment</span></div>
        <div></div><div></div><div></div>
        <div class="ad"></div>

        <div class="stage s6"><div class="h"><span class="k">STAGE 6</span><b>Results &amp; knowledge</b></div>
          <div class="t">What works, what does not, and why: in an IEEE journal article, a conference paper and this report.</div></div>
        <div class="al"></div>
        <div class="stage s5"><div class="h"><span class="k">STAGE 5</span><b>Evaluate</b></div>
          <div class="t">Against a pattern checker, 2 LLM judges and MiniCheck; 86 questions × 3 runs; 300 real sentences;
          Wilson intervals, McNemar, Holm.</div></div>
        <div class="al"></div>
        <div class="stage s4"><div class="h"><span class="k">STAGE 4</span><b>Freeze, then test</b></div>
          <div class="t">TRACE frozen by file hash <b>before</b> the test existed: 102 planted errors and 103 correct
          paraphrases by 2 AI writers.</div></div>
      </div>
    </div></section>

    <section class="grow"><h2>How TRACE Works</h2><div class="body">
      <div class="flow">
        <div class="fbox f1"><b>1 · Draft answer</b>“P082 has 120 units in stock”</div>
        <div class="ra"></div>
        <div class="fbox f2"><b>2 · AI extracts</b>a typed assertion<br><code>P082 · stock_on_hand = 120</code></div>
        <div class="ra"></div>
        <div class="fbox f3"><b>3 · Code verifies</b>reads the true value from the system: <code>0</code></div>
        <div class="ra"></div>
        <div class="verd">
          <div class="v1"><b>✓ Supported</b> → shown</div>
          <div class="v2"><b>✗ Contradicted</b> → corrected once, then a warning</div>
          <div class="v3"><b>? Unverifiable</b> → outside the language</div>
        </div>
      </div>
      <div class="key">The AI only extracts. The system's own code decides what is true.</div>
    </div></section>

  </div>

  <!-- ======================= RIGHT ======================= -->
  <div class="col">
    <section><h2>Key Results</h2><div class="body heroes">
      <div class="hero"><div class="big">25.9% <small>→</small> 2.4%</div><p>false statements in the AI's own answers,
      <b>without → with</b> grounding</p></div>
      <div class="hero"><div class="big">8–9 <small>→</small> 32<small>/32</small></div><p>paired questions answered
      correctly, without → with grounding (p &lt; 0.0001)</p></div>
      <div class="hero"><div class="big">69% <small>/</small> 4%</div><p>unseen errors detected by TRACE / false alarms on
      correct text</p></div>
      <div class="hero"><div class="big">0</div><p>errors caused by a verification function: <b>every failure is explainable</b></p></div>
    </div></section>

    <section><h2>TRACE vs Other Checkers <small>held-out test</small></h2><div class="body">
      ${heldoutChart()}
      <div class="honest"><b>Honest limit:</b> on the AI's own mistakes TRACE found only <b>4 of 19</b>; most were wrong
      definitions its language cannot express yet.</div>
    </div></section>

    <section class="grow"><h2>Conclusion</h2><div class="body">
      <p class="concl">Facts in an AI answer should be decided by the system that owns them, not by the model.</p>
      <p class="note" style="font-size:27px">Grounding prevented most errors; TRACE made the rest visible and explainable.
      Next: a user study, a wider language for definitions, warnings instead of automatic correction.</p>
      <p class="ack"><b>Acknowledgement:</b> ${META.supervisor} (INTI International University); ${META.homeSupervisor} and
      ${META.homeHod}, Head of CSE, G H Raisoni College of Engineering, Nagpur; research internship under the mobility programme.</p>
    </div></section>
  </div>
</main>
</body></html>`;
