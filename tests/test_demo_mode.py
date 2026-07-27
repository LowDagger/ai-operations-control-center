import json
import socket
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from control_center.models.alerts import AlertType, Severity
from control_center.repositories.local_repository import LocalJsonRepository
from control_center.services.alert_service import AlertService
from control_center.services.metric_service import calculate_metrics

PROJECT_ROOT = Path(__file__).parents[1]
DEMO_DIRECTORY = PROJECT_ROOT / "data" / "demo"
DEMO_TIMESTAMP = datetime(2026, 1, 15, 12, tzinfo=UTC)


def test_demo_fixture_output_is_deterministic() -> None:
    repository = LocalJsonRepository(DEMO_DIRECTORY)
    source = repository.load_metrics()
    workflows = repository.load_workflow_runs()
    expected_alerts = repository.load_expected_alerts()

    actual_alerts = AlertService().evaluate(
        source,
        calculate_metrics(source),
        workflows,
        created_at=DEMO_TIMESTAMP,
    )

    assert actual_alerts == expected_alerts
    assert calculate_metrics(source).cvr is not None
    assert any(alert.severity == Severity.WARNING for alert in actual_alerts)
    assert any(alert.severity == Severity.CRITICAL for alert in actual_alerts)
    assert any(
        alert.alert_type == AlertType.WORKFLOW_FAILURE for alert in actual_alerts
    )
    assert any(alert.alert_type == AlertType.MISSING_DATA for alert in actual_alerts)


def test_invalid_fixture_data_is_rejected(tmp_path: Path) -> None:
    invalid_directory = tmp_path / "invalid"
    invalid_directory.mkdir()
    (invalid_directory / "metrics.json").write_text(
        json.dumps({"revenue": -1}),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        LocalJsonRepository(invalid_directory).load_metrics()


def test_demo_mode_needs_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(socket.socket, "connect", fail_network)

    repository = LocalJsonRepository(DEMO_DIRECTORY)
    source = repository.load_metrics()
    workflows = repository.load_workflow_runs()
    alerts = AlertService().evaluate(
        source,
        calculate_metrics(source),
        workflows,
        created_at=DEMO_TIMESTAMP,
    )

    assert alerts

