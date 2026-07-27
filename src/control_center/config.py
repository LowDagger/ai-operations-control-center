"""Central configuration for deterministic business rules."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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

