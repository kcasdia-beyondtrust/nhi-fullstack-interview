"""API tests. Requires the Postgres container to be up (docker compose up -d db)."""

import os
import sys
from pathlib import Path

import pytest
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import DEFAULT_DATABASE_URL, build_engine, create_app, ensure_schema  # noqa: E402

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def database():
    engine = build_engine(DATABASE_URL)
    try:
        ensure_schema(engine)
    except SQLAlchemyError as exc:
        pytest.skip(f"Postgres is not reachable ({exc.__class__.__name__}). Run: docker compose up -d db")
    return engine


@pytest.fixture
def client():
    return create_app(DATABASE_URL).test_client()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_hello_returns_the_seeded_message(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.get_json() == {"message": "hello world"}
