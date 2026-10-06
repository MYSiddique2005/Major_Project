from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.db.session import get_engine
from app.scheduler import ScanScheduler

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Runs the proactive AI scan scheduler for as long as the server is up."""
    scheduler = ScanScheduler() if settings.insight_scan_interval_minutes > 0 else None
    if scheduler:
        scheduler.start()
    yield
    if scheduler:
        scheduler.stop()


app = FastAPI(
    lifespan=lifespan,
    title=f"{settings.app_name} API",
    version="0.1.0",
    description=(
        "ERP foundation for IntelliERP: Sales, Inventory, Procurement, Suppliers and Products with JWT "
        "authentication, role-based access control, a purchase-order approval workflow and audit logging. "
        "Data is stored in PostgreSQL (or in memory when `DATA_BACKEND=memory`).\n\n"
        "The AI assistant (`POST /api/v1/ai/chat`) answers from read-only ERP tools and needs "
        "`GEMINI_API_KEY` (or `ANTHROPIC_API_KEY` with `LLM_PROVIDER=anthropic`).\n\n"
        "To try protected endpoints: call `POST /api/v1/auth/login`, then click **Authorize** and paste "
        "the `access_token`."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(OperationalError)
async def database_unavailable_handler(_: Request, __: OperationalError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "The database is unavailable. Please try again later."})


def _database_status() -> str:
    if settings.data_backend == "memory":
        return "not used"
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except OperationalError:
        return "unavailable"


@app.get("/health", tags=["Health"], summary="Liveness check, including database connectivity")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "data_backend": settings.data_backend,
        "database": _database_status(),
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)
