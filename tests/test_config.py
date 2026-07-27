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

    settings = AppSettings.from_environment()

    assert settings.app_mode == AppMode.LIVE


def test_app_mode_rejects_invalid_environment_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_MODE", "staging")

    with pytest.raises(ValidationError):
        AppSettings.from_environment()

