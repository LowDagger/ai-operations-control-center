from datetime import UTC, datetime
from decimal import Decimal

from control_center.config import AppMode
from control_center.models.alerts import Alert, AlertType, Severity
from control_center.models.metrics import CalculatedMetrics
from control_center.models.workflows import RetryStatus, WorkflowRun, WorkflowStatus
from control_center.ui.alerts import alert_rows, format_alert_value
from control_center.ui.dashboard import build_kpi_cards, get_data_source_label
from control_center.ui.workflows import workflow_rows

NOW = datetime(2026, 1, 15, 12, tzinfo=UTC)


def test_data_source_labels_are_configuration_driven() -> None:
    assert get_data_source_label(AppMode.DEMO) == "LOCAL DEMO DATA"
    assert get_data_source_label(AppMode.LIVE) == "SUPABASE LIVE DATA"


def test_kpi_helpers_use_en_us_display_formatting() -> None:
    metrics = CalculatedMetrics(
        roas=Decimal("1.5"),
        cac=Decimal("66.666"),
        aov=Decimal("60"),
        cvr=Decimal("0.02"),
        order_volume=200,
        refund_rate=Decimal("0.15"),
        revenue=Decimal("12000"),
        ad_spend=Decimal("8000"),
    )

    cards = {card.label: card.value for card in build_kpi_cards(metrics)}

    assert cards == {
        "Revenue": "$12,000.00",
        "Ad spend": "$8,000.00",
        "ROAS": "1.50x",
        "CAC": "$66.67",
        "AOV": "$60.00",
        "CVR": "2.00%",
        "Order volume": "200",
        "Refund rate": "15.00%",
    }


def test_workflow_rows_show_clear_status_and_empty_reason() -> None:
    workflow = WorkflowRun(
        workflow_name="Demo sync",
        status=WorkflowStatus.SUCCEEDED,
        last_run=NOW,
        failure_reason=None,
        retry_status=RetryStatus.NOT_NEEDED,
        cost_anomaly=Decimal("0.05"),
        owner="Operations",
        severity=Severity.INFO,
    )

    rows = workflow_rows([workflow])

    assert rows[0]["Status"] == "SUCCEEDED"
    assert rows[0]["Severity"] == "INFO"
    assert rows[0]["Cost anomaly"] == "5.00%"
    assert rows[0]["Failure reason"] == "—"


def test_alert_rows_format_money_percentages_and_severity() -> None:
    alert = Alert(
        alert_type=AlertType.HIGH_CAC,
        title="High CAC",
        message="CAC is high.",
        severity=Severity.WARNING,
        source="metrics.cac",
        current_value=Decimal("1234.5"),
        threshold=Decimal("50"),
        created_timestamp=NOW,
    )

    rows = alert_rows([alert])

    assert rows[0]["Severity"] == "WARNING"
    assert rows[0]["Current value"] == "$1,234.50"
    assert rows[0]["Threshold"] == "$50.00"
    assert (
        format_alert_value(AlertType.HIGH_REFUND_RATE, Decimal("0.15"))
        == "15.00%"
    )
