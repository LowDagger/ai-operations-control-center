"""Supabase persistence using separate read and trusted-write clients."""

import logging
from typing import Any

from control_center.models.alerts import Alert
from control_center.models.persistence import (
    GeneratedSummaryRecord,
    MetricSnapshot,
)
from control_center.models.workflows import WorkflowRun
from control_center.repositories.exceptions import (
    RepositoryConfigurationError,
    RepositoryUnavailableError,
)
from control_center.repositories.local_repository import _validated_limit
from control_center.repositories.mappers import (
    alert_from_row,
    alert_to_row,
    generated_summary_from_row,
    generated_summary_to_row,
    metric_snapshot_from_row,
    metric_snapshot_to_row,
    workflow_run_from_row,
    workflow_run_to_row,
)

LOGGER = logging.getLogger(__name__)


class SupabaseRepository:
    """Persist validated models without exposing Supabase calls to the UI."""

    def __init__(
        self,
        *,
        read_client: Any,
        write_client: Any | None = None,
    ) -> None:
        self._read_client = read_client
        self._write_client = write_client

    @classmethod
    def from_credentials(
        cls,
        *,
        url: str,
        anon_key: str,
        service_role_key: str | None = None,
    ) -> "SupabaseRepository":
        """Build anon read and optional service-role write clients."""

        from supabase import create_client
        from supabase.client import ClientOptions

        def client_options() -> ClientOptions:
            return ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            )

        read_client = create_client(url, anon_key, options=client_options())
        write_client = (
            create_client(url, service_role_key, options=client_options())
            if service_role_key is not None
            else None
        )
        return cls(read_client=read_client, write_client=write_client)

    def save_metric_snapshot(self, snapshot: MetricSnapshot) -> MetricSnapshot:
        rows = self._insert(
            "metrics_snapshots",
            metric_snapshot_to_row(snapshot),
        )
        return metric_snapshot_from_row(_single_row(rows))

    def get_metric_snapshots(self, limit: int = 100) -> list[MetricSnapshot]:
        return [
            metric_snapshot_from_row(row)
            for row in self._select("metrics_snapshots", limit)
        ]

    def save_workflow_runs(
        self,
        workflows: list[WorkflowRun],
    ) -> list[WorkflowRun]:
        if not workflows:
            return []
        rows = self._insert(
            "workflow_runs",
            [workflow_run_to_row(workflow) for workflow in workflows],
        )
        return [workflow_run_from_row(row) for row in rows]

    def get_workflow_runs(self, limit: int = 100) -> list[WorkflowRun]:
        return [
            workflow_run_from_row(row)
            for row in self._select("workflow_runs", limit)
        ]

    def save_alerts(self, alerts: list[Alert]) -> list[Alert]:
        if not alerts:
            return []
        rows = self._insert(
            "alerts",
            [alert_to_row(alert) for alert in alerts],
        )
        return [alert_from_row(row) for row in rows]

    def get_alerts(self, limit: int = 100) -> list[Alert]:
        return [
            alert_from_row(row) for row in self._select("alerts", limit)
        ]

    def save_generated_summary(
        self,
        summary: GeneratedSummaryRecord,
    ) -> GeneratedSummaryRecord:
        rows = self._insert(
            "generated_summaries",
            generated_summary_to_row(summary),
        )
        return generated_summary_from_row(_single_row(rows))

    def get_generated_summaries(
        self,
        limit: int = 100,
    ) -> list[GeneratedSummaryRecord]:
        return [
            generated_summary_from_row(row)
            for row in self._select("generated_summaries", limit)
        ]

    def _select(self, table: str, limit: int) -> list[dict[str, Any]]:
        limit = _validated_limit(limit)
        try:
            response = (
                self._read_client.table(table)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
        except Exception as error:
            self._raise_unavailable("read", error)
        return _response_rows(response)

    def _insert(
        self,
        table: str,
        payload: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if self._write_client is None:
            raise RepositoryConfigurationError(
                "Trusted Supabase writes require a service-role key."
            )
        try:
            response = self._write_client.table(table).insert(payload).execute()
        except Exception as error:
            self._raise_unavailable("write", error)
        return _response_rows(response)

    @staticmethod
    def _raise_unavailable(operation: str, error: Exception) -> None:
        LOGGER.warning(
            "Supabase %s failed with %s.",
            operation,
            type(error).__name__,
        )
        raise RepositoryUnavailableError(
            f"Supabase {operation} is currently unavailable."
        ) from None


def _response_rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if not isinstance(data, list) or not all(
        isinstance(row, dict) for row in data
    ):
        raise RepositoryUnavailableError(
            "Supabase returned an invalid response."
        )
    return data


def _single_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != 1:
        raise RepositoryUnavailableError(
            "Supabase did not return exactly one saved row."
        )
    return rows[0]
