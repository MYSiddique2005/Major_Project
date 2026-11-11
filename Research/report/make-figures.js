// Writes the report's diagrams and charts as HTML pages in figures/; render.js turns them into PNGs.
// Every number in a chart comes from a results file in LLM/evaluation/results (see the comment above each chart).
//   node make-figures.js && node render.js
const fs = require('fs');
const path = require('path');
const DIR = path.join(__dirname, 'figures');
fs.mkdirSync(DIR, { recursive: true });

const CSS = `body{margin:0;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#111}
#fig{display:inline-block;padding:18px;background:#fff}
.box{border:1.6px solid #1f3b73;border-radius:6px;padding:8px 10px;background:#f3f6fc;font-size:13px;text-align:center}
.title{font-weight:bold;font-size:14px;margin-bottom:4px}
.small{font-size:11.5px;color:#333}`;

function page(name, body, script = '') {
  fs.writeFileSync(path.join(DIR, name + '.html'), `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style>
<script src="../node_modules/mermaid/dist/mermaid.min.js"></script>
<script src="../node_modules/chart.js/dist/chart.umd.js"></script></head>
<body><div id="fig">${body}</div><script>${script}</script></body></html>`);
}

function mermaidPage(name, def, width = 1100) {
  page(name, `<div style="width:${width}px"><pre class="mermaid">${def}</pre></div>`,
    `window.__ready=false; mermaid.initialize({startOnLoad:false, theme:'neutral', fontFamily:'Arial', flowchart:{htmlLabels:true}});
     mermaid.run().then(()=>{window.__ready=true});`);
}

function chartPage(name, config, width = 900, height = 420) {
  page(name, `<div style="width:${width}px;height:${height}px"><canvas id="c"></canvas></div>`,
    `Chart.defaults.font.family='Arial'; Chart.defaults.font.size=14; Chart.defaults.color='#111';
     const cfg=${JSON.stringify(config)};
     cfg.options=Object.assign({animation:false,responsive:true,maintainAspectRatio:false},cfg.options||{});
     cfg.plugins=[{id:'labels',afterDatasetsDraw(chart){const {ctx}=chart;ctx.save();ctx.font='12px Arial';ctx.fillStyle='#111';
       chart.data.datasets.forEach((ds,i)=>{chart.getDatasetMeta(i).data.forEach((bar,j)=>{const v=ds.data[j];if(v==null)return;
       const horiz=chart.options.indexAxis==='y';const t=(ds.labelSuffix!==undefined?v+ds.labelSuffix:v+'%');
       if(horiz){ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText(t,bar.x+4,bar.y);}else{ctx.textAlign='center';ctx.textBaseline='bottom';ctx.fillText(t,bar.x,bar.y-3);}});});ctx.restore();}}];
     new Chart(document.getElementById('c'),cfg);`);
}

const BLUE = '#2f5597', ORANGE = '#c55a11', GREY = '#8c8c8c', GREEN = '#548235', LIGHT = '#9dc3e6';

// ---------------------------------------------------------------- Chapter 3: methodology and design
page('fig-methodology', `<div style="width:1000px">
<div style="display:flex;gap:14px;align-items:stretch">
 ${[['1. Problem and evidence', 'Literature review (61 papers)<br>Wide World Importers data analysis<br>Role and permission analysis'],
    ['2. Requirements and design', 'Functional and non-functional requirements<br>UML: context, use case, activity, class, sequence'],
    ['3. Iterative development', '8 phases, each built, tested and reviewed<br>ERP core → analytics → AI assistant →<br>grounding → verification → controlled actions'],
    ['4. Evaluation', '269 automated tests<br>86-question evaluation, 3 repeats<br>Held-out hallucination test<br>Natural errors, harm check']]
   .map(([t, s], i) => `<div class="box" style="flex:1"><div class="title">${t}</div><div class="small">${s}</div></div>${i < 3 ? '<div style="align-self:center;font-size:26px;color:#1f3b73">➜</div>' : ''}`).join('')}
</div>
<div style="margin-top:12px;text-align:center;font-size:12.5px;color:#333">Results of step 4 fed back into steps 2 and 3 (e.g. five failures in the first evaluation run led to five design changes; TRACE replaced the pattern verifier)</div>
</div>`);

