import pytest
from pydantic import ValidationError

from control_center.config import AppMode, AppSettings


def test_app_mode_defaults_safely_to_demo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_MODE", raising=False)

    settings = AppSettings.from_environment()

    assert settings.app_mode == AppMode.DEMO


def test_app_mode_accepts_allowed_environment_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_MODE", " LIVE ")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

    settings = AppSettings.from_environment()

    assert settings.app_mode == AppMode.LIVE
    assert settings.gemini_api_key is not None
    assert settings.gemini_api_key.get_secret_value() == "test-key"
    assert settings.gemini_model == "gemini-test"
    assert "test-key" not in repr(settings)


def test_app_mode_rejects_invalid_environment_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_MODE", "staging")

    with pytest.raises(ValidationError):
        AppSettings.from_environment()
