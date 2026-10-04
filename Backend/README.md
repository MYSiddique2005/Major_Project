# IntelliERP backend

FastAPI service for IntelliERP (Phase 3: PostgreSQL persistence and rule-based analytics). See the [project README](../README.md) for scope, credentials,
the route list and the roadmap.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head              # create/upgrade the tables (database setup: see the project README)
python -m app.db.seed             # load demo data into an empty database
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
| Analytics | `app/analytics/` | Pure calculation functions (no I/O): demand, forecasting, stock risk, supplier performance, simulation |
| Repository | `app/repositories/` | Data access. `base.py` holds the interfaces; `postgres.py` and `mock_*.py` implement them |
| Database | `app/db/`, `migrations/` | SQLAlchemy tables, session factory, seed script, Alembic migrations |
| Seed data | `app/mock_data/` | Related demo records |

`app/api/deps.py` is the only place that names concrete repository classes. It opens one database
session per request and shares it between that request's repositories.

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

## Business rules in this phase

- Stock status (`app/utils/stock.py`): 0 → Out of Stock; ≤ 50% of safety stock → Critical;
  ≤ reorder level → Low Stock; otherwise In Stock.
- Purchase orders (`app/services/procurement_service.py`): the supplier must exist, be active and supply
  the product; quantity and price must be positive; expected delivery cannot precede the order date.
  Only drafts can be edited, deleted or submitted. An approval decision is final.
- Audit events are written for logins (including failures) and every purchase-order action.