page('fig-context', `<div style="width:1050px;position:relative">
<div style="display:grid;grid-template-columns:200px 60px 360px 60px 300px;align-items:center;row-gap:16px">
 <div>
  ${['Administrator', 'Inventory Manager', 'Procurement Manager', 'Employee (read-only)'].map(r => `<div class="box" style="margin:6px 0">👤 ${r}</div>`).join('')}
 </div>
 <div style="font-size:24px;text-align:center;color:#1f3b73">⇄</div>
 <div>
  <div class="box" style="background:#e8eef9"><div class="title">IntelliERP web application (React)</div>
   <div class="small">Dashboard · Sales · Inventory · Procurement · Suppliers · Analytics · Approvals · AI Insights · AI Assistant · Audit log</div></div>
  <div style="text-align:center;font-size:20px;color:#1f3b73">⇅ REST + JWT</div>
  <div class="box"><div class="title">FastAPI back end</div>
   <div class="small">Role-based access control · ERP services · Analytics engine (deterministic rules)<br>
   AI assistant: 15 permission-checked tools · Knowledge base (41 passages)<br>
   <b>Verification: figures + typed assertions (TRACE)</b> · Draft-only actions · Audit log</div></div>
  <div style="text-align:center;font-size:20px;color:#1f3b73">⇅ SQLAlchemy</div>
  <div class="box"><div class="title">PostgreSQL</div><div class="small">Wide World Importers: 227 products, 7 suppliers, 72,696 sales lines, 5,443 purchase-order lines</div></div>
 </div>
 <div style="font-size:24px;text-align:center;color:#1f3b73">⇄</div>
 <div>
  <div class="box" style="background:#fff4e5;border-color:#c55a11"><div class="title">LLM provider (external)</div>
  <div class="small">Google Gemini API (free tier)<br>gemini-3.5-flash-lite, Gemma 4 31B<br>receives the question, tool results and knowledge passages; never the database</div></div>
 </div>
</div></div>`);

// Use case diagram drawn as SVG
(() => {
  const actors = [['Administrator', 90], ['Inventory Manager', 230], ['Procurement Manager', 370], ['Employee', 510]];
  const cases = [
    ['Log in', 60, [0, 1, 2, 3]], ['View dashboard and ERP records', 110, [0, 1, 2, 3]], ['View analytics and risk', 160, [0, 1, 2]],
    ['Ask the AI assistant', 210, [0, 1, 2]], ['Review AI insights', 260, [0, 1, 2]], ['Create / submit purchase order', 310, [0, 2]],
    ['Draft order from AI recommendation', 360, [0, 2]], ['Approve or reject purchase order', 410, [0, 2]], ['View audit log', 460, [0]],
  ];
  const actor = (x, y, n) => `<g><circle cx="${x}" cy="${y - 28}" r="10" fill="none" stroke="#111"/><line x1="${x}" y1="${y - 18}" x2="${x}" y2="${y + 6}" stroke="#111"/>
    <line x1="${x - 14}" y1="${y - 10}" x2="${x + 14}" y2="${y - 10}" stroke="#111"/><line x1="${x}" y1="${y + 6}" x2="${x - 11}" y2="${y + 24}" stroke="#111"/>
    <line x1="${x}" y1="${y + 6}" x2="${x + 11}" y2="${y + 24}" stroke="#111"/><text x="${x}" y="${y + 42}" font-size="13" text-anchor="middle">${n}</text></g>`;
  let s = '';
  s += `<rect x="200" y="20" width="420" height="510" fill="none" stroke="#1f3b73" stroke-width="1.5"/><text x="410" y="40" text-anchor="middle" font-weight="bold" font-size="14">IntelliERP</text>`;
  cases.forEach(([n, y, who]) => {
    s += `<ellipse cx="410" cy="${y + 20}" rx="185" ry="19" fill="#f3f6fc" stroke="#1f3b73"/><text x="410" y="${y + 25}" text-anchor="middle" font-size="13">${n}</text>`;
    who.forEach(a => { s += `<line x1="110" y1="${actors[a][1]}" x2="225" y2="${y + 20}" stroke="#999" stroke-width="0.8"/>`; });
  });
  actors.forEach(([n, y]) => { s += actor(70, y, n); });
  s += actor(760, 220, 'LLM provider');
  [210, 260, 360].forEach(y => { s += `<line x1="595" y1="${y + 20}" x2="740" y2="210" stroke="#c55a11" stroke-dasharray="5,4" stroke-width="1"/>`; });
  s += `<ellipse cx="410" cy="510" rx="0" ry="0"/>`;
  s += `<text x="760" y="290" text-anchor="middle" font-size="11.5" fill="#555">«system», secondary</text>`;
  page('fig-usecase', `<svg width="860" height="560" font-family="Arial">${s}</svg>`);
})();

