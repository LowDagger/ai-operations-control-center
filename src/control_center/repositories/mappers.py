"""Single mapping boundary between Pydantic models and Supabase rows."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from control_center.models.alerts import Alert, AlertType
from control_center.models.metrics import CalculatedMetrics, DTCInputData
from control_center.models.persistence import (
    GeneratedSummaryRecord,
    MetricSnapshot,
)
from control_center.models.summaries import (
    FounderSummary,
    SummaryGenerationResult,
)
from control_center.models.workflows import WorkflowRun

DTC_FIELDS = tuple(DTCInputData.model_fields)
CALCULATED_FIELDS = (
    "roas",
    "cac",
    "aov",
    "cvr",
    "order_volume",
    "refund_rate",
)


def serialize_value(value: Any) -> Any:
    """Serialize database values without losing decimal or timezone precision."""

    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (Enum, UUID)):
        return str(value.value if isinstance(value, Enum) else value)
    if isinstance(value, tuple):
        return [serialize_value(item) for item in value]
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    return value


def metric_snapshot_to_row(snapshot: MetricSnapshot) -> dict[str, Any]:
    row = {
        "created_at": serialize_value(snapshot.created_at),
        **{
            field: serialize_value(getattr(snapshot.source, field))
            for field in DTC_FIELDS
        },
        **{
            field: serialize_value(getattr(snapshot.metrics, field))
            for field in CALCULATED_FIELDS
        },
    }
    if snapshot.id is not None:
        row["id"] = str(snapshot.id)
    return row


def metric_snapshot_from_row(row: dict[str, Any]) -> MetricSnapshot:
    source = DTCInputData.model_validate(
        {field: row.get(field) for field in DTC_FIELDS}
    )
    metrics = CalculatedMetrics.model_validate(
        {
            **{field: row.get(field) for field in CALCULATED_FIELDS},
            "revenue": row.get("revenue"),
            "ad_spend": row.get("ad_spend"),
        }
    )
    return MetricSnapshot.model_validate(
        {
            "id": row.get("id"),
            "created_at": row.get("created_at"),
            "source": source,
            "metrics": metrics,
        }
    )


def workflow_run_to_row(workflow: WorkflowRun) -> dict[str, Any]:
    return {
        field: serialize_value(value)
        for field, value in workflow.model_dump().items()
    }


def workflow_run_from_row(row: dict[str, Any]) -> WorkflowRun:
    return WorkflowRun.model_validate(
        {field: row.get(field) for field in WorkflowRun.model_fields}
    )


def alert_to_row(alert: Alert) -> dict[str, Any]:
    return {
        field: serialize_value(value)
        for field, value in alert.model_dump().items()
    }


def alert_from_row(row: dict[str, Any]) -> Alert:
    alert_type = row.get("alert_type")
    current_value = row.get("current_value")
    threshold = row.get("threshold")
    if alert_type not in {
        AlertType.WORKFLOW_FAILURE.value,
        AlertType.MISSING_DATA.value,
    }:
        current_value = _decimal_from_database(current_value)
        threshold = _decimal_from_database(threshold)
    return Alert.model_validate(
        {
            **{field: row.get(field) for field in Alert.model_fields},
            "current_value": current_value,
            "threshold": threshold,
        }
    )


def generated_summary_to_row(
    record: GeneratedSummaryRecord,
) -> dict[str, Any]:
    summary = record.result.summary
    row = {
        "created_at": serialize_value(record.created_at),
        "overall_status": summary.overall_status.value,
        "executive_summary": summary.executive_summary,
        "key_findings": serialize_value(summary.key_findings),
        "recommended_actions": serialize_value(summary.recommended_actions),
        "risks": serialize_value(summary.risks),
        "provider_used": record.result.provider_used,
        "generation_status": record.result.status.value,
        "fallback_reason": record.result.fallback_reason,
    }
    if record.id is not None:
        row["id"] = str(record.id)
    return row


def generated_summary_from_row(
    row: dict[str, Any],
) -> GeneratedSummaryRecord:
    summary = FounderSummary.model_validate(
        {
            field: row.get(field)
            for field in FounderSummary.model_fields
        }
    )
    result = SummaryGenerationResult.model_validate(
        {
            "summary": summary,
            "provider_used": row.get("provider_used"),
            "status": row.get("generation_status"),
            "fallback_reason": row.get("fallback_reason"),
        }
    )
    return GeneratedSummaryRecord.model_validate(
        {
            "id": row.get("id"),
            "created_at": row.get("created_at"),
            "result": result,
        }
    )


def _decimal_from_database(value: Any) -> Any:
    if isinstance(value, str):
        return Decimal(value)
    return value
