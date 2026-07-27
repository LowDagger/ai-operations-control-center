from datetime import UTC, datetime
from decimal import Decimal

import pytest

from control_center.models.alerts import AlertType, Severity
from control_center.models.metrics import DTCInputData
from control_center.models.workflows import RetryStatus, WorkflowRun, WorkflowStatus
from control_center.services.alert_service import AlertService
from control_center.services.metric_service import calculate_metrics

NOW = datetime(2026, 1, 15, 12, tzinfo=UTC)


def _healthy_source(**changes: object) -> DTCInputData:
    values: dict[str, object] = {
        "revenue": Decimal("10000"),
        "ad_spend": Decimal("2500"),
        "new_customers": 100,
        "orders": 200,
        "sessions": 5000,
        "refunds": 2,
        "refunded_revenue": Decimal("100"),
        "impressions": 100000,
        "clicks": 4000,
        "creative_frequency": Decimal("2"),
        "previous_period_ad_spend": Decimal("2400"),
    }
    values.update(changes)
    return DTCInputData.model_validate(values)


def _workflow(**changes: object) -> WorkflowRun:
    values: dict[str, object] = {
        "workflow_name": "Demo Workflow",
        "status": WorkflowStatus.SUCCEEDED,
        "last_run": NOW,
        "failure_reason": None,
        "retry_status": RetryStatus.NOT_NEEDED,
        "cost_anomaly": Decimal("0"),
        "owner": "Operations",
        "severity": Severity.INFO,
    }
    values.update(changes)
    return WorkflowRun.model_validate(values)


def _alert_types(
    source: DTCInputData,
    workflows: list[WorkflowRun] | None = None,
) -> set[AlertType]:
    alerts = AlertService().evaluate(
        source,
        calculate_metrics(source),
        workflows or [],
        created_at=NOW,
    )
    return {alert.alert_type for alert in alerts}


@pytest.mark.parametrize(
    ("source", "expected_type"),
    [
        (_healthy_source(revenue=Decimal("4000")), AlertType.LOW_ROAS),
        (_healthy_source(new_customers=20), AlertType.HIGH_CAC),
        (_healthy_source(refunds=20), AlertType.HIGH_REFUND_RATE),
        (
            _healthy_source(creative_frequency=Decimal("4")),
            AlertType.CREATIVE_FATIGUE,
        ),
        (_healthy_source(impressions=None), AlertType.MISSING_DATA),
    ],
)
def test_each_metric_and_data_alert_rule(
    source: DTCInputData,
    expected_type: AlertType,
) -> None:
    assert expected_type in _alert_types(source)


def test_workflow_failure_rule() -> None:
    failed = _workflow(
        status=WorkflowStatus.FAILED,
        failure_reason="Fictional failure.",
        retry_status=RetryStatus.EXHAUSTED,
        severity=Severity.CRITICAL,
    )
    assert AlertType.WORKFLOW_FAILURE in _alert_types(_healthy_source(), [failed])


def test_cost_spike_rule() -> None:
    expensive = _workflow(cost_anomaly=Decimal("0.30"))
    assert AlertType.COST_SPIKE in _alert_types(_healthy_source(), [expensive])


def test_healthy_data_produces_no_alerts() -> None:
    assert _alert_types(_healthy_source(), [_workflow()]) == set()


def test_critical_boundaries_set_critical_severity() -> None:
    source = _healthy_source(
        revenue=Decimal("2000"),
        new_customers=10,
        refunds=30,
        creative_frequency=Decimal("6"),
    )
    alerts = AlertService().evaluate(
        source,
        calculate_metrics(source),
        [_workflow(cost_anomaly=Decimal("0.75"))],
        created_at=NOW,
    )
    severities = {alert.alert_type: alert.severity for alert in alerts}
    assert severities[AlertType.LOW_ROAS] == Severity.CRITICAL
    assert severities[AlertType.HIGH_CAC] == Severity.CRITICAL
    assert severities[AlertType.HIGH_REFUND_RATE] == Severity.CRITICAL
    assert severities[AlertType.CREATIVE_FATIGUE] == Severity.CRITICAL
    assert severities[AlertType.COST_SPIKE] == Severity.CRITICAL

