"""KPI presentation helpers and Streamlit rendering."""

from dataclasses import dataclass
from decimal import Decimal

import streamlit as st

from control_center.config import AppMode
from control_center.models.metrics import CalculatedMetrics
from control_center.models.summaries import format_usd


@dataclass(frozen=True)
class KpiCard:
    """Display-only data for one KPI card."""

    label: str
    value: str


def get_data_source_label(app_mode: AppMode) -> str:
    """Return the compact configured data-source indicator."""

    if app_mode == AppMode.DEMO:
        return "LOCAL DEMO DATA"
    return "SUPABASE LIVE DATA"


def format_number(value: Decimal | int | None, decimal_places: int = 2) -> str:
    """Format a number with en-US separators without changing its value."""

    if value is None:
        return "N/A"
    return f"{value:,.{decimal_places}f}"


def format_percentage(value: Decimal | None) -> str:
    """Format a decimal ratio as an en-US percentage."""

    if value is None:
        return "N/A"
    return f"{value * 100:,.2f}%"


def build_kpi_cards(metrics: CalculatedMetrics) -> tuple[KpiCard, ...]:
    """Map calculated metrics to display values without recalculation."""

    return (
        KpiCard("Revenue", format_usd(metrics.revenue)),
        KpiCard("Ad spend", format_usd(metrics.ad_spend)),
        KpiCard(
            "ROAS",
            "N/A" if metrics.roas is None else f"{format_number(metrics.roas)}x",
        ),
        KpiCard("CAC", format_usd(metrics.cac)),
        KpiCard("AOV", format_usd(metrics.aov)),
        KpiCard("CVR", format_percentage(metrics.cvr)),
        KpiCard(
            "Order volume",
            format_number(metrics.order_volume, decimal_places=0),
        ),
        KpiCard("Refund rate", format_percentage(metrics.refund_rate)),
    )


def render_kpis(metrics: CalculatedMetrics) -> None:
    """Render responsive, read-only KPI cards."""

    st.header("Business performance")
    cards = build_kpi_cards(metrics)
    if all(card.value == "N/A" for card in cards):
        st.info(
            "No metric data is available in the demo fixtures.",
            icon=":material/info:",
        )
        return

    for card_group in (cards[:4], cards[4:]):
        with st.container(horizontal=True):
            for card in card_group:
                st.metric(card.label, card.value, border=True)
