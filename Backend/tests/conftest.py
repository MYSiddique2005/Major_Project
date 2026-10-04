"""Test setup.

By default the suite runs on the in-memory backend (fast, no database needed).
Set TEST_DATABASE_URL to run the same tests against PostgreSQL:

    TEST_DATABASE_URL=postgresql+psycopg://intellierp:intellierp@localhost:5432/intellierp_test pytest

The schema is then rebuilt with the Alembic migrations and every test starts
from freshly seeded data. The database name must contain "test" because all
of its contents are destroyed.
"""
import os

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
USE_POSTGRES = bool(TEST_DATABASE_URL)

# Must be set before the application (and its cached settings) is imported.
if USE_POSTGRES:
    os.environ["DATA_BACKEND"] = "postgres"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
else:
    os.environ["DATA_BACKEND"] = "memory"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.deps import reset_memory_state  # noqa: E402
from app.main import app  # noqa: E402

API = "/api/v1"
PASSWORDS = {
    "admin": "admin123",
    "inventory": "inventory123",
    "procurement": "procurement123",
    "employee": "employee123",
}

requires_postgres = pytest.mark.skipif(not USE_POSTGRES, reason="needs TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def migrated_database():
    """Rebuilds the test database schema from the Alembic migrations (PostgreSQL runs only)."""
    if not USE_POSTGRES:
        yield
        return

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text

    from app.db.session import get_engine

    engine = get_engine()
    if "test" not in (engine.url.database or ""):
        pytest.exit(f"Refusing to wipe database '{engine.url.database}': its name must contain 'test'.")

    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL.replace("%", "%%"))
    command.upgrade(config, "head")
    yield
    engine.dispose()


@pytest.fixture
def client(migrated_database):
    if USE_POSTGRES:
        from app.db.seed import reset
        from app.db.session import get_session_factory

        with get_session_factory()() as session:
            reset(session)
            session.commit()
    else:
        reset_memory_state()
    return TestClient(app)


@pytest.fixture
def auth(client):
    """Returns a function giving Authorization headers for a demo user."""

    def headers(username: str) -> dict[str, str]:
        response = client.post(f"{API}/auth/login", json={"username": username, "password": PASSWORDS[username]})
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return headers