mermaidPage('fig-activity', `flowchart TD
  A([User asks a question]) --> B[Retrieve 4 knowledge passages<br/>BM25 over the 41-passage knowledge base]
  B --> C[Offer the model only the tools<br/>the user's role permits]
  C --> D{Model calls a tool?}
  D -- yes --> E[Check permission again,<br/>run the tool through the ERP services] --> D
  D -- "no (answer drafted, max 8 rounds)" --> F[Verify the draft answer:<br/>every figure traced to a source;<br/>every factual statement checked by TRACE]
  F --> G{Anything contradicted or untraced?}
  G -- "yes, first time" --> H[Send back once with the<br/>contradicted statements and the data] --> F
  G -- no --> I[Show answer with sources,<br/>passages used and check results]
  G -- "yes, after correction" --> J[Show answer with the remaining<br/>statements flagged as warnings]
  I --> K([Audit log entry])
  J --> K`, 900);

mermaidPage('fig-class', `classDiagram
  direction LR
  class AIService{
    +chat(message, user, history) ChatResponse
  }
  class Toolbox{
    +tools_for(user) list~Tool~
    +run(call, user) ToolResult
  }
  class KnowledgeBase{
    +search(query, k) list~Match~
  }
  class AnalyticsService{
    +stock_risk(product)
    +forecast(product)
    +supplier_performance()
    +what_if(scenario)
  }
  class RecommendationChecker{
    +check(recommendation) RecommendationChecks
    +product_facts(id)
    +supplier_facts(id)
  }
  class TraceVerifier{
    +check(text, subject) TraceResult
    +rule_verdicts(text)
    +model_verdicts(assertions)
  }
  class Assertion{
    family: state|derived|policy
    attribute
    subject
    comparator
    value
  }
  class Verdict{
    status: supported|contradicted|unverifiable
    quote
    reason
  }
  class AIActionService{
    +draft_from_recommendation()
  }
  class ProcurementService{
    +create_draft()
    +submit()
  }
  class ApprovalService{
    +approve()
    +reject()
  }
  class InsightService{
    +run_scan(trigger)
    +review(id, status)
  }
  class AuditService{
    +record(event)
  }
  AIService --> Toolbox : uses
  AIService --> KnowledgeBase : grounds with
  AIService --> TraceVerifier : verifies answer
  AIService --> RecommendationChecker : checks figures
  Toolbox --> AnalyticsService : reads
  Toolbox --> AIActionService : draft only
  AIActionService --> ProcurementService
  ProcurementService --> ApprovalService : second person decides
  TraceVerifier --> Assertion : extracts
  TraceVerifier --> Verdict : returns
  TraceVerifier --> RecommendationChecker : facts
  InsightService --> AIService
  AIService --> AuditService
  ProcurementService --> AuditService`, 1250);

mermaidPage('fig-sequence', `sequenceDiagram
  autonumber
  actor U as User
  participant UI as React UI
  participant API as FastAPI /ai/chat
  participant AI as AIService
  participant LLM as Gemini (LLM)
  participant T as Toolbox + Analytics
  participant V as TRACE verifier
  U->>UI: types question
  UI->>API: POST /ai/chat (JWT)
  API->>AI: chat(message, user)
  AI->>AI: retrieve knowledge passages, select permitted tools
  AI->>LLM: question + passages + tool list
  LLM-->>AI: tool call get_product_overview(P082)
  AI->>T: run tool (permission checked again)
  T-->>AI: facts by module
  AI->>LLM: tool result
  LLM-->>AI: draft answer
  AI->>V: check(draft answer)
  V->>LLM: extract typed assertions (JSON)
  LLM-->>V: assertions
  V->>T: evaluate each assertion with the system's own code
  V-->>AI: verdicts (supported / contradicted / unverifiable)
  alt a statement is contradicted
    AI->>LLM: send back once with the contradictions and the data
    LLM-->>AI: corrected answer (checked again)
  end
  AI-->>API: answer, sources, passages, checks
  API-->>UI: JSON response (and audit log entry)
  UI-->>U: answer with verification results`, 1150);

