# IntelliERP

**IntelliERP: Evidence-Grounded Hallucination Detection and Verification for LLM-Based ERP Decision
Support** — university major/research project.

The research problem is hallucination in LLM-based ERP decision support: an assistant that states a wrong
figure, trend, risk level, company rule or permission. The project addresses it in two ways, both based on
the system's own evidence. It **prevents** false statements by grounding the LLM in enterprise data and
rules (deterministic analytics, permission-checked tools, a knowledge base generated partly from the code),
and it **detects** the ones that remain by verifying every statement at run time against the system of
record (figure tracing, a pattern-based claim checker, and TRACE, a typed assertion verifier). The only
action the AI can take is a draft purchase order that is validated, approved by a second person and audited.

**All nine phases are built. The repository contains the ERP foundation, PostgreSQL persistence, a rule-based
analytics engine, and an LLM assistant that is grounded in the company's schema and rules, reasons
across sales, inventory and procurement, raises insights on its own, makes recommendations that the
server checks against its own figures, and can turn a recommendation into a draft purchase order that
a person must review, submit and approve.**

An evaluation of the assistant on 86 questions, before and after fixes and repeated three times, is in `LLM/`
(Phase 8). The typed run-time verifier TRACE and its evaluation on development, held-out, natural-error and
false-premise sets are described under [TRACE](#typed-run-time-verification-trace-phase-9) (Phase 9). The
papers and the project report are in `Research/` (see [Research documents](#research-documents)).

## Scope (Phases 1–9)

Implemented:

- ERP modules: Sales, Inventory, Procurement, Suppliers, Products
- Dashboard with KPIs and charts, all served by the API
- JWT authentication and role-based access control (enforced by the backend, mirrored in the UI)
- Purchase-order workflow: Draft → Pending Approval → Approved / Rejected, with validation
- Approval Center and audit log
- PostgreSQL persistence through SQLAlchemy repositories, with Alembic migrations and a seed script
- An in-memory backend with the same demo data (`DATA_BACKEND=memory`) for running without a database
- Analytics (deterministic rules and statistics, not AI): stockout risk per product with the evidence
  behind each level, reorder suggestions, weekly demand forecasts, supplier delivery performance,
  dashboard risk alerts and what-if stock projections
- AI assistant: a chat page and `POST /api/v1/ai/chat`. An LLM (Google Gemini by default, or Anthropic
  Claude) answers questions by calling read-only tools over the analytics and ERP data, limited to what the
  user's role may see. Each answer lists the tool calls it used, and each question is audit-logged
- Enterprise grounding: a knowledge base of 41 passages (table and column meanings, business
  definitions, rules, workflows, role permissions, data notes). The passages relevant to each question
  are retrieved and given to the model, which can also search the knowledge base itself

- Cross-module reasoning: one tool returns a product's facts grouped by module (sales, inventory,
  procurement, supplier), and recommendations must give their evidence by module
- Checked recommendations: the assistant records each recommendation in a fixed structure, and the
  server compares it with the analytics (severity, reorder quantity, supplier, every figure in the text)
- Proactive insights: a scheduled scan has the assistant explain the current high and critical findings
  and recommend an action for each; they appear on the dashboard and the AI Insights page

- Controlled actions: a reorder recommendation or insight can become a draft purchase order, by a
  button or by asking the assistant. The draft is marked with its AI origin, carries the recommendation
  and its checks, and goes through the same validation, submission and approval as any other order

- Evaluation: a resumable harness in `LLM/evaluation` asks questions whose correct answers are computed
  from the database, with and without grounding, and scores the answers without using a model as judge

- Typed run-time verification (TRACE): an LLM extracts each factual statement of an answer as a typed
  assertion (64 attributes, 24 rule keys, 21 actions), and deterministic code decides whether it is true
  against the database, the analytics and the rule and permission registry (`LLM_VERIFIER=trace`)

Not planned: Text-to-SQL (the model never writes SQL), a vector database, machine-learning models,
production deployment.

## Technology

| Layer | Stack |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2, pydantic-settings, PyJWT, bcrypt, Uvicorn, pytest |
| LLM | Google Gemini (`google-genai`) or Anthropic Claude (`anthropic`), chosen by `LLM_PROVIDER` |
| Database | PostgreSQL, SQLAlchemy 2, Alembic, psycopg 3 |
| Frontend | React 19, TypeScript, Vite, React Router, Axios, Tailwind CSS v4, Recharts, Lucide |

The AI assistant needs a model API key in `Backend/.env`: `GEMINI_API_KEY` (free tier, from
<https://aistudio.google.com/apikey>) or, with `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY`. Everything
else runs without one, and the assistant page then says it is not configured. PostgreSQL is needed for
persistent data; without it, set `DATA_BACKEND=memory`.

## Project structure

```
Major_Project/
├── Backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, CORS, error handling
│   │   ├── api/               deps.py (wiring), router.py, v1/ (one router per module)
│   │   ├── core/              settings, JWT + password hashing, domain exceptions
│   │   ├── models/            domain entities and enums
│   │   ├── db/                SQLAlchemy tables, session factory, seed script
│   │   ├── schemas/           Pydantic request/response contracts
│   │   ├── services/          business logic and workflows
│   │   ├── analytics/         pure calculation functions: demand, forecasting, risk, simulation
│   │   ├── llm/               the tools the AI assistant may call
│   │   ├── knowledge/         the knowledge base the assistant is grounded in, and its retrieval
│   │   ├── repositories/      base.py (interfaces), postgres.py, mock_*.py (in-memory)
│   │   ├── mock_data/         demo records used to seed either backend
│   │   ├── security/          authentication, authorization, role → permission map
│   │   └── utils/
│   ├── migrations/            Alembic migrations
│   └── tests/
├── Frontend/
│   └── src/
│       ├── components/        common/ (table, modal, badges, ...), layout/, dashboard/, ...
│       ├── pages/             one file per route
│       ├── services/          api.ts + one service per backend module
│       ├── context/           AuthContext, ToastContext
│       ├── hooks/  types/  utils/
├── Data/                      Wide World Importers dataset: raw, cleaned, simulated, processed (see Data/README.md)
└── LLM/                       evaluation of the assistant: questions, runner, scoring, results (see LLM/README.md)
```

Request flow: `React page → service (Axios) → FastAPI route → service → repository interface → PostgreSQL`.

## Running it

### 1. Database

**Option A: project-owned PostgreSQL (no admin rights needed).** Uses the PostgreSQL binaries already
installed on the machine, runs as your user, stores its data in `Backend/.pgdata/` and listens only on
`localhost:5434`:

```bash
cd Backend
scripts/dev_db.sh start      # creates the instance and the database on first use
```

It does not start by itself after a reboot, so run `scripts/dev_db.sh start` before the backend
(`stop` and `status` are also available). `Backend/.env` must point at it:

```
DATA_BACKEND=postgres
DATABASE_URL=postgresql+psycopg://intellierp:intellierp@localhost:5434/intellierp
```

**Option B: the system PostgreSQL service (port 5432).** Needs `sudo` once; this matches the default
`DATABASE_URL`, so no `.env` entry is required:

```bash
sudo -u postgres psql -c "CREATE ROLE intellierp LOGIN PASSWORD 'intellierp'" \
                      -c "CREATE DATABASE intellierp OWNER intellierp"
```

The `intellierp` password is for local development only.

**Then, for either option (first time only),** create the tables and load the demo data:

```bash
cd Backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed
```

`python -m app.db.seed` loads the small hand-written demo data. To load the Wide World Importers
dataset instead (see [Dataset](#dataset)):

```bash
python -m app.db.load_dataset --reset    # replaces all rows; --months N sets the history (default 12, 0 = all)
```

To run without PostgreSQL at all, put `DATA_BACKEND=memory` in `Backend/.env` (demo data only).

### 2. Backend

http://localhost:8000, Swagger at http://localhost:8000/docs, ReDoc at `/redoc`:

```bash
cd Backend
python3 -m venv .venv            # first time only
source .venv/bin/activate
pip install -r requirements.txt  # first time only
uvicorn app.main:app --reload
```

`GET /health` reports which data backend is active and whether the database is reachable.

### 3. Frontend

http://localhost:5173:

```bash
cd Frontend
npm install                      # first time only
npm run dev
```

### Database tasks

| Task | Command (in `Backend/`, virtualenv active) |
|---|---|
| Apply migrations | `alembic upgrade head` |
| Create a migration after changing `app/db/models.py` | `alembic revision --autogenerate -m "describe change"` then review the file |
| Check models and database agree | `alembic check` |
| Wipe all rows and reload the demo data | `python -m app.db.seed --reset` |
| Wipe all rows and load the dataset | `python -m app.db.load_dataset --reset` |

### Tests

```bash
cd Backend && source .venv/bin/activate
pytest                                   # in-memory backend, no database needed
TEST_DATABASE_URL=postgresql+psycopg://intellierp:intellierp@localhost:5434/intellierp_test pytest
```

The second form runs the same suite plus persistence and constraint tests against PostgreSQL. It
rebuilds that database from the migrations and wipes it, so the name must contain `test`
(create it once with `PGPASSWORD=intellierp createdb -h localhost -p 5434 -U intellierp intellierp_test`
for Option A, or `sudo -u postgres createdb -O intellierp intellierp_test` and port 5432 for Option B).

## Demo credentials

**Development only.** These accounts are defined in `Backend/app/mock_data/users.py`, loaded by the seed
script (passwords are stored as bcrypt hashes) and shown on the login page. Replace them, and set a real `SECRET_KEY`, before any deployment.

| Username | Password | Role | Can do |
|---|---|---|---|
| `admin` | `admin123` | ADMIN | Everything, including audit logs |
| `inventory` | `inventory123` | INVENTORY_MANAGER | View dashboard, sales, inventory, products, suppliers; analytics; AI page |
| `procurement` | `procurement123` | PROCUREMENT_MANAGER | View inventory, products, suppliers; create, submit and approve purchase orders; analytics; AI page |
| `employee` | `employee123` | EMPLOYEE | Read-only: dashboard, sales, inventory, products, suppliers |

The role → permission map lives in `Backend/app/security/permissions.py`.

## API

All routes are under `/api/v1` and, except login, require `Authorization: Bearer <token>`.

| Area | Routes |
|---|---|
| Auth | `POST /auth/login`, `GET /auth/me` |
| Dashboard | `GET /dashboard/summary`, `/dashboard/sales-trend`, `/dashboard/inventory-status`, `/dashboard/procurement-status` |
| Products | `GET /products`, `GET /products/{id}` |
| Sales | `GET /sales`, `GET /sales/stats`, `GET /sales/{id}` |
| Inventory | `GET /inventory`, `GET /inventory/stats`, `GET /inventory/{id}` |
| Suppliers | `GET /suppliers`, `GET /suppliers/{id}` |
| Procurement | `GET /procurement`, `GET /procurement/{id}`, `POST /procurement`, `PUT /procurement/{id}`, `DELETE /procurement/{id}`, `POST /procurement/{id}/submit` |
| Approvals | `GET /approvals`, `GET /approvals/{id}`, `POST /approvals/{id}/approve`, `POST /approvals/{id}/reject` |
| Analytics | `GET /analytics/stock-risk`, `GET /analytics/stock-risk/{product_id}`, `GET /analytics/forecast/{product_id}`, `GET /analytics/supplier-performance`, `GET /analytics/alerts`, `POST /analytics/what-if` |
| Audit | `GET /audit-logs` |
| AI assistant | `POST /ai/chat`, `GET /ai/knowledge`, `POST /ai/recommendations/draft-order` |
| AI insights | `GET /ai/insights`, `GET /ai/insights/scans`, `POST /ai/insights/scan`, `POST /ai/insights/{id}/acknowledge`, `POST /ai/insights/{id}/dismiss`, `POST /ai/insights/{id}/draft-order` |
| System | `GET /system/info` |
| Health | `GET /health` (no prefix) |

List endpoints accept `search` and module-specific filters (`status`, `product_id`, ...).

## Demo data

21 products, 10 suppliers, 24 inventory records, about 1,570 sales orders (one year of history) and 27
purchase orders, all sharing the same IDs so cross-module questions have real answers. Example: Laptop
Pro 14 (`P001`) has 470 units against a safety stock of 600, sales up about 35% over the last eight
weeks, a primary supplier (`S001`) and an 800-unit purchase order awaiting approval. Brightline Components (`S002`) has a pattern of late deliveries.
Dates are generated relative to the day the data is seeded, and the analytics look at the most recent
weeks, so re-seed (`python -m app.db.seed --reset`) if a PostgreSQL database was seeded long ago or
before Phase 3 (which enlarged the sales history).

## Dataset

`Data/` holds a larger dataset built from Microsoft's Wide World Importers sample ERP database (MIT
licence): 227 products, 7 goods suppliers, 663 customers and 231,412 sales order lines from 2013 to
2016. Products, suppliers, customers, prices, costs and all sales are source records. **Purchase orders,
deliveries and stock levels are simulated** from the real sales with a reorder-point policy and
assumed supplier reliability, because the source's own supply-side records were not usable; report
supply-side results as simulated. `Data/README.md` describes the pipeline, the model and the limits.

`python -m app.db.load_dataset --reset` loads it into PostgreSQL: all products, suppliers and stock,
plus the most recent 12 months of sales (about 72,700 lines) and purchase orders (about 5,400 lines).
Dates are moved forward so the last day of the data is the day it is loaded. Afterwards the system keeps
treating the data's last day as "today" (`BUSINESS_DATE=auto`, see `Backend/app/core/clock.py`), so the
analytics do not drift as calendar days pass and no reload is needed. The header shows that date. Approvals and audit logs start empty, and the demo accounts are unchanged. The in-memory
backend and the tests keep using the demo data described above.

## Analytics (Phase 3)

All calculations are deterministic and live in `Backend/app/analytics/` as pure functions; each module's
docstring states its rules. `AnalyticsService` feeds them ERP data through the repositories.

| Output | How it is calculated |
|---|---|
| Demand | Units sold per day over the last 28 days (cancelled orders excluded); trend = change against the previous 28 days, shown only when both periods have at least 5 orders |
| Stockout risk | **Critical**: nothing on hand and still selling. **High**: stock runs out before a new order could arrive and no delivery is due in time, or stock is below safety stock while demand is up 15% or more. **Medium**: below safety stock; or cover within 7 days of the lead time with no delivery due in time; or stock runs out before a new order could arrive and the delivery it relies on comes from a supplier with High delivery risk. **Low**: otherwise, including short stock covered by a delivery due in time |
| Evidence | Each risk item lists the facts that produced it (stock vs safety stock, demand, trend, days of cover vs lead time, open orders) |
| Lead time | Average of the supplier's actual deliveries when there are at least two, otherwise the supplier's stated delivery time |
| Reorder suggestion | Order up to `demand × (lead time + 14-day review period) + safety stock`, minus stock and open orders, rounded up to 10. Only when the stock position is at or below the reorder point |
| Forecast | Weekly totals; 4-week moving average or 12-week linear trend. The method with the lower one-week-ahead error over the last 8 weeks is used unless one is requested |
| Supplier performance | On-time rate, average and longest delay, observed lead time and overdue orders, from purchase-order history. Delay trend: orders due in the last 60 days against the 60 days before, counting an order still overdue with its delay so far |
| What-if | Day-by-day stock projection for a changed demand level, delivery delay and/or a new order, compared with the baseline. Read-only |

A reorder suggestion never creates anything by itself. A user with procurement rights can open it as a
pre-filled draft, which then goes through the normal validation, approval and audit path.

## AI assistant (Phase 4)

`POST /ai/chat` takes a `message` and, optionally, the earlier turns of the conversation as `history`.

1. The backend offers the model only the tools the user's role has permission for.
2. The model chooses tools; the backend runs them through the same services the pages use and returns
   the results. The permission is checked again when each tool runs.
3. The model writes its answer from those results. The response carries the answer, the tool calls as
   `sources`, the model name and token usage.

| Tool | Returns | Permission |
|---|---|---|
| `list_stock_risk`, `get_stock_risk` | Stockout risk with its evidence, reorder point, suggested order | `analytics:view` |
| `get_demand_forecast` | 26 weeks of demand and a weekly forecast | `analytics:view` |
| `list_supplier_performance` | On-time rate, delays, lead time, overdue orders | `analytics:view` |
| `list_risk_alerts` | Current high and critical alerts | `analytics:view` |
| `run_what_if` | Stock projection under a changed demand, delay or order | `analytics:view` |
| `search_products` | Product master data and stock status | `products:view` |
| `get_inventory` | Stock records of a product | `inventory:view` |
| `get_sales_summary` | Units, revenue, weekly units, top customers and products | `sales:view` |
| `list_purchase_orders` | Purchase orders and their delivery dates, the number overdue, or one order by its ID | `procurement:view` |
| `list_suppliers` | Supplier master data | `suppliers:view` |
| `get_product_overview` | One product's facts grouped by module (Phase 6) | `analytics:view` |
| `propose_recommendation` | Records a recommendation and returns the server's checks on it (Phase 6) | `analytics:view` |
| `search_knowledge` | Passages from the knowledge base (Phase 5) | `ai:use` |
| `draft_purchase_order` | Creates a draft purchase order from a reorder recommendation (Phase 7) | `procurement:create` |

All tools are read-only except `draft_purchase_order`, which can only create a Draft. The model has no
database access, writes no SQL, and is instructed to take every figure from a tool result. It stops after
at most 8 rounds of tool calls.

Three things keep an answer tied to the data rather than to the model's instructions alone:

- **Lists say when they are cut off.** A list tool returns at most 50 rows. Its result gives the totals
  over everything that matched (for purchase orders, including how many are overdue) and, when rows were
  left out, a note saying so, so the model does not count the rows it happens to see.
- **Figures need a source.** The server looks up every figure in the answer among the tool results, the
  knowledge passages supplied, the question and the earlier turns. If the answer states figures although
  no tool was called, it is sent back to the model once to be corrected. Figures that still cannot be
  traced are returned as `unverified_figures` and shown under the answer as a caution. Whole numbers up
  to 10 are ignored (they are usually counts of the items listed), and a figure the model worked out
  from tool results is flagged, not blocked.
- **Statements are checked too.** `app/llm/claims.py` finds 12 kinds of qualitative statement (below
  safety stock, demand rising, units overdue or on time, a delivery due in time, a risk level, a stock
  status, and others) and checks each against the same facts the model was given. A chat answer that
  contradicts the data is sent back once; a contradicted recommendation is returned to the model to be
  re-recorded; an insight that contradicts the data is not stored until corrected; an AI-drafted order is
  flagged for its reviewer. Contradictions that remain are shown under the answer.
- **The user's rights are stated.** Each question tells the model what the user's role cannot see and
  what the user may do with purchase orders, so it does not present its own limits as the user's.

| Setting in `Backend/.env` | Meaning |
|---|---|
| `LLM_PROVIDER` | `gemini` (default) or `anthropic` |
| `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` | Key for the chosen provider |
| `LLM_MODEL` | Model name; default `gemini-3.8-flash` or `claude-opus-5-5` |
| `LLM_FALLBACK_MODEL` | Gemini only: models to move on to, in order, when the one in use is overloaded or out of daily quota; default `gemini-3.5-flash,gemini-3.5-flash-lite` |
| `INSIGHT_SCAN_INTERVAL_MINUTES` | Minutes between scheduled scans; default 1440, 0 switches them off |
| `INSIGHT_MAX_FINDINGS` | Findings analysed per scan; default 6 |
| `LLM_EFFORT` | Claude only: `low` to `max`, default `medium` |

Each question sends ERP figures to the provider. On Gemini's free tier Google may use that content to
improve its products and limits requests per model: 5 a minute and 20 a day on `gemini-3.8-flash` when
this was written. One question uses one request per round of tool calls, so a day's quota on one model
is a handful of questions. The assistant waits out the per-minute limit and moves to the next fallback
model when a model is overloaded or its daily quota is used up. Claude is billed per token to the key's account. The provider and model that
answered are returned with every response, so runs on different models can be compared in Phase 8.

## Enterprise grounding (Phase 5)

A general-purpose model does not know what "safety stock", "Low Stock" or "high risk" mean in this
system, or how its figures are calculated. The knowledge base in `Backend/app/knowledge/` tells it.

| Kind | Passages | Where the text comes from |
|---|---:|---|
| Schema | 11 | Generated from the database models: every table, column, key and foreign key, with a written description of each column |
| Definitions | 11 | Written: stock on hand, safety stock, reorder level and point, days of cover, demand and trend, lead time, units on order, on-time rate, revenue, margin, forecast error |
| Rules | 8 | Written: stock status, stockout risk, reorder suggestion, supplier risk, what-if assumptions, purchase-order validation, limits of the assistant, how insights and recommendations are checked |
| Workflows | 4 | Written: purchase-order lifecycle, approval, AI-drafted purchase orders, sales-order statuses |
| Access | 4 | Generated from the role → permission map |
| Data notes | 3 | Written: identifiers and how modules link, what is source data and what is simulated, limits of the figures |

Thresholds and periods in the written passages are filled in from the constants of the code that applies
them, and a test fails if a database column has no description, so the knowledge base cannot drift from
the system.

How it is used for each question:

1. **Retrieve.** The question (with the previous question, for follow-ups) is matched against every
   passage with BM25 keyword ranking over title, alternative keywords and text. The best 4 are kept.
2. **Augment.** Those passages are placed in front of the question inside `<knowledge>` tags, and the
   model is told to treat them as the authority on terms and rules.
3. **Generate.** The model answers, still taking all figures from the ERP tools. It can call
   `search_knowledge` for anything the supplied passages do not cover.

The response lists the passages supplied (`knowledge`), and the chat page shows them under the answer.
`GET /ai/knowledge` returns or searches the knowledge base. Retrieval is keyword-based, not embedding-based:
the collection is small and written in the vocabulary users ask in, and it needs no second external
service. On 26 test questions the answering passage is ranked first for 24 and in the top three for all
26; those questions were written alongside the passages, so this checks that retrieval works, not how it
does on questions from real users.

`LLM_GROUNDING=false` in `Backend/.env` removes the passages, the instruction and the search tool, which
is how Phase 8 will measure what grounding contributes.

## Cross-module reasoning, recommendations and proactive insights (Phase 6)

**Cross-module facts.** `get_product_overview` gives the model one product's position grouped by the
module each fact comes from: sales (demand, trend, units per week, forecast), inventory (stock, safety
stock, days of cover), procurement (lead time, units on order, overdue units), the supplier's delivery
record, and the risk assessment. The same structure feeds the proactive scan.

**Checked recommendations.** When the assistant recommends an action it records it with
`propose_recommendation`: a headline, an explanation, an action (`reorder`, `expedite_delivery`,
`review_supplier` or `monitor`) and evidence labelled by module. The server then checks it
(`Backend/app/llm/recommendations.py`) and returns the results with it:

| Check | What it does |
|---|---|
| Severity | Set from the analytics; the model's opinion is not used |
| Reorder quantity | Compared with the quantity the reorder rule gives; both are shown if they differ |
| Supplier | Must be able to supply the product |
| Cross-module | Evidence must come from at least two of sales, inventory and procurement/supplier |
| Figures | Every number in the text is looked up among the system's figures for that product or supplier and the rule thresholds; any not found are listed |

The figure check is a lookup, not proof: it ignores identifiers and dates, allows rounding, and cannot
tell a correct figure used in the wrong place. The model is told what the checks found so it can correct
its answer. Recommendations appear as cards under the chat answer.

**Proactive insights.** A scan works in two halves. The analytics decide what is wrong (every High or
Critical stock or supplier finding) and how severe it is. The model receives the cross-module facts and
the applicable rules for the most severe findings (6 by default) and records one insight per finding
with the same structure and checks as above. It cannot raise an insight about anything the analytics did
not flag. A scan is normally one model request; the model is reminded once or twice if it leaves
findings out.

Scans run on a schedule (`INSIGHT_SCAN_INTERVAL_MINUTES`, default 1440 = daily, 0 = off) from a
background thread in the web process, and on demand from the AI Insights page. The time of the last scan
is stored, so restarting the server neither repeats nor skips one. Insights are stored in `ai_insights`
and scans in `ai_scans`. An insight is New until a user acknowledges or dismisses it, and is superseded
when its subject is analysed again or is no longer flagged. Viewing needs `analytics:view`; running a
scan and reviewing need `ai:use`. Scans and reviews are audit-logged. An insight creates no order.

## Controlled actions (Phase 7)

The AI side can cause exactly one change to the ERP data: a purchase order in status Draft.

1. **Recommendation.** A `reorder` recommendation names a product, a supplier and a quantity.
2. **Checks.** The server checks it again against the reorder rule, the supplier and the system's
   figures (the Phase 6 checks), using the figures of that moment.
3. **Draft.** `ProcurementService.create_draft` creates the draft, with the validation every purchase
   order passes. The order records its `origin` (AI Assistant or AI Insight), the insight it came from,
   and the recommendation with its evidence and check results as they stood.
4. **Review and submission.** A user with `procurement:create` reviews the draft, may edit it, and
   submits it.
5. **Approval.** A different user with `procurement:approve` approves or rejects it; the person the
   draft was made for cannot approve it. The purchase-order page and
   the Approval Center show the AI's reasoning and any warning from the checks.

Three ways in, one path: the "Create draft purchase order" button on a recommendation card in the chat,
the same button on a reorder insight, and the assistant's `draft_purchase_order` tool when the user
asks it to draft the order.

| Control | How it is enforced |
|---|---|
| Only a draft | The assistant has no tool that edits, submits, approves, cancels or places an order; a test asserts this |
| Only for users who could do it themselves | The tool is offered, and the endpoints open, only with `procurement:create`; the service checks again |
| Only on request | The assistant is instructed to draft only when the user asks, and to call the tool rather than say it will; this rests on the model following its instructions, not on code |
| Same rules as any order | Supplier must be active and supply the product; quantity and price limits apply |
| Bounded | At most 3 drafts for one chat message; one draft per insight |
| A different quantity is visible | A quantity that differs from the reorder rule is not blocked, but is flagged on the draft for the reviewer and approver |
| No substitute supplier | If the user names a supplier and the server refuses the draft (for example, that supplier does not supply the product), a draft from any supplier the user did not name is refused for the rest of that message; the user has to ask for it |
| A second person decides | Whoever the draft was made for cannot approve it (separation of duties) |
| Traceable | The audit log records the draft with its AI origin, and each later step |

## Evaluation (Phase 8)

`LLM/evaluation` runs the assistant, exactly as the web application builds it, on 86 questions in five
groups (grounding, factual, cross-module, controlled actions and permissions, abstention). Each case
computes its correct answer from the application's services at run time. 32 of the questions are also
asked with the knowledge base switched off. Scoring matches expected facts by number, phrase or pattern,
counts figures in an answer that nothing supports, and uses no model as a judge. `LLM/README.md`
explains how to run it and reports the results in full.

Runs of 10 to 13 October 2026, all on `gemini-3.5-flash-lite` (the free tier's smallest model), on the
Wide World Importers dataset:

| Run | Passed with grounding | 95% CI | Unsupported figures |
|---|---:|---:|---:|
| `extended-1`: before the fixes below | 81 of 86 (94%) | 87-97% | 4 of 334 |
| `fixed-1`: after the fixes | 84 of 86 (98%) | 92-99% | 1 of 310 |
| `fixed-2`: repeat | 86 of 86 (100%) | 96-100% | 3 of 342 |
| `fixed-3`: repeat | 86 of 86 (100%) | 96-100% | 2 of 332 |

| The same 32 questions | Passed with grounding | Passed without | p (exact sign test) |
|---|---:|---:|---:|
| `extended-1` | 32 | 9 | < 0.0001 |
| `fixed-1` / `fixed-2` / `fixed-3` | 32 / 32 / 32 | 8 / 9 / 9 | < 0.0001 each |

Without the knowledge base the assistant still answered 5 or 6 of 7 cross-module questions, because the
tools return those facts, but only 2 to 4 of 25 questions about the company's own terms and rules.
Across the three repeats of the fixed system, 84 of 86 questions passed every time with grounding; two
failed once. The unsupported figures with grounding are all figures worked out correctly from tool
results.

The first run found five real failures, and each led to a change in the system: overdue orders counted
from a truncated list; a real order declared missing for the same reason; figures and a supplier stated
without any lookup; a draft announced but not made, with the user's rights misdescribed; and a supplier
the user named swapped for another after the server refused it. The changes are described under
[AI assistant](#ai-assistant-phase-4) and [Controlled actions](#controlled-actions-phase-7). All five
passed in every repeat. Two other questions failed once after the changes (a supplier looked up by its
ID in a search that matches names, and a non-existent product described as having no stock).

**Claim verification.** On model-written rewrites of texts not used while it was written (verifier frozen
before scoring), the final version caught 48 of 62 planted false statements within its scope over two test sets (77%, 95% CI
66-86%) and raised false alarms on 2 of 124 paraphrases (2%). It also found two genuine model errors that
the keyword scoring had passed. See `LLM/evaluation/results/claims/summary.md`.

**A second model.** One run on the open-weight `gemma-4-31b-it`, on the same system, passed 86 of 86 with
grounding and 32 of 32 paired questions against 6 without (p < 0.0001). See `LLM/README.md`.

Two earlier runs on the first 24 questions (6 October) passed 23 and 24 of 24 with grounding and 5 of
10 without, and are unchanged under the current scoring.

These are indications from a test written by the system's builders, scored by keyword and corrected by
reading the answers, on two models from one provider; they are not statistically reliable rates. `LLM/README.md`
lists the limits, and the `report.md` and `notes.md` in each results folder have every answer and every
correction to the key.

## Typed run-time verification: TRACE (Phase 9)

The pattern-based claim checker of Phase 8 recognises twelve kinds of statement. **TRACE** (Typed Run-time
Assertion Checking for Enterprise assistants, `Backend/app/llm/trace/`) checks any statement its assertion
language can express:

- **Language** (`catalogue.py`, `schema.py`): an assertion is (quote, subject, attribute, comparator, value,
  tense, scenario). 64 attributes in three families by source of truth: *state* (the database), *derived*
  (the analytics: risk levels, reorder rule, forecasts, what-if simulations, rankings) and *policy* (24 rule
  constants read from the code, and what each role and the assistant may do, over 21 actions).
- **Extraction** (`extract_llm.py`, `extract_rule.py`): a model records the statements through one forced,
  schema-validated tool call; a rule extractor reuses the Phase 8 patterns. Hybrid mode runs both.
- **Verification** (`verify.py`, `engine.py`): deterministic. It resolves the subject, reads the true value
  through the application's services and compares. Four safeguards keep extraction errors from becoming
  false verdicts (subjects must be named in the text, ambiguous terms, type checks, records newer than the
  data). A contradicted chat answer is returned to the model once; what remains is shown to the user.
- **Setting:** `LLM_VERIFIER` in `Backend/.env`: `patterns` (default), `trace-rule` (no model call),
  `trace` (hybrid) or `off`.

TRACE was frozen (file hashes in `LLM/evaluation/results/trace/frozen.json`) before the held-out test was
generated, and `trace_score` refuses to run if the files have changed.

### Results

All on the Wide World Importers dataset; extraction with `gemini-3.5-flash-lite`. Every answer, extraction,
verdict and label is in `LLM/evaluation/results/trace/`.

| Held-out test (102 model-written errors, 103 paraphrases, two writer models) | Errors detected | False alarms |
|---|---:|---:|
| Patterns (Phase 8) | 15 (15%) | 2 (2%) |
| TRACE-rule (no model call) | 20 (20%) | 2 (2%) |
| TRACE-hybrid | 70 (69%, 95% CI 59-77%) | 4 (4%) |
| LLM judge, `gemini-3.5-flash-lite`, same evidence | 80 (78%) | 17 (17%) |
| LLM judge, `gemma-4-31b-it`, same evidence | 76 (75%) | 7 (7%) |
| MiniCheck (Flan-T5-Large) | 38 (37%) | 22 (21%) |

- TRACE-hybrid against the patterns: 55 errors only TRACE found, none only the patterns (McNemar exact,
  Holm-adjusted p < 1e-15). Against the two judges the difference in detection is not significant
  (p = 0.36). TRACE raised significantly fewer false alarms than the Gemini judge (p = 0.036) and
  MiniCheck, but not than the Gemma judge.
- Every one of TRACE's 32 misses and 4 false alarms was traced by hand: none came from a verification
  function; they came from the extractor (statement not recorded, or recorded unfaithfully) and from
  statements the language cannot express (`heldout-details.md`).
- On the development sets (183 errors), TRACE-hybrid detected 69% against 38% for the patterns
  (`dev-report.md`).
- **Natural errors** (`natural/`): in a random sample of 300 sentences from 590 stored answers, 19 of 261
  checkable sentences were false (7.3%): 2.4% with the knowledge base, 25.9% without it. TRACE found 4 of
  the 19 and the Gemini judge 10. Most natural errors misstate a definition, or relate two correct figures
  wrongly, which the language does not cover. Nine labels were corrected after a consistency check; the
  log is `natural/label-corrections.jsonl` and both versions are reported.
- **False-premise questions** (`../fpq-report.md`): 44 questions that assume something false. Answers
  rebutted the premise 89-93% of the time with the verifier off, and verification did not change this
  significantly on either model.
- **Harm check** (`harm-report.md`): the 86 questions with TRACE passed 84 of 86 (84, 86, 86 with the
  patterns). TRACE sent 10 answers back; two false alarms made a correct answer wrong.
- **Repeatability** (`repeat-extraction.md`, `repeat-judge.md`): given an extraction, verdicts are identical
  (420 of 420). Two extractions of the same 50 texts led to the same flag decision for 47 and the same
  flagged statements for 41; the Gemini judge asked twice: 47 and 34.

### Running the TRACE evaluation

```bash
cd LLM
PY=../Backend/.venv/bin/python
$PY -m evaluation.trace_eval extract && $PY -m evaluation.trace_eval dev      # development sets
$PY -m evaluation.trace_testset pool                                          # held-out pool (TRACE must be frozen)
LLM_MODEL=gemini-3.5-flash-lite $PY -m evaluation.trace_testset perturb --writer gemini
LLM_MODEL=gemma-4-31b-it        $PY -m evaluation.trace_testset perturb --writer gemma
$PY -m evaluation.trace_score extract                                         # TRACE extractions, cached
$PY -m evaluation.trace_baselines judge --set heldout-gemini                  # LLM judge (model = LLM_MODEL)
$PY -m evaluation.trace_baselines minicheck-prep --set heldout-gemini         # then: evaluation/minicheck_run.py
$PY -m evaluation.trace_score report                                          # results/trace/heldout-report.md
$PY -m evaluation.trace_natural sample                                        # natural errors: sample, extract, judge,
$PY -m evaluation.trace_natural score --scope sampled                         #   flags, sheets (labels), score
$PY -m evaluation.natural_sample_report                                       # the sample by condition
$PY -m evaluation.run --suite fpq --name fpq-gemini-trace --conditions grounded   # with LLM_VERIFIER=off|patterns|trace
$PY -m evaluation.fpq_report
bash evaluation/run_trace_harm.sh && $PY -m evaluation.harm_report            # the 86 questions with TRACE
$PY -m evaluation.extract_repeat extract && $PY -m evaluation.extract_repeat compare
$PY -m evaluation.judge_repeat && $PY -m evaluation.judge_repeat compare
```

All model calls are cached and resumable, because the free API tier limits and interrupts them.
`run_remaining.sh`, `run_gemma_shards.sh` and `run_gemma_repeat.sh` run the long jobs in loops.

## Research documents

| Document | Source | Build |
|---|---|---|
| Conference paper (IEEE conference format): the system, grounding and the pattern-based verifier | `Research/paper/intellierp.tex` | `pdflatex`, `bibtex`, `pdflatex` twice (or Overleaf) |
| Journal article (IEEE journal format): TRACE and its evaluation | `Research/journal/trace.tex` | the same |
| Final-year project report (Word) | `Research/report/` (`src/*.js` chapters, `build.js`) | `npm install`, `node make-figures.js`, `node render.js`, `node build.js` |

`Research/literature-review.md` and `Research/trace/annotation-guide.md` hold the literature notes and the
guide the natural-error labels follow.

## Data model

Tables: `users`, `suppliers`, `products`, `supplier_products` (which suppliers can deliver which
products), `inventory`, `sales_orders`, `purchase_orders`, `approvals`, `audit_logs`, `ai_scans`,
`ai_insights`.

- Foreign keys link products, inventory, sales and purchase orders to their product and supplier.
- Status and role columns are text guarded by CHECK constraints; quantities must be positive and
  stock cannot be negative.
- IDs keep readable prefixes (`PO-1028`) and come from one PostgreSQL sequence per table.
- Stock status and order totals are computed in the service layer, not stored.
- Each use case commits once, so a workflow step and its audit event are saved together or not at all.

## Current limitations

- The JWT is kept in `localStorage`; there is no refresh token or logout on the server side.
- No user management UI; the Settings page is read-only.
- Purchase orders stop at Approved/Rejected. Ordered and Delivered exist only in seed data.
- Separation of duties is by username only: whoever created or submitted a purchase order cannot approve
  it (`SEPARATION_OF_DUTIES=false` switches this off). With the demo accounts this means an order from
  `procurement` is approved by `admin`. There are no approval limits by amount.
- Lists are filtered and joined in Python after loading the table, and paginated in the browser. With
  12 months of the dataset loaded, sales endpoints take just under a second and the sales list is an
  18 MB response; loading more history would need SQL-level filtering and pagination.
- Two people deciding the same approval at the same instant are not guarded by row locks.
- Timestamps are stored without a time zone (server local time).
- Analytics: demand is assumed constant in projections; forecasts are simple statistical methods with
  no seasonality; supplier statistics rest on very few deliveries per supplier in the demo data; the rule-based
  alerts are computed when requested; only the AI insights are produced on a schedule.
- Frontend has no automated tests.
- AI assistant: the answer arrives in one piece after all tool calls finish (no streaming), so a question
  can take up to a minute. The browser keeps the conversation; it is lost on reload and is not
  stored on the server.
  Automated tests use a scripted stand-in for the model, so they check the plumbing, not answer quality.
  The check of an answer's figures is a lookup: it cannot tell a figure the model worked out correctly
  from one it made up, or a real figure used in the wrong place.

## What could come next

- **Two gaps the last run showed:** the stock-risk search does not match a supplier's ID, and asking for
  the stock of a product that does not exist returns "no stock records" instead of "no such product".
  They were left as they are so that the repeated runs measured one unchanged system.
- **Further evaluation:** questions written by other people, and the same runs on other models
  (`EVAL_MODEL` and `EVAL_PREFIX` with `run_extended.sh`).
- **TRACE:** a more faithful and more stable extractor (it misses or misrecords the changed statement in 21
  of 32 held-out misses, and two extractions of a text often differ); attributes for definitions, status
  meanings and relations between figures (most natural errors); a warning instead of automatic correction
  when a flag rests on one uncertain assertion; a second, human annotation of the natural-error labels
  (`LLM/evaluation/results/trace/natural/sheet-annotator-2.csv` is prepared for it); a user study.

## Roadmap

| Phase | Content |
|---|---|
| 1 (done) | Frontend, FastAPI backend, mock ERP data, REST APIs, authentication, RBAC, ERP workflows, approval workflow, audit logs |
| 2 (done) | PostgreSQL, SQLAlchemy, Alembic, persistent ERP data |
| 3 (done) | Analytics, risk detection, forecasting, what-if analysis |
| 4 (done) | LLM integration, natural-language interface, tool/function calling |
| 5 (done) | Enterprise grounding: RAG, schema metadata, business rules, enterprise knowledge |
| 6 (done) | Cross-module LLM reasoning, proactive intelligence, explainable recommendations |
| 7 (done) | Controlled ERP actions, human approval, LLM-generated purchase-order drafts |
| 8 (done) | Evaluation: research experiments, reliability testing, hallucination analysis, cross-module reasoning evaluation |
| 9 (done) | TRACE: typed run-time verification of the assistant's statements; held-out, natural-error, false-premise and harm experiments |
