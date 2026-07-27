"""Workflow execution models."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from control_center.models.alerts import Severity


class WorkflowStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RUNNING = "running"


class RetryStatus(StrEnum):
    NOT_NEEDED = "not_needed"
    PENDING = "pending"
    EXHAUSTED = "exhausted"
    SUCCEEDED = "succeeded"


class WorkflowRun(BaseModel):
    """One validated workflow execution."""

    model_config = ConfigDict(extra="forbid")

    workflow_name: str = Field(min_length=1)
    status: WorkflowStatus
    last_run: AwareDatetime
    failure_reason: str | None = None
    retry_status: RetryStatus
    cost_anomaly: Decimal | None = Field(default=None, ge=0)
    owner: str = Field(min_length=1)
    severity: Severity

