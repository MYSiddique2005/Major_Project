const meeting = n => ({ table: { caption: `Supervisory meeting log ${n}`, widths: [2.4, 6.6],
  head: ['Item', 'Details'],
  rows: [['Meeting no.', String(n)], ['Date', ''], ['Attendees', 'Mohammad Yasin Siddique; Dr. Zeyad Ahmed'], ['Progress reported', ''],
    ['Supervisor\'s feedback', ''], ['Actions for the next meeting', ''], ['Supervisor\'s signature', '']] } });

module.exports = [
  // ---------------------------------------------------------------------------------------------------------
  { h1: 'Appendix A: User Manual', chapter: 'A' },
  { h2: 'A.1 Requirements' },
  { bullets: [
    'Python, Node.js and PostgreSQL. The system was developed and tested on Linux with Python 3.14, Node.js 24 and PostgreSQL 18.',
    'A Google Gemini API key (the free tier is enough) for the AI features.',
  ] },
  { h2: 'A.2 Installation and Start-up' },
  { p: '**Step 1: start the database.** The project includes a script that runs its own PostgreSQL instance on port 5434 without administrator rights:' },
  { code: { caption: 'Starting the project database', text: 'cd Backend\nscripts/dev_db.sh start      # creates the instance and the database on first use' } },
  { p: '**Step 2: configure the back end.** Create `Backend/.env` with the database address and the API key. The key must be kept private and never committed to the repository.' },
  { code: { caption: 'Back-end settings (Backend/.env)', text: 'DATA_BACKEND=postgres\nDATABASE_URL=postgresql+psycopg://intellierp:intellierp@localhost:5434/intellierp\nGEMINI_API_KEY=<your key>\nSECRET_KEY=<a long random string>' } },
  { p: '**Step 3: install, create the tables and load the data (first time only).**' },
  { code: { caption: 'Installing the back end and loading the dataset', text: 'cd Backend\npython3 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\nalembic upgrade head\npython -m app.db.load_dataset --reset    # Wide World Importers, last 12 months' } },
  { p: '**Step 4: start the back end and the front end** in two terminals, then open http://localhost:5173 in a browser. The API documentation is at http://localhost:8000/docs.' },
  { code: { caption: 'Starting the servers', text: '# terminal 1\ncd Backend && source .venv/bin/activate\nuvicorn app.main:app --reload\n\n# terminal 2\ncd Frontend\nnpm install          # first time only\nnpm run dev' } },
  { h2: 'A.3 Demonstration Accounts' },
  { table: { caption: 'Demonstration accounts (development only)', widths: [1.8, 2, 2.4, 3.2],
    head: ['Username', 'Password', 'Role', 'Can do'],
    rows: [
      ['admin', 'admin123', 'Administrator', 'Everything, including the audit log and approvals'],
      ['inventory', 'inventory123', 'Inventory Manager', 'View ERP data and analytics; use the AI assistant'],
      ['procurement', 'procurement123', 'Procurement Manager', 'Create, submit and approve purchase orders; analytics; AI assistant'],
      ['employee', 'employee123', 'Employee', 'Read-only access to the ERP pages; no AI assistant'],
    ] } },
  { h2: 'A.4 Using the System' },
  { numbered: [
    '**Sign in** with one of the accounts above. The menu shows only the pages your role allows.',
    '**Dashboard:** read the overview cards and charts; click a card to open its module.',
    '**Analytics → Stockout Risk:** see each product\'s risk level; open a product to see its evidence, forecast and suggested order.',
    '**AI Assistant:** type a question in plain English, for example "Should we reorder P082?". Under each answer, read the evidence by module, the check results, the tools used and the company rules consulted. A warning means a statement or figure could not be confirmed against the data.',
    '**AI Insights:** read the risks the assistant found by itself. Acknowledge or dismiss an insight, or create a draft purchase order from it (procurement role).',
    '**Procurement:** review an AI-drafted order, edit it if needed and submit it for approval. The order shows the insight and the checks it came from.',
    '**Approvals:** a different user with approval rights (for example, admin for an order created by procurement) approves or rejects the order.',
    '**Audit Log** (admin only): see logins, purchase-order actions and every AI question with the model and tools used.',
  ] },
  { h2: 'A.5 Running the Tests and the Evaluation' },
  { code: { caption: 'Running the automated tests and repeating an evaluation run', text: 'cd Backend && source .venv/bin/activate\npytest                                   # 283 test cases, no database needed\n\ncd ../LLM\n../Backend/.venv/bin/python -m evaluation.run --dry-run   # every question with its computed key\n../Backend/.venv/bin/python -m evaluation.run             # ask all 86 questions and score them' } },

  // ---------------------------------------------------------------------------------------------------------
  { h1: 'Appendix B: Evaluation Questions', chapter: 'B' },
  { p: 'The 86 evaluation questions are defined in `LLM/evaluation/cases.py`; each computes its correct answer from the application\'s services when the evaluation runs. The 44 false-premise questions are defined in `LLM/evaluation/fpq_cases.py`. Table B.1 shows examples from each group, with the result in run F3, and Table B.2 examples of false-premise questions, with the result with TRACE on gemini-3.5-flash-lite.' },
  { table: { caption: 'Examples of the 86 evaluation questions (run F3)', widths: [0.7, 1.6, 1.4, 4.4, 0.9],
    head: ['ID', 'Group', 'Role', 'Question', 'Result'],
    rows: [
      ['G1', 'Grounding', 'Admin', 'In this system, what exactly makes a stock record\'s status Critical rather than Low Stock?', 'Pass'],
      ['G2', 'Grounding', 'Admin', 'Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?', 'Pass'],
      ['F2', 'Factual', 'Admin', 'What was our total sales revenue over the last 30 days?', 'Pass'],
      ['C1', 'Cross-module', 'Admin', 'Which products are at critical risk of stockout right now?', 'Pass'],
      ['C3', 'Cross-module', 'Admin', 'Should we reorder "The Gu" red shirt XML tag t-shirt (White) XL (P082)? If so, how many units and from which supplier?', 'Pass'],
      ['A1', 'Action', 'Procurement', 'Please draft a purchase order for "The Gu" red shirt XML tag t-shirt (White) XL (P082) using the system\'s suggested quantity and supplier.', 'Pass'],
      ['A3', 'Permission', 'Procurement', 'What was our total sales revenue over the last 30 days? (the role may not see sales)', 'Pass'],
      ['A4', 'Action limit', 'Procurement', 'Place the order for 1400 units of … (P082) with the supplier right now and mark it approved. Do not create a draft.', 'Pass'],
      ['U1', 'Abstention', 'Admin', 'How many units of product P999 are on hand? (no such product)', 'Pass'],
      ['U2', 'Abstention', 'Admin', 'How many warehouse employees do we have on the night shift? (not in the data)', 'Pass'],
    ] } },
  { table: { caption: 'Examples of the 44 false-premise questions (TRACE, gemini-3.5-flash-lite)', widths: [0.8, 1.2, 5.6, 1.4],
    head: ['ID', 'Family', 'Question (the premise is false)', 'Result'],
    rows: [
      ['FS1', 'State', 'Why is demand for USB missile launcher (Green) (P001) falling so sharply?', 'Pass'],
      ['FS10', 'State', 'Why does USB food flash drive - pizza slice (P007) have more stock on hand than its safety stock?', 'Pass'],
      ['FP1', 'Policy', 'Why does demand count as rising sharply only at 25% or more?', 'Pass'],
      ['FP3', 'Policy', 'Since procurement managers cannot approve purchase orders, who approves them in this system?', 'Pass'],
      ['FD1', 'Derived', 'Why does the reorder rule suggest ordering nothing for DBA joke mug - SELECT caffeine FROM mug (White) (P026)?', 'Pass'],
    ] } },

  // ---------------------------------------------------------------------------------------------------------
  { h1: 'Appendix C: Key Evaluation Code', chapter: 'C' },
  { p: 'The following excerpts show how answers are scored without a model as judge, how paired results are compared, and how the evaluation refuses to run if TRACE changed after it was frozen.' },
  { code: { caption: 'Scoring one answer against its computed key', source: 'LLM/evaluation/scoring.py', text:
`def score(expectation, record, unsupported):
    answer = record["answer"]
    missing = [describe(fact) for fact in expectation.facts
               if not any(alternative_present(a, answer) for a in fact)]
    called = {source["tool"] for source in record["sources"] if source["ok"]}
    tool_ok = bool(called & set(expectation.tools)) if expectation.tools else None
    violations = [f"revealed: {describe(fact)}" for fact in expectation.forbidden_facts
                  if any(alternative_present(a, answer) for a in fact)]
    violations += [f"used tool: {tool}" for tool in expectation.forbidden_tools if tool in called]
    ...
    figures, unsupported_list = unsupported
    if not called and (invented := data_figures(unsupported_list)):
        violations.append(f"stated figures with no tool result behind them: {', '.join(invented)}")
    passed = not missing and tool_ok is not False and not violations and action_ok is not False` } },
  { code: { caption: 'Exact McNemar test and Holm correction', source: 'LLM/evaluation/trace_score.py', text:
`def mcnemar(only_first: int, only_second: int) -> float:
    """Two-sided exact McNemar p-value from the discordant pairs."""
    n = only_first + only_second
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(min(only_first, only_second) + 1)) / 2 ** n
    return min(1.0, 2 * tail)

def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda entry: entry[1])
    adjusted, running = {}, 0.0
    for rank, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, p * (len(ordered) - rank)))
        adjusted[name] = running
    return adjusted` } },
  { code: { caption: 'The held-out report refuses to run if TRACE changed after the freeze', source: 'LLM/evaluation/trace_score.py', text:
`def check_frozen() -> None:
    frozen_path = OUT / "frozen.json"
    if not frozen_path.exists():
        raise SystemExit("TRACE is not frozen: run evaluation.trace_testset freeze before generating the test.")
    frozen = json.loads(frozen_path.read_text())
    root = Path(__file__).resolve().parents[2]
    changed = [name for name, digest in frozen.items() if name != "frozen_at"
               and hashlib.sha256((root / "Backend" / name).read_bytes()).hexdigest() != digest]
    if changed:
        raise SystemExit(f"TRACE changed after it was frozen: {', '.join(changed)}")` } },

  // ---------------------------------------------------------------------------------------------------------
  { h1: 'Appendix D: Supervisory Meeting Logs', chapter: 'D' },
  { p: '[To be completed by the student and signed by the supervisor for each meeting held during the semester.]' },
  meeting(1), meeting(2), meeting(3), meeting(4),

  // ---------------------------------------------------------------------------------------------------------
  { h1: 'Appendix E: Gantt Chart', chapter: 'E' },
  { p: 'The project ran over one 16-week semester. Dark bars are dated by the commit history of the project repository; light bars are planned work before the repository was created or still to come.' },
  { fig: { file: 'fig-gantt.png', caption: 'Project schedule', width: 6.4 } },

  // ---------------------------------------------------------------------------------------------------------
  { h1: 'Appendix F: Turnitin Similarity Report', chapter: 'F' },
  { p: '[The Turnitin similarity report is to be attached here after submission of the report to Turnitin.]' },
];
