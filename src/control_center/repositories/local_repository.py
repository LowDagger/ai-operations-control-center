"""Offline JSON repository with Pydantic validation at the boundary."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from control_center.models.alerts import Alert
from control_center.models.metrics import DTCInputData
from control_center.models.workflows import WorkflowRun


class LocalJsonRepository:
    """Load local fixtures only; this class has no network behavior."""

    def __init__(self, data_directory: Path) -> None:
        self.data_directory = data_directory

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

    def _load_json(self, filename: str) -> Any:
        fixture_path = self.data_directory / filename
        with fixture_path.open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file, parse_float=Decimal)
