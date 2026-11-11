import pytest

from app.core.config import Settings


def test_app_env_overridden_by_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    assert Settings().app_env == "prod"
