"""Safe provider selection and deterministic summary fallback."""

import logging
from collections.abc import Callable

from pydantic import ValidationError

from control_center.config import AppMode, AppSettings
from control_center.models.summaries import (
    FounderSummary,
    OperationsSummary,
    SummaryGenerationResult,
    SummaryStatus,
)
from control_center.providers.base import SummaryProvider
from control_center.providers.demo import DemoSummaryProvider
from control_center.providers.gemini import GeminiSummaryProvider

LOGGER = logging.getLogger(__name__)

LiveProviderFactory = Callable[[str, str], SummaryProvider]


def _default_live_provider(api_key: str, model: str) -> SummaryProvider:
    return GeminiSummaryProvider(api_key=api_key, model=model)


class SummaryService:
    """Generate a narrative while preserving deterministic authority."""

    def __init__(
        self,
        *,
        demo_provider: SummaryProvider | None = None,
        live_provider_factory: LiveProviderFactory | None = None,
    ) -> None:
        self._demo_provider = demo_provider or DemoSummaryProvider()
        self._live_provider_factory = (
            live_provider_factory or _default_live_provider
        )

    def generate(
        self,
        operations: OperationsSummary,
        settings: AppSettings,
    ) -> SummaryGenerationResult:
        """Select live Gemini only when explicitly enabled and configured."""

        if settings.app_mode == AppMode.DEMO:
            return self._demo_result(operations, SummaryStatus.DEMO)

        if settings.gemini_api_key is None:
            LOGGER.warning(
                "Gemini live mode has no API key; using deterministic fallback."
            )
            return self._demo_result(
                operations,
                SummaryStatus.FALLBACK,
                "Gemini API key is not configured.",
            )

        provider: SummaryProvider | None = None
        try:
            provider = self._live_provider_factory(
                settings.gemini_api_key.get_secret_value(),
                settings.gemini_model,
            )
            generated = provider.generate_summary(operations)
            validated = FounderSummary.model_validate(generated.model_dump())
        except Exception as error:
            reason = self._safe_failure_reason(error)
            LOGGER.warning(
                "Summary provider %s failed with %s; using deterministic fallback.",
                getattr(provider, "provider_name", "Gemini"),
                type(error).__name__,
            )
            return self._demo_result(
                operations,
                SummaryStatus.FALLBACK,
                reason,
            )

        return SummaryGenerationResult(
            summary=validated,
            provider_used=provider.provider_name,
            status=SummaryStatus.LIVE,
        )

    def _demo_result(
        self,
        operations: OperationsSummary,
        status: SummaryStatus,
        fallback_reason: str | None = None,
    ) -> SummaryGenerationResult:
        summary = self._demo_provider.generate_summary(operations)
        return SummaryGenerationResult(
            summary=summary,
            provider_used=self._demo_provider.provider_name,
            status=status,
            fallback_reason=fallback_reason,
        )

    @staticmethod
    def _safe_failure_reason(error: Exception) -> str:
        if isinstance(error, ValidationError):
            return "Gemini returned invalid structured output."
        if (
            isinstance(error, TimeoutError)
            or "timeout" in type(error).__name__.lower()
        ):
            return "Gemini summary generation timed out."
        return "Gemini summary generation is unavailable."
