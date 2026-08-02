"""Shared pytest fixtures: test database, app client and helpers."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Configure the environment BEFORE importing application modules.
os.environ["DATABASE_URL"] = "sqlite:///./test_career.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["STORAGE_LOCAL_PATH"] = tempfile.mkdtemp(prefix="career_test_storage_")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402,F401  (registers tables on Base.metadata)
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_test_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    from app.db.seed import seed_all
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        seed_all(session)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_tables_between_tests(_create_test_schema):
    """Truncate all tables before each test for full isolation."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
    from app.db.seed import seed_all
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        seed_all(session)
    yield


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def signup_and_login(client, email: str = "user@test.io", password: str = "SecurePass123") -> dict:
    """Register and log in a user, returning tokens and user info."""
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "full_name": "Test User", "password": password},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    return {
        "user": body["user"],
        "access_token": body["tokens"]["access_token"],
        "refresh_token": body["tokens"]["refresh_token"],
    }


def auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
def authed_client(client):
    creds = signup_and_login(client)
    client.headers.update(auth_headers(creds["access_token"]))
    return client, creds


@pytest.fixture()
def admin_client(client):
    creds = signup_and_login(client, email="admin@test.io")
    from app.db.session import SessionLocal
    from app.repositories.user_repo import UserRepository

    with SessionLocal() as session:
        user = UserRepository(session).get_by_email("admin@test.io")
        user.role = "admin"
        session.commit()
    client.headers.update(auth_headers(creds["access_token"]))
    return client, creds
