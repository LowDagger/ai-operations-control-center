import socket
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

from control_center.config import AppMode, AppSettings
from control_center.models.metrics import CalculatedMetrics
from control_center.models.summaries import (
    FounderSummary,
    OperationsSummary,
    OverallStatus,
    SummaryStatus,
)
from control_center.providers.claude_stub import ClaudeSummaryProviderStub
from control_center.providers.gemini import GeminiSummaryProvider
from control_center.services.summary_service import SummaryService

NOW = datetime(2026, 1, 15, 12, tzinfo=UTC)

VALID_SUMMARY = FounderSummary(
    overall_status=OverallStatus.ATTENTION,
    executive_summary="Revenue is stable, with deterministic alerts to review.",
    key_findings=("ROAS is below its configured threshold.",),
    recommended_actions=("Review the existing alerts with their owners.",),
    risks=("Unresolved alerts may affect performance.",),
)


def _operations() -> OperationsSummary:
    return OperationsSummary(
        metrics=CalculatedMetrics(
            roas=Decimal("1.5"),
            cac=Decimal("40"),
            aov=Decimal("60"),
            cvr=Decimal("0.02"),
            order_volume=200,
            refund_rate=Decimal("0.01"),
            revenue=Decimal("12000"),
            ad_spend=Decimal("8000"),
        ),
        workflows=(),
        alerts=(),
    )


class FakeModels:
    def __init__(
        self,
        *,
        response_text: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response_text = response_text
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self, models: FakeModels) -> None:
        self.models = models


def _gemini_provider(models: FakeModels) -> GeminiSummaryProvider:
    return GeminiSummaryProvider(
        api_key="test-key",
        model="gemini-test",
        client=FakeClient(models),
    )


def test_valid_gemini_structured_response_is_revalidated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("real network access attempted")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(socket.socket, "connect", fail_network)
    models = FakeModels(response_text=VALID_SUMMARY.model_dump_json())

    summary = _gemini_provider(models).generate_summary(_operations())

    assert summary == VALID_SUMMARY
    assert models.calls[0]["config"]["response_mime_type"] == "application/json"
    assert models.calls[0]["config"]["response_schema"] is FounderSummary
    prompt = models.calls[0]["contents"]
    assert "Do not recalculate metrics" in prompt
    assert "create or modify alerts" in prompt
    assert "decide retries" in prompt
    assert "make approvals" in prompt


def test_invalid_gemini_structured_response_is_rejected() -> None:
    models = FakeModels(
        response_text='{"overall_status": "unknown", "executive_summary": "Bad"}'
    )

    with pytest.raises(ValidationError):
        _gemini_provider(models).generate_summary(_operations())


def test_valid_live_summary_reports_gemini_provider() -> None:
    provider = _gemini_provider(
        FakeModels(response_text=VALID_SUMMARY.model_dump_json())
    )
    result = SummaryService(
        live_provider_factory=lambda api_key, model: provider
    ).generate(
        _operations(),
        AppSettings(app_mode=AppMode.LIVE, gemini_api_key="test-key"),
    )

    assert result.status == SummaryStatus.LIVE
    assert result.provider_used == "Gemini"
    assert result.summary == VALID_SUMMARY
    assert result.fallback_reason is None


def test_invalid_gemini_response_uses_automatic_fallback() -> None:
    provider = _gemini_provider(FakeModels(response_text='{"invalid": true}'))
    result = SummaryService(
        live_provider_factory=lambda api_key, model: provider
    ).generate(
        _operations(),
        AppSettings(app_mode=AppMode.LIVE, gemini_api_key="test-key"),
    )

    assert result.status == SummaryStatus.FALLBACK
    assert result.fallback_reason == "Gemini returned invalid structured output."
    assert result.provider_used == "Deterministic demo"


def test_timeout_uses_automatic_deterministic_fallback() -> None:
    provider = _gemini_provider(FakeModels(error=TimeoutError("private detail")))
    service = SummaryService(
        live_provider_factory=lambda api_key, model: provider
    )
    settings = AppSettings(
        app_mode=AppMode.LIVE,
        gemini_api_key="test-key",
    )

    result = service.generate(_operations(), settings)

    assert result.status == SummaryStatus.FALLBACK
    assert result.provider_used == "Deterministic demo"
    assert result.fallback_reason == "Gemini summary generation timed out."


def test_live_mode_without_api_key_uses_fallback() -> None:
    def fail_factory(api_key: str, model: str) -> GeminiSummaryProvider:
        raise AssertionError("live provider should not be created")

    result = SummaryService(live_provider_factory=fail_factory).generate(
        _operations(),
        AppSettings(app_mode=AppMode.LIVE),
    )

    assert result.status == SummaryStatus.FALLBACK
    assert result.fallback_reason == "Gemini API key is not configured."


def test_demo_mode_never_creates_live_provider() -> None:
    def fail_factory(api_key: str, model: str) -> GeminiSummaryProvider:
        raise AssertionError("live provider should not be created")

    result = SummaryService(live_provider_factory=fail_factory).generate(
        _operations(),
        AppSettings(app_mode=AppMode.DEMO),
    )

    assert result.status == SummaryStatus.DEMO
    assert result.provider_used == "Deterministic demo"
    assert result.summary.overall_status == OverallStatus.HEALTHY


def test_provider_failure_falls_back_without_logging_secret(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "never-log-this-key"

    def fail_factory(api_key: str, model: str) -> GeminiSummaryProvider:
        assert api_key == secret
        raise RuntimeError(f"provider unavailable for {secret}")

    result = SummaryService(live_provider_factory=fail_factory).generate(
        _operations(),
        AppSettings(app_mode=AppMode.LIVE, gemini_api_key=secret),
    )

    assert result.status == SummaryStatus.FALLBACK
    assert result.fallback_reason == "Gemini summary generation is unavailable."
    assert secret not in caplog.text


def test_founder_summary_pydantic_validation_rejects_invalid_shape() -> None:
    with pytest.raises(ValidationError):
        FounderSummary.model_validate(
            {
                "overall_status": "healthy",
                "executive_summary": "",
                "key_findings": [],
                "recommended_actions": [],
                "risks": [],
                "unexpected": "not allowed",
            }
        )


def test_claude_stub_is_not_required() -> None:
    with pytest.raises(NotImplementedError, match="not required"):
        ClaudeSummaryProviderStub().generate_summary(_operations())
