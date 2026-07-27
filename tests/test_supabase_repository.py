import socket
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

from control_center.models.alerts import Alert, AlertType, Severity
from control_center.models.metrics import CalculatedMetrics, DTCInputData
from control_center.models.persistence import (
    GeneratedSummaryRecord,
    MetricSnapshot,
)
from control_center.models.summaries import (
    FounderSummary,
    OverallStatus,
    SummaryGenerationResult,
    SummaryStatus,
)
from control_center.models.workflows import RetryStatus, WorkflowRun, WorkflowStatus
from control_center.repositories.exceptions import (
    RepositoryConfigurationError,
    RepositoryUnavailableError,
)
from control_center.repositories.mappers import (
    alert_to_row,
    generated_summary_to_row,
    metric_snapshot_to_row,
    workflow_run_to_row,
)
from control_center.repositories.supabase_repository import SupabaseRepository

NOW = datetime(2026, 1, 15, 12, tzinfo=UTC)
ROW_ID = "12345678-1234-5678-1234-567812345678"


class FakeQuery:
    def __init__(self, client: "FakeClient", table: str) -> None:
        self.client = client
        self.table = table
        self.operation = ""
        self.payload: Any = None
        self.query_limit: int | None = None

    def select(self, columns: str) -> "FakeQuery":
        self.operation = "select"
        return self

    def insert(self, payload: Any) -> "FakeQuery":
        self.operation = "insert"
        self.payload = payload
        return self

    def order(self, column: str, *, desc: bool) -> "FakeQuery":
        return self

    def limit(self, limit: int) -> "FakeQuery":
        self.query_limit = limit
        return self

    def execute(self) -> SimpleNamespace:
        if self.client.error is not None:
            raise self.client.error
        self.client.calls.append(
            {
                "table": self.table,
                "operation": self.operation,
                "payload": self.payload,
                "limit": self.query_limit,
            }
        )
        if self.operation == "select":
            return SimpleNamespace(data=self.client.rows.get(self.table, []))

        payloads = self.payload if isinstance(self.payload, list) else [self.payload]
        rows = [
            {
                **payload,
                "id": ROW_ID,
                "created_at": payload.get("created_at", NOW.isoformat()),
            }
            for payload in payloads
        ]
        return SimpleNamespace(data=rows)


