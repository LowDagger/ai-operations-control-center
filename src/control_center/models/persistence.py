"""Persistence envelopes composed from existing domain models."""

from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict

from control_center.models.metrics import CalculatedMetrics, DTCInputData
from control_center.models.summaries import SummaryGenerationResult


class MetricSnapshot(BaseModel):
    """One persisted input snapshot and its deterministic calculated metrics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID | None = None
    created_at: AwareDatetime
    source: DTCInputData
    metrics: CalculatedMetrics


class GeneratedSummaryRecord(BaseModel):
    """One persisted founder summary with generation metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID | None = None
    created_at: AwareDatetime
    result: SummaryGenerationResult

