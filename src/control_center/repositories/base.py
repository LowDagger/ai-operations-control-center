"""Repository contract for validated operations data."""

from typing import Protocol

from control_center.models.alerts import Alert
from control_center.models.persistence import (
    GeneratedSummaryRecord,
    MetricSnapshot,
)
from control_center.models.workflows import WorkflowRun


class OperationsRepository(Protocol):
    def save_metric_snapshot(self, snapshot: MetricSnapshot) -> MetricSnapshot: ...

    def get_metric_snapshots(self, limit: int = 100) -> list[MetricSnapshot]: ...

    def save_workflow_runs(
        self,
        workflows: list[WorkflowRun],
    ) -> list[WorkflowRun]: ...

    def get_workflow_runs(self, limit: int = 100) -> list[WorkflowRun]: ...

    def save_alerts(self, alerts: list[Alert]) -> list[Alert]: ...

    def get_alerts(self, limit: int = 100) -> list[Alert]: ...

    def save_generated_summary(
        self,
        summary: GeneratedSummaryRecord,
    ) -> GeneratedSummaryRecord: ...

    def get_generated_summaries(
        self,
        limit: int = 100,
    ) -> list[GeneratedSummaryRecord]: ...
