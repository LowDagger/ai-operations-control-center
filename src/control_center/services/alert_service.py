"""Explicit deterministic alert rules."""

from datetime import datetime
from decimal import Decimal

from pydantic import TypeAdapter

from control_center.config import AlertThresholds
from control_center.models.alerts import Alert, AlertType, Severity
from control_center.models.metrics import CalculatedMetrics, DTCInputData
from control_center.models.workflows import WorkflowRun, WorkflowStatus


class AlertService:
    """Evaluate configured rules in a stable order."""

    def __init__(self, thresholds: AlertThresholds | None = None) -> None:
        self.thresholds = thresholds or AlertThresholds()

    def evaluate(
        self,
        source: DTCInputData,
        metrics: CalculatedMetrics,
        workflows: list[WorkflowRun],
        *,
        created_at: datetime,
    ) -> list[Alert]:
        timestamp = TypeAdapter(datetime).validate_python(created_at)
        if timestamp.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        alerts: list[Alert] = []
        alerts.extend(self._metric_alerts(metrics, timestamp))
        alerts.extend(self._creative_alerts(source, timestamp))
        alerts.extend(self._workflow_alerts(workflows, timestamp))
        alerts.extend(self._missing_data_alerts(source, timestamp))
        return alerts

    def _metric_alerts(
        self,
        metrics: CalculatedMetrics,
        created_at: datetime,
    ) -> list[Alert]:
        alerts: list[Alert] = []
        if metrics.roas is not None and metrics.roas < self.thresholds.low_roas:
            severity = (
                Severity.CRITICAL
                if metrics.roas < self.thresholds.critical_roas
                else Severity.WARNING
            )
            alerts.append(
                self._alert(
                    AlertType.LOW_ROAS,
                    "Low ROAS",
                    "ROAS is below the configured minimum.",
                    severity,
                    "metrics.roas",
                    metrics.roas,
                    self.thresholds.low_roas,
                    created_at,
                )
            )
        if metrics.cac is not None and metrics.cac > self.thresholds.high_cac:
            severity = (
                Severity.CRITICAL
                if metrics.cac > self.thresholds.critical_cac
                else Severity.WARNING
            )
            alerts.append(
                self._alert(
                    AlertType.HIGH_CAC,
                    "High CAC",
                    "Customer acquisition cost exceeds the configured maximum.",
                    severity,
                    "metrics.cac",
                    metrics.cac,
                    self.thresholds.high_cac,
                    created_at,
                )
            )
        if (
            metrics.refund_rate is not None
            and metrics.refund_rate > self.thresholds.high_refund_rate
        ):
            severity = (
                Severity.CRITICAL
                if metrics.refund_rate > self.thresholds.critical_refund_rate
                else Severity.WARNING
            )
            alerts.append(
                self._alert(
                    AlertType.HIGH_REFUND_RATE,
                    "High refund rate",
                    "Refund rate exceeds the configured maximum.",
                    severity,
                    "metrics.refund_rate",
                    metrics.refund_rate,
                    self.thresholds.high_refund_rate,
                    created_at,
                )
            )
        return alerts

    def _creative_alerts(
        self,
        source: DTCInputData,
        created_at: datetime,
    ) -> list[Alert]:
        frequency = source.creative_frequency
        if frequency is None or frequency <= self.thresholds.creative_fatigue:
            return []
        severity = (
            Severity.CRITICAL
            if frequency > self.thresholds.critical_creative_fatigue
            else Severity.WARNING
        )
        return [
            self._alert(
                AlertType.CREATIVE_FATIGUE,
                "Creative fatigue",
                "Creative frequency exceeds the configured maximum.",
                severity,
                "metrics.creative_frequency",
                frequency,
                self.thresholds.creative_fatigue,
                created_at,
            )
        ]

    def _workflow_alerts(
        self,
        workflows: list[WorkflowRun],
        created_at: datetime,
    ) -> list[Alert]:
        alerts: list[Alert] = []
        for workflow in workflows:
            if workflow.status == WorkflowStatus.FAILED:
                alerts.append(
                    self._alert(
                        AlertType.WORKFLOW_FAILURE,
                        f"Workflow failed: {workflow.workflow_name}",
                        workflow.failure_reason or "Workflow failed without a reason.",
                        workflow.severity,
                        f"workflow.{workflow.workflow_name}",
                        workflow.status.value,
                        WorkflowStatus.SUCCEEDED.value,
                        created_at,
                    )
                )
            if (
                workflow.cost_anomaly is not None
                and workflow.cost_anomaly > self.thresholds.cost_spike
            ):
                severity = (
                    Severity.CRITICAL
                    if workflow.cost_anomaly > self.thresholds.critical_cost_spike
                    else Severity.WARNING
                )
                alerts.append(
                    self._alert(
                        AlertType.COST_SPIKE,
                        f"Cost spike: {workflow.workflow_name}",
                        "Workflow cost increase exceeds the configured maximum.",
                        severity,
                        f"workflow.{workflow.workflow_name}.cost",
                        workflow.cost_anomaly,
                        self.thresholds.cost_spike,
                        created_at,
                    )
                )
        return alerts

    def _missing_data_alerts(
        self,
        source: DTCInputData,
        created_at: datetime,
    ) -> list[Alert]:
        missing_fields = [
            field_name
            for field_name, value in source.model_dump().items()
            if value is None
        ]
        if not missing_fields:
            return []
        missing = ", ".join(sorted(missing_fields))
        return [
            self._alert(
                AlertType.MISSING_DATA,
                "Missing source data",
                f"Required source fields are missing: {missing}.",
                Severity.WARNING,
                "dtc_input",
                missing,
                "all fields present",
                created_at,
            )
        ]

    @staticmethod
    def _alert(
        alert_type: AlertType,
        title: str,
        message: str,
        severity: Severity,
        source: str,
        current_value: Decimal | str | None,
        threshold: Decimal | str | None,
        created_at: datetime,
    ) -> Alert:
        return Alert(
            alert_type=alert_type,
            title=title,
            message=message,
            severity=severity,
            source=source,
            current_value=current_value,
            threshold=threshold,
            created_timestamp=created_at,
        )

