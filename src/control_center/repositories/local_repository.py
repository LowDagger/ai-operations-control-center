"""Offline JSON repository with Pydantic validation at the boundary."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from control_center.models.alerts import Alert
from control_center.models.metrics import DTCInputData
from control_center.models.persistence import (
    GeneratedSummaryRecord,
    MetricSnapshot,
)
from control_center.models.workflows import WorkflowRun


class LocalJsonRepository:
    """Load local fixtures only; this class has no network behavior."""

    def __init__(self, data_directory: Path) -> None:
        self.data_directory = data_directory
        self._metric_snapshots: list[MetricSnapshot] = []
        self._saved_workflows: list[WorkflowRun] = []
        self._saved_alerts: list[Alert] = []
        self._saved_summaries: list[GeneratedSummaryRecord] = []

    def load_metrics(self) -> DTCInputData:
        return DTCInputData.model_validate(self._load_json("metrics.json"))

    def load_workflow_runs(self) -> list[WorkflowRun]:
        return TypeAdapter(list[WorkflowRun]).validate_python(
            self._load_json("workflow_runs.json")
        )

    def load_expected_alerts(self) -> list[Alert]:
        return TypeAdapter(list[Alert]).validate_python(
            self._load_json("expected_alerts.json")
        )

    def save_metric_snapshot(self, snapshot: MetricSnapshot) -> MetricSnapshot:
        validated = MetricSnapshot.model_validate(snapshot.model_dump())
        self._metric_snapshots.append(validated)
        return validated

    def get_metric_snapshots(self, limit: int = 100) -> list[MetricSnapshot]:
        return list(reversed(self._metric_snapshots[-_validated_limit(limit) :]))

    def save_workflow_runs(
        self,
        workflows: list[WorkflowRun],
    ) -> list[WorkflowRun]:
        validated = TypeAdapter(list[WorkflowRun]).validate_python(workflows)
        self._saved_workflows.extend(validated)
        return validated

    def get_workflow_runs(self, limit: int = 100) -> list[WorkflowRun]:
        limit = _validated_limit(limit)
        source = self._saved_workflows or self.load_workflow_runs()
        return list(reversed(source[-limit:]))

    def save_alerts(self, alerts: list[Alert]) -> list[Alert]:
        validated = TypeAdapter(list[Alert]).validate_python(alerts)
        self._saved_alerts.extend(validated)
        return validated

    def get_alerts(self, limit: int = 100) -> list[Alert]:
        limit = _validated_limit(limit)
        source = self._saved_alerts or self.load_expected_alerts()
        return list(reversed(source[-limit:]))

    def save_generated_summary(
        self,
        summary: GeneratedSummaryRecord,
    ) -> GeneratedSummaryRecord:
        validated = GeneratedSummaryRecord.model_validate(summary.model_dump())
        self._saved_summaries.append(validated)
        return validated

    def get_generated_summaries(
        self,
        limit: int = 100,
    ) -> list[GeneratedSummaryRecord]:
        return list(reversed(self._saved_summaries[-_validated_limit(limit) :]))

    def _load_json(self, filename: str) -> Any:
        fixture_path = self.data_directory / filename
        with fixture_path.open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file, parse_float=Decimal)


def _validated_limit(limit: int) -> int:
    if limit <= 0:
        raise ValueError("Repository limit must be positive.")
    return limit
