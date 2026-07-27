"""Pure deterministic metric calculations."""

from decimal import Decimal

from control_center.models.metrics import CalculatedMetrics, DTCInputData


def _safe_divide(
    numerator: Decimal | int | None,
    denominator: Decimal | int | None,
) -> Decimal | None:
    if numerator is None or denominator in (None, 0):
        return None
    return Decimal(numerator) / Decimal(denominator)


def calculate_metrics(source: DTCInputData) -> CalculatedMetrics:
    """Calculate DTC metrics without inference, I/O, or side effects."""

    return CalculatedMetrics(
        roas=_safe_divide(source.revenue, source.ad_spend),
        cac=_safe_divide(source.ad_spend, source.new_customers),
        aov=_safe_divide(source.revenue, source.orders),
        cvr=_safe_divide(source.orders, source.sessions),
        order_volume=source.orders,
        refund_rate=_safe_divide(source.refunds, source.orders),
        revenue=source.revenue,
        ad_spend=source.ad_spend,
    )