// ---------------------------------------------------------------- Chapter 5: development
mermaidPage('fig-architecture', `flowchart TB
  subgraph FE[Frontend: React 19 + TypeScript + Vite + Tailwind]
    P[Pages: Dashboard, Sales, Inventory, Procurement,<br/>Analytics, Approvals, AI Insights, AI Assistant, Audit]
    S[Services: Axios clients, AuthContext, JWT storage]
  end
  subgraph BE[Backend: Python + FastAPI]
    R[API routers /api/v1: one per module]
    SEC[Security: JWT, bcrypt, role to permission map]
    SV[Services: business logic and workflows]
    AN[Analytics: demand, forecast, stock risk,<br/>supplier performance, what-if]
    LL[LLM layer: providers, 15 tools, knowledge base,<br/>recommendation checks, TRACE verifier]
    RP[Repositories: PostgreSQL / in-memory]
  end
  DB[(PostgreSQL 11 tables)]
  EXT[[Gemini API]]
  P --> S --> R
  R --> SEC
  R --> SV --> RP --> DB
  SV --> AN
  SV --> LL --> EXT
  LL --> AN`, 1000);

mermaidPage('fig-trace', `flowchart LR
  A[Assistant's draft answer] --> B[LLM extractor<br/>prompt trace-extract-3<br/>JSON assertions]
  A --> C[Rule extractor<br/>12 claim patterns]
  B --> D{Schema validation<br/>64 attributes, 3 families}
  D -- invalid --> X[dropped and counted]
  D -- valid --> E[Grounding and type checks<br/>subject named in text,<br/>ambiguous terms, units, dates]
  C --> F
  E --> F[Deterministic verifier:<br/>evaluates each assertion with<br/>the system's own tested code]
  F --> G[supported]
  F --> H[contradicted]
  F --> I[unverifiable]
  H --> J[sent back once for correction,<br/>then shown as a warning]`, 1250);

mermaidPage('fig-po-states', `stateDiagram-v2
  direction LR
  [*] --> Draft: created by a user or drafted by the AI
  Draft --> Draft: edited (procurement:create)
  Draft --> PendingApproval: submitted
  Draft --> [*]: deleted
  PendingApproval --> Approved: approved by a different user (procurement:approve)
  PendingApproval --> Rejected: rejected
  Approved --> [*]
  Rejected --> [*]`, 1100);

mermaidPage('fig-erd', `erDiagram
  SUPPLIERS ||--o{ SUPPLIER_PRODUCTS : supplies
  PRODUCTS ||--o{ SUPPLIER_PRODUCTS : "supplied by"
  PRODUCTS ||--o{ INVENTORY : "stocked as"
  PRODUCTS ||--o{ SALES_ORDERS : "sold in"
  PRODUCTS ||--o{ PURCHASE_ORDERS : "ordered in"
  SUPPLIERS ||--o{ PURCHASE_ORDERS : receives
  PURCHASE_ORDERS ||--o| APPROVALS : "decided by"
  USERS ||--o{ APPROVALS : decides
  USERS ||--o{ AUDIT_LOGS : performs
  AI_SCANS ||--o{ AI_INSIGHTS : produces
  AI_INSIGHTS |o--o{ PURCHASE_ORDERS : "drafted from"
  PRODUCTS { string id PK
    string name
    float price
    float unit_cost }
  INVENTORY { string id PK
    string product_id FK
    string warehouse
    int current_stock
    int safety_stock
    int reorder_level }
  PURCHASE_ORDERS { string id PK
    string product_id FK
    string supplier_id FK
    int quantity
    string status
    string origin
    json ai_recommendation }
  SALES_ORDERS { string id PK
    string product_id FK
    int quantity
    date order_date
    string status }`, 1100);

