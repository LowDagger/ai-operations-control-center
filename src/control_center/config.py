"""Central configuration for deterministic business rules."""

import os
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class AppMode(StrEnum):
    """Supported application operating modes."""

    DEMO = "demo"
    LIVE = "live"


class AppSettings(BaseModel):
    """Validated runtime settings that do not require credentials."""

    model_config = ConfigDict(frozen=True)

    app_mode: AppMode = AppMode.DEMO
    gemini_api_key: SecretStr | None = Field(default=None, repr=False)
    gemini_model: str = Field(default="gemini-2.5-flash", min_length=1)

    @classmethod
    def from_environment(cls) -> "AppSettings":
        """Read the app mode from the environment with a safe demo default."""

        app_mode = os.environ.get("APP_MODE", AppMode.DEMO.value)
        api_key = os.environ.get("GEMINI_API_KEY", "").strip() or None
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
        return cls(
            app_mode=app_mode.strip().lower(),
            gemini_api_key=api_key,
            gemini_model=model,
        )


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
