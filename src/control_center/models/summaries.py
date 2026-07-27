"""Read-only summary models and en-US presentation helpers."""

from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from control_center.models.alerts import Alert
from control_center.models.metrics import CalculatedMetrics
from control_center.models.workflows import WorkflowRun


def format_usd(value: Decimal | None) -> str:
    """Format money consistently using en-US separators."""

    return "N/A" if value is None else f"${value:,.2f}"


class OperationsSummary(BaseModel):
    """Validated aggregate that a future UI can consume without recalculation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metrics: CalculatedMetrics
    workflows: tuple[WorkflowRun, ...]
    alerts: tuple[Alert, ...]


class OverallStatus(StrEnum):
    """Allowed high-level narrative status labels."""

    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"


SummaryItem = Annotated[str, Field(min_length=1, max_length=180)]


class FounderSummary(BaseModel):
    """Strict narrative output allowed from a summary provider."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    overall_status: OverallStatus
    executive_summary: str = Field(min_length=1, max_length=600)
    key_findings: tuple[SummaryItem, ...] = Field(min_length=1, max_length=5)
    recommended_actions: tuple[SummaryItem, ...] = Field(
        min_length=1,
        max_length=5,
    )
    risks: tuple[SummaryItem, ...] = Field(min_length=1, max_length=5)


class SummaryStatus(StrEnum):
    """How the displayed founder summary was produced."""

    DEMO = "demo"
    LIVE = "live"
    FALLBACK = "fallback"


class SummaryGenerationResult(BaseModel):
    """Validated summary plus safe provider/fallback metadata for the UI."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: FounderSummary
    provider_used: str = Field(min_length=1)
    status: SummaryStatus
    fallback_reason: str | None = None

