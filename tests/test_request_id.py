import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from structlog.testing import capture_logs

from app.core.middleware import RequestIdMiddleware, pick_request_id
from app.main import app

client = TestClient(app)


def test_generates_request_id_when_missing() -> None:
    response = client.get("/health/live")
    uuid.UUID(response.headers["X-Request-ID"])  # raises if not a uuid


def test_echoes_valid_request_id() -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_replaces_unsafe_request_id() -> None:
    for bad in ["a" * 65, "has space", "semi;colon"]:
        response = client.get("/health/live", headers={"X-Request-ID": bad})
        assert response.headers["X-Request-ID"] != bad
        uuid.UUID(response.headers["X-Request-ID"])
    assert pick_request_id("abc\n") != "abc\n"  # log-injection guard


def test_access_log_has_fields_and_no_secrets() -> None:
    with capture_logs() as logs:
        client.get(
            "/health/live?token=SECRETQ",
            headers={"Authorization": "Bearer SECRETH", "X-Request-ID": "abc-123"},
        )
    access = [e for e in logs if e["event"] == "request"]
    assert len(access) == 1
    entry = access[0]
    assert entry["request_id"] == "abc-123"
    assert entry["method"] == "GET"
    assert entry["path"] == "/health/live"
    assert entry["status"] == 200
    assert isinstance(entry["duration_ms"], (int, float))
    assert "SECRET" not in str(logs)


def test_unhandled_error_logs_500_once() -> None:
    boom_app = FastAPI()
    boom_app.add_middleware(RequestIdMiddleware)

    @boom_app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    boom_client = TestClient(boom_app, raise_server_exceptions=False)
    with capture_logs() as logs:
        response = boom_client.get("/boom")
    assert response.status_code == 500
    access = [e for e in logs if e["event"] == "request"]
    assert len(access) == 1
    assert access[0]["status"] == 500
