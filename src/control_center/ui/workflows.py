"""Workflow table presentation helpers and Streamlit rendering."""

from datetime import UTC
from decimal import Decimal

import streamlit as st

from control_center.models.workflows import WorkflowRun


def format_ratio(value: Decimal | None) -> str:
    """Format a decimal ratio as an en-US percentage."""

    return "N/A" if value is None else f"{value * 100:,.2f}%"


def workflow_rows(workflows: list[WorkflowRun]) -> list[dict[str, str]]:
    """Convert workflow models to display-only table rows."""

    return [
        {
            "Workflow": workflow.workflow_name,
            "Status": workflow.status.value.upper(),
            "Last run": workflow.last_run.astimezone(UTC).strftime(
                "%b %d, %Y %H:%M UTC"
            ),
            "Retry": workflow.retry_status.value.replace("_", " ").title(),
            "Cost anomaly": format_ratio(workflow.cost_anomaly),
            "Owner": workflow.owner,
            "Severity": workflow.severity.value.upper(),
            "Failure reason": workflow.failure_reason or "—",
        }
        for workflow in workflows
    ]


def render_workflows(workflows: list[WorkflowRun]) -> None:
    """Render workflow monitoring with explicit status and severity labels."""

    st.header("Workflow monitoring")
    rows = workflow_rows(workflows)
    if not rows:
        st.info(
            "No workflow runs are available in the demo fixtures.",
            icon=":material/info:",
        )
        return

    st.dataframe(
        rows,
        hide_index=True,
        column_config={
            "Workflow": st.column_config.TextColumn("Workflow", pinned=True),
            "Status": st.column_config.TextColumn("Status"),
            "Last run": st.column_config.TextColumn("Last run"),
            "Retry": st.column_config.TextColumn("Retry"),
            "Cost anomaly": st.column_config.TextColumn("Cost anomaly"),
            "Owner": st.column_config.TextColumn("Owner"),
            "Severity": st.column_config.TextColumn("Severity"),
            "Failure reason": st.column_config.TextColumn("Failure reason"),
        },
    )
