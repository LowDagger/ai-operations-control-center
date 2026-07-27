"""DTC source data and deterministic calculated metrics."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DTCInputData(BaseModel):
    """Validated DTC inputs.

    ``None`` represents a source field that was not delivered. Negative values
    and unexpected fields are rejected.
    """

    model_config = ConfigDict(extra="forbid")

    revenue: Decimal | None = Field(default=None, ge=0)
    ad_spend: Decimal | None = Field(default=None, ge=0)
    new_customers: int | None = Field(default=None, ge=0)
    orders: int | None = Field(default=None, ge=0)
    sessions: int | None = Field(default=None, ge=0)
    refunds: int | None = Field(default=None, ge=0)
    refunded_revenue: Decimal | None = Field(default=None, ge=0)
    impressions: int | None = Field(default=None, ge=0)
    clicks: int | None = Field(default=None, ge=0)
    creative_frequency: Decimal | None = Field(default=None, ge=0)
    previous_period_ad_spend: Decimal | None = Field(default=None, ge=0)


class CalculatedMetrics(BaseModel):
    """Metrics produced only by deterministic service code."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    roas: Decimal | None
    cac: Decimal | None
    aov: Decimal | None
    cvr: Decimal | None
    order_volume: int | None = Field(ge=0)
    refund_rate: Decimal | None = Field(ge=0)
    revenue: Decimal | None = Field(ge=0)
    ad_spend: Decimal | None = Field(ge=0)

