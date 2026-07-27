"""Alert table presentation helpers and Streamlit rendering."""

from datetime import UTC
from decimal import Decimal

import streamlit as st

from control_center.models.alerts import Alert, AlertType, Severity
from control_center.models.summaries import format_usd

PERCENTAGE_ALERTS = {
    AlertType.HIGH_REFUND_RATE,
    AlertType.COST_SPIKE,
}


def format_alert_value(
    alert_type: AlertType,
    value: Decimal | str | None,
) -> str:
    """Format an alert value according to its display semantics."""

    if value is None:
        return "N/A"
    if isinstance(value, str):
        return value
    if alert_type == AlertType.HIGH_CAC:
        return format_usd(value)
    if alert_type in PERCENTAGE_ALERTS:
        return f"{value * 100:,.2f}%"
    if alert_type == AlertType.LOW_ROAS:
        return f"{value:,.2f}x"
    return f"{value:,.2f}"


def alert_rows(alerts: list[Alert]) -> list[dict[str, str]]:
    """Convert alerts to read-only table rows."""

    return [
        {
            "Severity": alert.severity.value.upper(),
            "Alert": alert.title,
            "Message": alert.message,
            "Current value": format_alert_value(
                alert.alert_type,
                alert.current_value,
            ),
            "Threshold": format_alert_value(
                alert.alert_type,
                alert.threshold,
            ),
            "Source": alert.source,
            "Created": alert.created_timestamp.astimezone(UTC).strftime(
                "%b %d, %Y %H:%M UTC"
            ),
        }
        for alert in alerts
    ]


def render_alerts(alerts: list[Alert]) -> None:
    """Render active alerts with prominent deterministic severity labels."""

    st.header("Active alerts")
    rows = alert_rows(alerts)
    if not rows:
        st.success(
            "No active alerts were produced by the deterministic rules.",
            icon=":material/check_circle:",
        )
        return

    severity_counts = {
        severity: sum(alert.severity == severity for alert in alerts)
        for severity in (Severity.CRITICAL, Severity.WARNING, Severity.INFO)
    }
    with st.container(horizontal=True):
        st.badge(
            f"{severity_counts[Severity.CRITICAL]} critical",
            icon=":material/error:",
            color="red",
        )
        st.badge(
            f"{severity_counts[Severity.WARNING]} warning",
            icon=":material/warning:",
            color="orange",
        )

    st.dataframe(
        rows,
        hide_index=True,
        column_config={
            "Severity": st.column_config.TextColumn("Severity", pinned=True),
            "Alert": st.column_config.TextColumn("Alert"),
            "Message": st.column_config.TextColumn("Message"),
            "Current value": st.column_config.TextColumn("Current value"),
            "Threshold": st.column_config.TextColumn("Threshold"),
            "Source": st.column_config.TextColumn("Source"),
            "Created": st.column_config.TextColumn("Created"),
        },
    )
