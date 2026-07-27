"""Deterministic offline founder-summary provider."""

from control_center.models.alerts import AlertType, Severity
from control_center.models.summaries import (
    FounderSummary,
    OperationsSummary,
    OverallStatus,
)
from control_center.models.workflows import WorkflowStatus


class DemoSummaryProvider:
    """Build a stable narrative from existing deterministic results."""

    provider_name = "Deterministic demo"

    def generate_summary(self, operations: OperationsSummary) -> FounderSummary:
        critical_alerts = [
            alert
            for alert in operations.alerts
            if alert.severity == Severity.CRITICAL
        ]
        warning_alerts = [
            alert
            for alert in operations.alerts
            if alert.severity == Severity.WARNING
        ]
        failed_workflows = [
            workflow
            for workflow in operations.workflows
            if workflow.status == WorkflowStatus.FAILED
        ]

        if critical_alerts:
            overall_status = OverallStatus.CRITICAL
        elif warning_alerts:
            overall_status = OverallStatus.ATTENTION
        else:
            overall_status = OverallStatus.HEALTHY

        prioritized_alerts = critical_alerts + warning_alerts
        key_findings = tuple(
            alert.title for alert in prioritized_alerts[:3]
        ) or ("No deterministic alerts are active.",)

        actions = ["Review the deterministic alerts with their named owners."]
        if failed_workflows:
            actions.append(
                "Investigate failed workflows before any human retry decision."
            )
        if any(
            alert.alert_type == AlertType.MISSING_DATA
            for alert in operations.alerts
        ):
            actions.append("Restore the missing source fields and rerun validation.")

        risks = tuple(
            alert.message for alert in prioritized_alerts[:3]
        ) or ("No material risks are present in the current fictional snapshot.",)

        return FounderSummary(
            overall_status=overall_status,
            executive_summary=(
                "The fictional snapshot contains "
                f"{len(critical_alerts)} critical and "
                f"{len(warning_alerts)} warning alerts across "
                f"{len(operations.workflows)} monitored workflows."
            ),
            key_findings=key_findings,
            recommended_actions=tuple(actions),
            risks=risks,
        )