class FakeClient:
    def __init__(
        self,
        rows: dict[str, list[dict[str, Any]]] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.rows = rows or {}
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def table(self, table: str) -> FakeQuery:
        return FakeQuery(self, table)


def _metric_snapshot() -> MetricSnapshot:
    return MetricSnapshot(
        created_at=NOW,
        source=DTCInputData(
            revenue=Decimal("12000.10"),
            ad_spend=Decimal("8000.20"),
            new_customers=120,
            orders=200,
            sessions=10000,
            refunds=30,
            refunded_revenue=Decimal("1800.30"),
            impressions=100000,
            clicks=400,
            creative_frequency=Decimal("6.25"),
            previous_period_ad_spend=Decimal("4000.40"),
        ),
        metrics=CalculatedMetrics(
            roas=Decimal("1.499975000624984375"),
            cac=Decimal("66.668333333333333333"),
            aov=Decimal("60.0005"),
            cvr=Decimal("0.02"),
            order_volume=200,
            refund_rate=Decimal("0.15"),
            revenue=Decimal("12000.10"),
            ad_spend=Decimal("8000.20"),
        ),
    )


def _workflow() -> WorkflowRun:
    return WorkflowRun(
        workflow_name="Revenue sync",
        status=WorkflowStatus.SUCCEEDED,
        last_run=NOW,
        failure_reason=None,
        retry_status=RetryStatus.NOT_NEEDED,
        cost_anomaly=Decimal("0.05"),
        owner="Operations",
        severity=Severity.INFO,
    )


def _alert() -> Alert:
    return Alert(
        alert_type=AlertType.HIGH_CAC,
        title="High CAC",
        message="CAC exceeds the deterministic threshold.",
        severity=Severity.WARNING,
        source="metrics.cac",
        current_value=Decimal("66.668333333333333333"),
        threshold=Decimal("50.00"),
        created_timestamp=NOW,
    )


def _summary_record() -> GeneratedSummaryRecord:
    return GeneratedSummaryRecord(
        created_at=NOW,
        result=SummaryGenerationResult(
            summary=FounderSummary(
                overall_status=OverallStatus.ATTENTION,
                executive_summary="The fictional snapshot needs review.",
                key_findings=("CAC is above its deterministic threshold.",),
                recommended_actions=("Review the alert with its owner.",),
                risks=("Acquisition efficiency may remain weak.",),
            ),
            provider_used="Gemini",
            status=SummaryStatus.LIVE,
        ),
    )


def _row_with_id(row: dict[str, Any]) -> dict[str, Any]:
    return {**row, "id": ROW_ID}


def test_successful_inserts_use_service_role_and_safe_serialization() -> None:
    read_client = FakeClient()
    write_client = FakeClient()
    repository = SupabaseRepository(
        read_client=read_client,
        write_client=write_client,
    )

    saved_metric = repository.save_metric_snapshot(_metric_snapshot())
    saved_workflows = repository.save_workflow_runs([_workflow()])
    saved_alerts = repository.save_alerts([_alert()])
    saved_summary = repository.save_generated_summary(_summary_record())

    assert saved_metric.id == UUID(ROW_ID)
    assert saved_workflows == [_workflow()]
    assert saved_alerts == [_alert()]
    assert saved_summary.id == UUID(ROW_ID)
    assert read_client.calls == []
    assert [call["table"] for call in write_client.calls] == [
        "metrics_snapshots",
        "workflow_runs",
        "alerts",
        "generated_summaries",
    ]

    metric_payload = write_client.calls[0]["payload"]
    assert metric_payload["revenue"] == "12000.10"
    assert metric_payload["roas"] == "1.499975000624984375"
    assert metric_payload["created_at"] == NOW.isoformat()
    workflow_payload = write_client.calls[1]["payload"][0]
    assert workflow_payload["last_run"] == NOW.isoformat()
    alert_payload = write_client.calls[2]["payload"][0]
    assert alert_payload["created_timestamp"] == NOW.isoformat()


def test_successful_reads_validate_all_models_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("real network access attempted")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(socket.socket, "connect", fail_network)
    rows = {
        "metrics_snapshots": [
            _row_with_id(metric_snapshot_to_row(_metric_snapshot()))
        ],
        "workflow_runs": [workflow_run_to_row(_workflow())],
        "alerts": [alert_to_row(_alert())],
        "generated_summaries": [
            _row_with_id(generated_summary_to_row(_summary_record()))
        ],
    }
    read_client = FakeClient(rows=rows)
    repository = SupabaseRepository(read_client=read_client)

    assert repository.get_metric_snapshots(limit=1)[0].source == (
        _metric_snapshot().source
    )
    assert repository.get_workflow_runs() == [_workflow()]
    assert repository.get_alerts() == [_alert()]
    assert repository.get_generated_summaries()[0].result == (
        _summary_record().result
    )
    assert all(call["operation"] == "select" for call in read_client.calls)


def test_invalid_database_row_is_rejected_by_pydantic() -> None:
    invalid_workflow = {
        **workflow_run_to_row(_workflow()),
        "status": "invented",
    }
    repository = SupabaseRepository(
        read_client=FakeClient(rows={"workflow_runs": [invalid_workflow]})
    )

    with pytest.raises(ValidationError):
        repository.get_workflow_runs()


def test_supabase_errors_are_safe_and_do_not_log_secrets(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "service-role-secret"
    repository = SupabaseRepository(
        read_client=FakeClient(error=RuntimeError(secret))
    )

    with pytest.raises(
        RepositoryUnavailableError,
        match="currently unavailable",
    ):
        repository.get_alerts()

    assert secret not in caplog.text


def test_writes_require_service_role_client() -> None:
    repository = SupabaseRepository(read_client=FakeClient())

    with pytest.raises(
        RepositoryConfigurationError,
        match="service-role key",
    ):
        repository.save_alerts([_alert()])

