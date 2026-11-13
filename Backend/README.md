# IntelliERP backend

FastAPI service for IntelliERP, version 1.0 (all nine phases complete): PostgreSQL persistence, rule-based
analytics, and a grounded LLM assistant whose statements are checked against the data (claim patterns or TRACE,
set by `LLM_VERIFIER`), which makes checked recommendations, raises insights on a schedule and can draft purchase
orders for approval. See the [project README](../README.md) for scope, credentials,
the route list and the roadmap.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head              # create/upgrade the tables (database setup: see the project README)
python -m app.db.seed             # load demo data into an empty database
python -m app.db.load_dataset --reset   # or: replace it with the dataset in ../Data (last 12 months)
uvicorn app.main:app --reload     # http://localhost:8000, docs at /docs and /redoc
pytest                            # run the tests (in-memory backend)
```

Configuration is read from environment variables or a `.env` file (see `.env.example`). `FRONTEND_URL`
is the allowed CORS origin; separate several with commas. `DATA_BACKEND` is `postgres` (default) or
`memory`; `DATABASE_URL` is the SQLAlchemy URL.

## Layers

| Layer | Location | Responsibility |
|---|---|---|
| API | `app/api/v1/` | HTTP, status codes, permission dependencies. No business logic. |
| Service | `app/services/` | Business rules, workflows, building response schemas |
| LLM tools | `app/llm/` | The read-only functions the assistant may call, each tied to a permission |
| Knowledge | `app/knowledge/` | The passages the assistant is grounded in (`content.py`) and their retrieval (`base.py`) |
| Analytics | `app/analytics/` | Pure calculation functions (no I/O): demand, forecasting, stock risk, supplier performance, simulation |
| Repository | `app/repositories/` | Data access. `base.py` holds the interfaces; `postgres.py` and `mock_*.py` implement them |
| Database | `app/db/`, `migrations/` | SQLAlchemy tables, session factory, seed script, Alembic migrations |
| Seed data | `app/mock_data/` | Related demo records |

`app/api/deps.py` is the only place that names concrete repository classes. It opens one database
session per request and shares it between that request's repositories.

## AI assistant

`AIService` (`app/services/ai_service.py`) sends the question to the model together with the tools the
user's role allows, runs the tools the model asks for, and returns the answer with the list of tool
calls as `sources`. It talks to the model through a provider in `app/llm/providers.py`: Gemini by
default (`GEMINI_API_KEY`), or Claude with `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`.
`LLM_MODEL` overrides the provider's default model.

To add a provider: implement `start()` returning a conversation with `reply()` and
`add_tool_results()`, keep whatever the API needs passed back between tool calls, add it to
`build_provider`, and test it with a stand-in client as in `tests/test_providers.py`.

To add a tool: write an input model and a handler in `app/llm/tools.py`, register it in
`Toolbox._build` with the permission it needs, and add it to `test_every_tool_returns_data`. Keep
tools read-only and their results small; the model reads every character they return.

To add knowledge: add an `Entry` to `WRITTEN` in `app/knowledge/content.py` (take numbers from the code's
constants, and list other words people use for the term in `keywords`), then add a question for it to
`RETRIEVAL_CASES` in `tests/test_knowledge.py`. A new database column needs a line in
`COLUMN_DESCRIPTIONS` or the tests fail.

The tests never call the real model. `tests/test_ai.py` swaps in a scripted provider through the
`get_llm_provider` dependency.

## Recommendations and proactive insights

`app/llm/recommendations.py` builds the cross-module facts for a product or supplier and checks a
recommendation against them. `InsightService` (`app/services/insight_service.py`) runs a scan: the
analytics pick the findings, the model records one insight per finding through a single tool, and each
is checked and stored. `app/scheduler.py` runs scans from a background thread started in `main.py`; it
reads the last scan time from the database, so it is safe under the development reloader.

`AIActionService` (`app/services/ai_action_service.py`) is the only place the AI side changes ERP data:
it checks a reorder recommendation and passes it to `ProcurementService.create_draft`. Keep it that way;
do not give the assistant a tool that submits, approves or edits.

After pulling these changes run `alembic upgrade head` (adds `ai_scans`, `ai_insights` and the AI-origin
columns on `purchase_orders`).

## Working with the database

- Services receive domain entities (`app/models/entities.py`), never ORM objects. Repositories convert.
- Repositories flush but do not commit. A service that changes data calls `self._uow.commit()` once,
  at the end of the use case. Anything uncommitted is rolled back when the request ends.
- To change the schema: edit `app/db/models.py` and the matching entity, run
  `alembic revision --autogenerate -m "..."`, review the generated file, then `alembic upgrade head`.
  Autogenerate does not pick up CHECK constraints or sequences; add those by hand.
- New repository methods go on the interface in `base.py` and in both implementations.

## Adding a protected endpoint

```python
@router.get("", dependencies=[Depends(require_permission(Permission.SALES_VIEW))])
```

Use `user: User = Depends(require_permission(...))` instead when the handler needs the current user.
Add new permissions to `app/security/permissions.py`.

## Business rules

- Stock status (`app/utils/stock.py`): 0 → Out of Stock; ≤ 50% of safety stock → Critical;
  ≤ reorder level → Low Stock; otherwise In Stock.
- Purchase orders (`app/services/procurement_service.py`): the supplier must exist, be active and supply
  the product; quantity and price must be positive; expected delivery cannot precede the order date.
  Only drafts can be edited, deleted or submitted. An approval decision is final.
- Audit events are written for logins (including failures) and every purchase-order action.
