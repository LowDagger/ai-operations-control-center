from decimal import Decimal

from control_center.models.metrics import DTCInputData
from control_center.models.summaries import format_usd
from control_center.services.metric_service import calculate_metrics


def test_every_metric_formula() -> None:
    source = DTCInputData(
        revenue=Decimal("1000"),
        ad_spend=Decimal("250"),
        new_customers=10,
        orders=20,
        sessions=500,
        refunds=2,
        refunded_revenue=Decimal("100"),
        impressions=10000,
        clicks=600,
        creative_frequency=Decimal("2"),
        previous_period_ad_spend=Decimal("200"),
    )

    metrics = calculate_metrics(source)

    assert metrics.roas == Decimal("4")
    assert metrics.cac == Decimal("25")
    assert metrics.aov == Decimal("50")
    assert metrics.cvr == Decimal("0.04")
    assert metrics.order_volume == 20
    assert metrics.refund_rate == Decimal("0.1")
    assert metrics.revenue == Decimal("1000")
    assert metrics.ad_spend == Decimal("250")


def test_division_by_zero_returns_none() -> None:
    source = DTCInputData(
        revenue=Decimal("0"),
        ad_spend=Decimal("0"),
        new_customers=0,
        orders=0,
        sessions=0,
        refunds=0,
    )

    metrics = calculate_metrics(source)

    assert metrics.roas is None
    assert metrics.cac is None
    assert metrics.aov is None
    assert metrics.cvr is None
    assert metrics.refund_rate is None
    assert metrics.order_volume == 0


def test_money_uses_en_us_formatting() -> None:
    assert format_usd(Decimal("1234567.8")) == "$1,234,567.80"
    assert format_usd(None) == "N/A"

