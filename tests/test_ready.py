from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.db import DbCheck, get_db_check
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def _override(check: DbCheck) -> None:
    app.dependency_overrides[get_db_check] = lambda: check


def test_ready_ok() -> None:
    async def ok() -> None:
        return None

    _override(ok)
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_503_hides_error_details(caplog: pytest.LogCaptureFixture) -> None:
    async def fail() -> None:
        raise RuntimeError("postgresql+asyncpg://u:s3cret@db:5432/x")

    _override(fail)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "s3cret" not in response.text
    assert "s3cret" not in caplog.text