// ---------------------------------------------------------------- Chapter 6: results (charts)
// LLM/evaluation/results/fixed-summary.md, gemma4-summary.md, extended-1
chartPage('chart-runs', { type: 'bar', data: { labels: ['E1 (before fixes)', 'F1', 'F2', 'F3', 'G (Gemma 4 31B)'],
  datasets: [{ label: 'Questions passed with grounding (of 86)', data: [81, 84, 86, 86, 86], backgroundColor: [GREY, BLUE, BLUE, BLUE, GREEN], labelSuffix: '' }] },
  options: { plugins: { legend: { display: false }, title: { display: true, text: 'Questions passed with grounding (of 86)' } }, scales: { y: { min: 0, max: 90 } } } });

chartPage('chart-grounding', { type: 'bar', data: { labels: ['E1', 'F1', 'F2', 'F3', 'G (Gemma)'],
  datasets: [{ label: 'With knowledge base', data: [32, 32, 32, 32, 32], backgroundColor: BLUE, labelSuffix: '' },
             { label: 'Without knowledge base', data: [9, 8, 9, 9, 6], backgroundColor: ORANGE, labelSuffix: '' }] },
  options: { plugins: { title: { display: true, text: '32 paired questions answered correctly' } }, scales: { y: { min: 0, max: 36 } } } });

// LLM/evaluation/results/claims/summary.md
chartPage('chart-verifier-versions', { type: 'bar', data: { labels: ['v1 (mutation estimate)', 'v2 (n=25)', 'v3 set 1 (n=31)', 'v3 set 2 (n=31)', 'v3 both (n=62)'],
  datasets: [{ data: [48, 60, 81, 74, 77], backgroundColor: [GREY, LIGHT, BLUE, BLUE, BLUE] }] },
  options: { indexAxis: 'y', plugins: { legend: { display: false }, title: { display: true, text: 'Pattern verifier: in-scope injected errors detected (%)' } }, scales: { x: { min: 0, max: 100 } } } }, 900, 360);

// LLM/evaluation/results/trace/dev-report.md (final prompt)
chartPage('chart-dev', { type: 'bar', data: { labels: ['Patterns (v3)', 'TRACE-rule', 'TRACE-model', 'TRACE-hybrid'],
  datasets: [{ label: 'Errors detected', data: [38, 43, 61, 69], backgroundColor: BLUE },
             { label: 'False alarms on paraphrases', data: [1, 1, 5, 7], backgroundColor: ORANGE }] },
  options: { plugins: { title: { display: true, text: 'Development sets: 183 errors, 182 paraphrases (%)' } }, scales: { y: { min: 0, max: 100 } } } });

// LLM/evaluation/results/trace/heldout-report.md
chartPage('chart-heldout', { type: 'bar', data: { labels: ['Patterns (v3)', 'TRACE-rule', 'TRACE-model', 'TRACE-hybrid', 'LLM judge (Gemini)', 'LLM judge (Gemma)', 'MiniCheck'],
  datasets: [{ label: 'Errors detected (of 102)', data: [15, 20, 65, 69, 78, 75, 37], backgroundColor: BLUE },
             { label: 'False alarms (of 103 paraphrases)', data: [2, 2, 3, 4, 17, 7, 21], backgroundColor: ORANGE }] },
  options: { plugins: { title: { display: true, text: 'Held-out test, written after TRACE was frozen (%)' } }, scales: { y: { min: 0, max: 100 } } } }, 950, 430);

chartPage('chart-errortype', { type: 'bar', data: { labels: ['Derived (15)', 'Existence (18)', 'Figure (26)', 'Permission (9)', 'Qualitative (20)', 'Rule (14)'],
  datasets: [{ label: 'TRACE-hybrid', data: [87, 50, 81, 22, 70, 79], backgroundColor: BLUE },
             { label: 'LLM judge (Gemini)', data: [73, 89, 77, 33, 85, 93], backgroundColor: GREY },
             { label: 'LLM judge (Gemma)', data: [67, 72, 77, 44, 75, 100], backgroundColor: GREEN }] },
  options: { plugins: { title: { display: true, text: 'Held-out errors detected by error type (%)' } }, scales: { y: { min: 0, max: 100 } } } }, 950, 430);

