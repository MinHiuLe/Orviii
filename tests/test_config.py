import pytest

from app.core.config import Settings


def test_app_env_overridden_by_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    assert Settings().app_env == "prod"


def test_database_url_overridden_by_env(monkeypatch: pytest.MonkeyPatch) -> None:
    url = "postgresql://u:p@db:5432/d"
    monkeypatch.setenv("DATABASE_URL", url)
    assert Settings().database_url == url
