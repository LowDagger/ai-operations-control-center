"""Alert models shared by deterministic rules and repositories."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(StrEnum):
    LOW_ROAS = "low_roas"
    HIGH_CAC = "high_cac"
    HIGH_REFUND_RATE = "high_refund_rate"
    CREATIVE_FATIGUE = "creative_fatigue"
    WORKFLOW_FAILURE = "workflow_failure"
    COST_SPIKE = "cost_spike"
    MISSING_DATA = "missing_data"


class Alert(BaseModel):
    """A deterministic alert emitted from an explicit business rule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    alert_type: AlertType
    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: Severity
    source: str = Field(min_length=1)
    current_value: Decimal | str | None
    threshold: Decimal | str | None
    created_timestamp: AwareDatetime

