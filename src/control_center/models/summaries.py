"""Read-only summary models and en-US presentation helpers."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

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

