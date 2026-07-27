"""Central configuration for deterministic business rules."""

import os
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AppMode(StrEnum):
    """Supported application operating modes."""

    DEMO = "demo"
    LIVE = "live"


class AppSettings(BaseModel):
    """Validated runtime settings that do not require credentials."""

    model_config = ConfigDict(frozen=True)

    app_mode: AppMode = AppMode.DEMO

    @classmethod
    def from_environment(cls) -> "AppSettings":
        """Read the app mode from the environment with a safe demo default."""

        app_mode = os.environ.get("APP_MODE", AppMode.DEMO.value)
        return cls(app_mode=app_mode.strip().lower())


class AlertThresholds(BaseModel):
    """All alert thresholds, expressed as ratios or USD values.

    Ratios use decimal notation: ``0.05`` means 5%. Warning thresholds trigger
    when a metric crosses the configured boundary; critical thresholds determine
    severity for the same rule.
    """

    model_config = ConfigDict(frozen=True)

    low_roas: Decimal = Field(default=Decimal("2.00"), gt=0)
    critical_roas: Decimal = Field(default=Decimal("1.00"), gt=0)
    high_cac: Decimal = Field(default=Decimal("50.00"), ge=0)
    critical_cac: Decimal = Field(default=Decimal("100.00"), ge=0)
    high_refund_rate: Decimal = Field(default=Decimal("0.05"), ge=0, le=1)
    critical_refund_rate: Decimal = Field(default=Decimal("0.10"), ge=0, le=1)
    creative_fatigue: Decimal = Field(default=Decimal("3.00"), ge=0)
    critical_creative_fatigue: Decimal = Field(default=Decimal("5.00"), ge=0)
    cost_spike: Decimal = Field(default=Decimal("0.25"), ge=0)
    critical_cost_spike: Decimal = Field(default=Decimal("0.50"), ge=0)
