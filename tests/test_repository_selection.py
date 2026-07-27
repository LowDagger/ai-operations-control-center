import socket
from pathlib import Path

import pytest

from control_center.config import AppMode, AppSettings
from control_center.repositories.exceptions import (
    RepositoryConfigurationError,
)
from control_center.repositories.factory import select_repository
from control_center.repositories.local_repository import LocalJsonRepository


def test_demo_mode_selects_local_repository_without_network(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    def fail_factory(url: str, anon_key: str, service_key: str | None) -> object:
        raise AssertionError("Supabase factory should not be called")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(socket.socket, "connect", fail_network)

    repository = select_repository(
        AppSettings(app_mode=AppMode.DEMO),
        tmp_path,
        supabase_factory=fail_factory,
    )

    assert isinstance(repository, LocalJsonRepository)


def test_live_mode_selects_supabase_repository() -> None:
    sentinel = object()
    captured: dict[str, str | None] = {}

    def factory(url: str, anon_key: str, service_key: str | None) -> object:
        captured.update(
            url=url,
            anon_key=anon_key,
            service_key=service_key,
        )
        return sentinel

    repository = select_repository(
        AppSettings(
            app_mode=AppMode.LIVE,
            supabase_url="https://example.supabase.co",
            supabase_anon_key="anon-key",
            supabase_service_role_key="service-key",
        ),
        Path("unused"),
        supabase_factory=factory,
    )

    assert repository is sentinel
    assert captured == {
        "url": "https://example.supabase.co",
        "anon_key": "anon-key",
        "service_key": "service-key",
    }


@pytest.mark.parametrize(
    "settings",
    [
        AppSettings(app_mode=AppMode.LIVE),
        AppSettings(
            app_mode=AppMode.LIVE,
            supabase_url="https://example.supabase.co",
        ),
    ],
)
def test_live_mode_rejects_missing_read_configuration(
    settings: AppSettings,
) -> None:
    with pytest.raises(
        RepositoryConfigurationError,
        match="SUPABASE_URL and SUPABASE_ANON_KEY",
    ):
        select_repository(settings, Path("unused"))

