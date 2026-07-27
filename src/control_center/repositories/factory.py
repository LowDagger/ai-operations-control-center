"""Configuration-driven repository selection."""

from collections.abc import Callable
from pathlib import Path

from control_center.config import AppMode, AppSettings
from control_center.repositories.base import OperationsRepository
from control_center.repositories.exceptions import (
    RepositoryConfigurationError,
)
from control_center.repositories.local_repository import LocalJsonRepository
from control_center.repositories.supabase_repository import SupabaseRepository

SupabaseRepositoryFactory = Callable[[str, str, str | None], OperationsRepository]


def _default_supabase_factory(
    url: str,
    anon_key: str,
    service_role_key: str | None,
) -> OperationsRepository:
    return SupabaseRepository.from_credentials(
        url=url,
        anon_key=anon_key,
        service_role_key=service_role_key,
    )


def select_repository(
    settings: AppSettings,
    demo_data_directory: Path,
    *,
    supabase_factory: SupabaseRepositoryFactory | None = None,
) -> OperationsRepository:
    """Select local demo or Supabase live storage without silent fallback."""

    if settings.app_mode == AppMode.DEMO:
        return LocalJsonRepository(demo_data_directory)

    if settings.supabase_url is None or settings.supabase_anon_key is None:
        raise RepositoryConfigurationError(
            "Live mode requires SUPABASE_URL and SUPABASE_ANON_KEY."
        )

    service_role_key = (
        settings.supabase_service_role_key.get_secret_value()
        if settings.supabase_service_role_key is not None
        else None
    )
    factory = supabase_factory or _default_supabase_factory
    return factory(
        str(settings.supabase_url).rstrip("/"),
        settings.supabase_anon_key.get_secret_value(),
        service_role_key,
    )

