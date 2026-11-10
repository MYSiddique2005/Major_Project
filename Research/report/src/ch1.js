module.exports = [
  { h1: 'Chapter 1: Introduction' },
  { h2: '1.0 Overview' },
  { p: 'Enterprise resource planning (ERP) systems hold the data that managers need to run a business: what was sold, what is in stock, what has been ordered from which supplier and when it should arrive. The information is spread across modules, so answering a simple question such as "which products will run out before the next delivery?" means reading several screens and applying the company\'s own rules. Large language models (LLMs) promise to do this from a question in plain language, and research on AI in ERP is growing by 11.3% a year [@hurbean2026erp].' },
  { p: 'There is a catch. An LLM writes fluent, confident text whether or not the text is true. In an ERP system, a false statement is not a harmless mistake: a buyer who is told that a product\'s stock is above its reorder point does not reorder, and a manager who is told that procurement managers cannot approve orders escalates for no reason. This project builds **IntelliERP**, an ERP decision-support system with an LLM assistant, and studies one problem in depth: **how to stop the assistant from showing users false statements about the business, by using the system\'s own data and rules as evidence.**' },

  { h2: '1.1 Research Description' },
  { p: 'IntelliERP combines four layers that work together against false statements.' },
  { p: '**First, a complete ERP foundation.** The system has Sales, Inventory, Procurement, Supplier and Product modules, a dashboard, a purchase-order workflow with approvals, an audit log and role-based access control for four roles. It runs on PostgreSQL with data derived from Microsoft\'s Wide World Importers sample database: 227 products, 7 suppliers and 72,696 sales lines over twelve months.' },
  { p: '**Second, deterministic analytics.** Rule-based functions compute demand and its trend, days of cover, observed supplier lead times, a four-level stockout risk, reorder quantities, weekly forecasts, supplier performance and what-if projections. The analytics, not the AI, decide what is at risk.' },
  { p: '**Third, a grounded AI assistant.** The assistant answers through 15 tools that wrap the application\'s own services; it never writes SQL and may use only the tools the user\'s role allows. Before each question it is given the relevant passages from a 41-passage knowledge base of the company\'s schema, definitions, rules and workflows (retrieval-augmented generation, [@lewis2020rag]). It raises proactive insights about the risks the analytics found, and the only change it can make to the data is a draft purchase order that a second person must approve.' },
  { p: '**Fourth, run-time verification, the core contribution.** Every answer is checked before the user sees it. Every figure must be traceable to a tool result or knowledge passage, and every factual statement is checked by **TRACE** (Typed Run-time Assertion Checking for Enterprise assistants). TRACE uses an LLM only to turn each statement into a typed assertion, for example *stock_on_hand(P082) = 0*, and then decides whether the assertion is true with the system\'s own tested code. A contradicted answer is sent back to the model once for correction; anything still wrong is shown to the user as a warning.' },

  { h2: '1.2 Problem Statement' },
  { p: 'Current LLM-based ERP assistants leave three connected problems unsolved.' },
  { numbered: [
    '**Assistants make false statements about enterprise data and rules.** LLMs that write SQL over realistic enterprise schemas solve as few as 21% of tasks [@lei2025spider2], and a general model does not know a company\'s own definitions and thresholds [@sequeda2023kg]. Even when the figures are right, the explanation around them can be wrong: a wrong trend, a wrong risk level or an invented rule. Such errors are hard for a user to notice because the answer reads well.',
    '**Existing checks are weak, unexplainable or absent.** Agentic inventory systems claim explainability without checking their explanations [@quan2024invagent]. The newest ERP agents control what the model may *do* but not whether what it *says* is true; the closest system states that its run-time gate is "not a bound on how often a hallucinated or mis-calibrated decision is proposed" [@liu2026agenticerp]. Where outputs are checked, the checker is usually another LLM, which can be wrong itself, gives different verdicts when asked twice, and cannot explain which fact it relied on [@gu2024judge].',
    '**People act on what the assistant says.** Explanations make people accept AI advice whether it is right or wrong [@bansal2021whole], while signals that make checking cheap reduce over-reliance [@vasconcelos2023overreliance]. An ERP assistant that can also create orders turns a false statement into a wrong transaction unless the action path is controlled.',
  ] },

  { h2: '1.3 Research Questions' },
  { p: '**RQ1: Prevention by grounding.** How can an LLM assistant inside an ERP system be designed so that its answers are grounded in the system\'s own data and rules, and how much does grounding improve the correctness of its answers?' },
  { p: '**RQ2: Detection by verification.** How accurately can typed run-time verification (TRACE) detect false statements in the assistant\'s answers, compared with a pattern-based checker, an LLM judge and a trained fact-checker, both on model-written errors and on the assistant\'s own errors?' },
  { p: '**RQ3: Effect and cost.** Does verification with correction change what users finally see, can it cause harm, and what does it cost in time, tokens and repeatability?' },

  { h2: '1.4 Project Objectives' },
  { h3: '1.4.1 To address Research Question 1' },
  { numbered: [
    'To build a complete ERP system (sales, inventory, procurement, suppliers, approvals, audit) with role-based access control, on a realistic dataset.',
    'To design an AI assistant in which deterministic analytics decide what is at risk and the LLM explains through permission-checked tools, grounded in a knowledge base that is generated partly from the code so that it cannot drift from it.',
    'To measure the effect of grounding by asking the same questions with and without the knowledge base, repeated across runs and models.',
  ] },
  { h3: '1.4.2 To address Research Question 2' },
  { numbered: [
    'To design a typed assertion language for enterprise statements covering the database state, analytics results and company rules and permissions.',
    'To implement TRACE, in which an LLM only extracts assertions and deterministic code decides their truth, so that every error can be attributed to extraction, language coverage or a verification function.',
    'To evaluate TRACE on development and held-out test sets of model-written errors, frozen before the held-out test was generated, against a pattern-based checker, an LLM judge and MiniCheck, and on a labelled random sample of the assistant\'s own answers.',
  ] },
  { h3: '1.4.3 To address Research Question 3' },
  { numbered: [
    'To measure whether verification changes how often the assistant rebuts false premises in questions, and whether it harms ordinary answers.',
    'To measure the time, tokens and repeatability of verification, and compare them with an LLM judge.',
    'To keep the AI\'s only action, a draft purchase order, behind validation, role permissions, separation of duties and an audit trail.',
  ] },

  { h2: '1.5 Project Scope' },
  { h3: '1.5.1 Technical Implementation' },
  { p: 'The project is a full-stack web application: a React 19 and TypeScript front end, a Python FastAPI back end and a PostgreSQL database managed with SQLAlchemy and Alembic. The assistant uses Google\'s Gemini API (free tier); all evaluation runs use `gemini-3.5-flash-lite`, and a second, open-weight model (`gemma-4-31b-it`) is used to test whether the design depends on one model.' },
  { h3: '1.5.2 Functional Capabilities' },
  { bullets: [
    '**ERP modules:** dashboard, sales, inventory, products, suppliers, procurement with a Draft → Pending Approval → Approved/Rejected workflow, Approval Center and audit log.',
    '**Analytics:** stockout risk with its evidence, reorder suggestions, demand forecasts, supplier performance, risk alerts and what-if projections.',
    '**AI assistant:** questions in plain language, answered through tools, with the sources, knowledge passages and verification results shown under each answer.',
    '**Proactive insights:** scheduled scans that explain each high or critical risk and recommend an action.',
    '**Verification:** figure tracing, typed assertion checking (TRACE), correction and warnings.',
    '**Controlled actions:** AI-drafted purchase orders that go through normal validation, review and approval by a different person.',
  ] },
  { h3: '1.5.3 Out of Scope' },
  { p: 'Text-to-SQL generation, model training or fine-tuning, a vector database, production deployment, and a study with real users are outside the scope of this one-semester project.' },

  { h2: '1.6 Project Limitations' },
  { h3: '1.6.1 Technical Constraints' },
  { p: 'The project used only the free tier of the Gemini API. Its daily request limits and frequent overload errors slowed the experiments and limited their size; for example, the natural-error study was run on the 211 answers that contain a sampled sentence rather than all 590. Supply-side data (purchase orders, deliveries and stock levels) are simulated from the real sales, because the source database\'s own supply records were not usable.' },
  { h3: '1.6.2 Design Considerations' },
  { p: 'TRACE can only check statements its assertion language can express. Statements about definitions, reasons and the system\'s own capabilities are outside the language. The extraction step uses an LLM and can therefore be wrong; the design makes such errors visible but does not remove them.' },

  { h2: '1.7 Research Methodology' },
  { p: 'The project follows a design-science approach [@hevner2004design]: an artefact (IntelliERP and TRACE) is built to address a practical problem, and its effect is measured with controlled experiments. Development was iterative, in eight phases, each of which was built, tested with automated tests and reviewed before the next started: (1) ERP foundation, (2) PostgreSQL persistence, (3) analytics, (4) LLM integration and tool calling, (5) enterprise grounding, (6) cross-module reasoning and proactive insights, (7) controlled actions and (8) evaluation. Results of the evaluation fed back into the design: five failures found in the first evaluation run led to five design changes, and the limits of the pattern-based checker led to TRACE. Chapter 3 describes the methodology in detail.' },

  { h2: '1.8 Target Audience' },
  { h3: '1.8.1 Primary' },
  { p: 'Operations staff in small and medium wholesale and retail businesses, such as inventory and procurement managers, who need fast, reliable answers that cross the sales, inventory and procurement modules.' },
  { h3: '1.8.2 Secondary' },
  { p: 'Managers and administrators who must trust and audit what an AI assistant tells their staff and what it changes in the system.' },
  { h3: '1.8.3 Tertiary' },
  { p: 'Developers and researchers building LLM assistants for enterprise software, who need a way to verify assistant output against a system of record.' },

  { h2: '1.9 Summary' },
  { p: 'This chapter introduced IntelliERP and the single problem it addresses: false statements by an LLM assistant in ERP decision support. The project prevents them with evidence grounding and detects them with run-time verification that keeps the decision of truth out of the language model. Three research questions and their objectives were set. The next chapter reviews the literature on which the design is based and the gaps it fills.' },
];