// LLM/evaluation/results/trace/natural/report.md
chartPage('chart-natural', { type: 'bar', data: { labels: ['Patterns (v3)', 'TRACE-hybrid', 'Gemini judge', 'Gemma judge (203 answers)', 'MiniCheck'],
  datasets: [{ label: 'Recall on the false sentences of the sample', data: [11, 21, 53, 79, 74], backgroundColor: BLUE },
             { label: 'Precision of flags', data: [100, 15, 24, 17, 8], backgroundColor: ORANGE }] },
  options: { plugins: { title: { display: true, text: "The assistant's own errors (%)" } }, scales: { y: { min: 0, max: 110 } } } }, 900, 420);

// LLM/evaluation/results/fpq-report.md (both models complete)
chartPage('chart-fpq', { type: 'bar', data: { labels: ['Verifier off', 'Patterns', 'TRACE'],
  datasets: [{ label: 'gemini-3.5-flash-lite (44 questions)', data: [89, 84, 93], backgroundColor: BLUE },
             { label: 'gemma-4-31b-it (44 questions)', data: [93, 93, 93], backgroundColor: GREEN }] },
  options: { plugins: { title: { display: true, text: 'False-premise questions: answers that rebut the premise (%)' } }, scales: { y: { min: 0, max: 100 } } } }, 900, 400);

// LLM/evaluation/results/trace/harm-report.md
chartPage('chart-harm', { type: 'bar', data: { labels: ['fixed-1 (patterns)', 'fixed-2 (patterns)', 'fixed-3 (patterns)', 'trace-1 (TRACE)'],
  datasets: [{ label: 'Questions passed (of 86)', data: [84, 86, 86, 84], backgroundColor: [BLUE, BLUE, BLUE, ORANGE], labelSuffix: '' }] },
  options: { plugins: { legend: { display: false }, title: { display: true, text: 'Harm check: the 86 evaluation questions with each verifier' } }, scales: { y: { min: 0, max: 90 } } } }, 900, 380);

// ---------------------------------------------------------------- Appendix: Gantt chart
(() => {
  // weeks of a 16-week semester; the repository's commit dates fix weeks 6-14 (5 Oct to 11 Nov 2026)
  const rows = [
    ['Topic, supervisor meeting, scope', 1, 2, 'plan'], ['Literature review (first 30 papers)', 2, 5, 'plan'],
    ['Requirements and system design', 3, 5, 'plan'], ['Phases 1-3: ERP core, PostgreSQL, analytics', 3, 6, 'plan'],
    ['Phases 4-7: AI assistant, grounding, insights, AI drafts', 6, 6, 'git'], ['Phase 8: evaluation, 86 questions x 3 runs', 6, 7, 'git'],
    ['Claim verifier and held-out tests; research paper', 7, 7, 'git'], ['Second model (Gemma); 31 further papers', 8, 9, 'git'],
    ['TRACE design, development sets, freeze', 9, 10, 'git'], ['Held-out test, baselines, natural errors', 10, 13, 'git'],
    ['Harm check, repeatability, journal paper', 13, 14, 'git'], ['Final report, viva preparation', 14, 16, 'plan'],
  ];
  const cells = w => Array.from({ length: 16 }, (_, i) => i + 1).map(i => {
    const on = i >= w[1] && i <= w[2];
    return `<td style="border:1px solid #bbb;width:32px;height:22px;background:${on ? (w[3] === 'git' ? '#2f5597' : '#9dc3e6') : '#fff'}"></td>`;
  }).join('');
  page('fig-gantt', `<table style="border-collapse:collapse;font-size:12.5px">
   <tr><th style="border:1px solid #bbb;padding:4px 8px;text-align:left;background:#1f3b73;color:#fff">Task</th>${Array.from({ length: 16 }, (_, i) => `<th style="border:1px solid #bbb;background:#1f3b73;color:#fff;font-weight:normal">W${i + 1}</th>`).join('')}</tr>
   ${rows.map(r => `<tr><td style="border:1px solid #bbb;padding:3px 8px;white-space:nowrap">${r[0]}</td>${cells(r)}</tr>`).join('')}
  </table>
  <div style="margin-top:8px;font-size:12px"><span style="display:inline-block;width:14px;height:12px;background:#2f5597"></span> dated by the repository's commit history (week 6 = 5 Oct 2026)
  &nbsp;&nbsp;<span style="display:inline-block;width:14px;height:12px;background:#9dc3e6"></span> planned (before the repository, or still to come)</div>`);
})();

console.log('figures written to', DIR);
