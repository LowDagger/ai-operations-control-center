"""Repository contract for validated operations data."""

from typing import Protocol

from control_center.models.alerts import Alert
from control_center.models.metrics import DTCInputData
from control_center.models.workflows import WorkflowRun


class OperationsRepository(Protocol):
    def load_metrics(self) -> DTCInputData: ...

    def load_workflow_runs(self) -> list[WorkflowRun]: ...

    def load_expected_alerts(self) -> list[Alert]: ...

