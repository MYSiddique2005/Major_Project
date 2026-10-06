# IntelliERP

**IntelliERP: An LLM-Grounded Intelligent ERP Decision-Support System for Cross-Module Operational
Reasoning and Controlled Enterprise Actions** — university major/research project.

The research goal is to study how an LLM can be grounded in enterprise data and rules, reason across
Sales, Inventory and Procurement, surface operational risks, and turn recommendations into ERP actions
that are validated, permission-checked, approved by a person and audited.

**This repository is currently at Phase 5: the ERP foundation, PostgreSQL persistence, a rule-based
analytics engine, and an LLM assistant that answers questions by calling read-only ERP tools and is
grounded in a knowledge base of the company's schema, definitions and rules.**

## Scope so far (Phases 1–5)

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
  Claude) answers questions by calling 11 read-only tools over the analytics and ERP data, limited to what the
  user's role may see. Each answer lists the tool calls it used, and each question is audit-logged
- Enterprise grounding: a knowledge base of 37 passages (table and column meanings, business
  definitions, rules, workflows, role permissions, data notes). The passages relevant to each question
  are retrieved and given to the model, which can also search the knowledge base itself

Not implemented yet: proactive LLM alerts
(Phase 6), LLM-drafted purchase orders (Phase 7), the evaluation (Phase 8). Not planned: Text-to-SQL
(the model never writes SQL), a vector database, machine-learning models, production deployment.

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
└── LLM/                       empty; reserved for a later phase
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
| AI assistant | `POST /ai/chat`, `GET /ai/knowledge` |
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
Dates are moved forward so the last day of the data is the day it is loaded; reload if it was loaded
long ago. Approvals and audit logs start empty, and the demo accounts are unchanged. The in-memory
backend and the tests keep using the demo data described above.

## Analytics (Phase 3)

All calculations are deterministic and live in `Backend/app/analytics/` as pure functions; each module's
docstring states its rules. `AnalyticsService` feeds them ERP data through the repositories.

| Output | How it is calculated |
|---|---|
| Demand | Units sold per day over the last 28 days (cancelled orders excluded); trend = change against the previous 28 days, shown only when both periods have at least 5 orders |
| Stockout risk | **Critical**: nothing on hand and still selling. **High**: stock runs out before a new order could arrive and no delivery is due in time, or stock is below safety stock while demand is up 15% or more. **Medium**: below safety stock, or cover within 7 days of the lead time. **Low**: otherwise |
| Evidence | Each risk item lists the facts that produced it (stock vs safety stock, demand, trend, days of cover vs lead time, open orders) |
| Lead time | Average of the supplier's actual deliveries when there are at least two, otherwise the supplier's stated delivery time |
| Reorder suggestion | Order up to `demand × (lead time + 14-day review period) + safety stock`, minus stock and open orders, rounded up to 10. Only when the stock position is at or below the reorder point |
| Forecast | Weekly totals; 4-week moving average or 12-week linear trend. The method with the lower one-week-ahead error over the last 8 weeks is used unless one is requested |
| Supplier performance | On-time rate, average and longest delay, observed lead time, delay trend and overdue orders, from purchase-order history |
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
| `list_purchase_orders` | Purchase orders and their delivery dates | `procurement:view` |
| `list_suppliers` | Supplier master data | `suppliers:view` |

All tools are read-only. The model has no database access, writes no SQL, and takes every figure from a
tool result. It stops after at most 8 rounds of tool calls.

| Setting in `Backend/.env` | Meaning |
|---|---|
| `LLM_PROVIDER` | `gemini` (default) or `anthropic` |
| `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` | Key for the chosen provider |
| `LLM_MODEL` | Model name; default `gemini-3.8-flash` or `claude-opus-5-5` |
| `LLM_EFFORT` | Claude only: `low` to `max`, default `medium` |

Each question sends ERP figures to the provider. On Gemini's free tier Google may use that content to
improve its products and applies per-minute and per-day request limits; one question uses one request
per round of tool calls. Claude is billed per token to the key's account. The provider and model that
answered are returned with every response, so runs on different models can be compared in Phase 8.

## Enterprise grounding (Phase 5)

A general-purpose model does not know what "safety stock", "Low Stock" or "high risk" mean in this
system, or how its figures are calculated. The knowledge base in `Backend/app/knowledge/` tells it.

| Kind | Passages | Where the text comes from |
|---|---:|---|
| Schema | 9 | Generated from the database models: every table, column, key and foreign key, with a written description of each column |
| Definitions | 11 | Written: stock on hand, safety stock, reorder level and point, days of cover, demand and trend, lead time, units on order, on-time rate, revenue, margin, forecast error |
| Rules | 7 | Written: stock status, stockout risk, reorder suggestion, supplier risk, what-if assumptions, purchase-order validation, limits of the assistant |
| Workflows | 3 | Written: purchase-order lifecycle, approval, sales-order statuses |
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

## Data model

Tables: `users`, `suppliers`, `products`, `supplier_products` (which suppliers can deliver which
products), `inventory`, `sales_orders`, `purchase_orders`, `approvals`, `audit_logs`.

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
- A user who may approve can approve their own purchase order (no separation of duties yet).
- Lists are filtered and joined in Python after loading the table, and paginated in the browser. With
  12 months of the dataset loaded, sales endpoints take just under a second and the sales list is an
  18 MB response; loading more history would need SQL-level filtering and pagination.
- Two people deciding the same approval at the same instant are not guarded by row locks.
- Timestamps are stored without a time zone (server local time).
- Analytics: demand is assumed constant in projections; forecasts are simple statistical methods with
  no seasonality; supplier statistics rest on very few deliveries per supplier in the demo data; alerts
  are computed when requested, not by a scheduled job.
- Frontend has no automated tests.
- AI assistant: the answer arrives in one piece after all tool calls finish (no streaming), so a question
  can take up to a minute. The browser keeps the conversation; it is lost on reload and is not
  stored on the server.
  Automated tests use a scripted stand-in for the model, so they check the plumbing, not answer quality.

## Where later phases plug in

- **Recommendations (Phase 6):** fill the `recommendations` field of the chat response, which the
  frontend already receives.
- **LLM-drafted purchase orders (Phase 7):** add a tool that calls `ProcurementService.create_draft` and
  report it in `actions`. Drafts from any source go through the same validation, approval and audit path.

## Roadmap

| Phase | Content |
|---|---|
| 1 (done) | Frontend, FastAPI backend, mock ERP data, REST APIs, authentication, RBAC, ERP workflows, approval workflow, audit logs |
| 2 (done) | PostgreSQL, SQLAlchemy, Alembic, persistent ERP data |
| 3 (done) | Analytics, risk detection, forecasting, what-if analysis |
| 4 (done) | LLM integration, natural-language interface, tool/function calling |
| 5 (current) | Enterprise grounding: RAG, schema metadata, business rules, enterprise knowledge |
| 6 | Cross-module LLM reasoning, proactive intelligence, explainable recommendations |
| 7 | Controlled ERP actions, human approval, LLM-generated purchase-order drafts |
| 8 | Evaluation: research experiments, reliability testing, hallucination analysis, cross-module reasoning evaluation |
# Major_Project
