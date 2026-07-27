"""Streamlit entry point for the fictional operations dashboard."""

from datetime import UTC, datetime
from json import JSONDecodeError
from pathlib import Path

import streamlit as st
from pydantic import ValidationError

from control_center.config import AppMode, AppSettings
from control_center.repositories.local_repository import LocalJsonRepository
from control_center.services.alert_service import AlertService
from control_center.services.metric_service import calculate_metrics
from control_center.ui.alerts import render_alerts
from control_center.ui.dashboard import render_kpis
from control_center.ui.workflows import render_workflows

st.set_page_config(
    page_title="AI Operations Control Center",
    page_icon=":material/analytics:",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parent
DEMO_DATA_DIRECTORY = PROJECT_ROOT / "data" / "demo"
DEMO_EVALUATION_TIMESTAMP = datetime(2026, 1, 15, 12, tzinfo=UTC)

try:
    settings = AppSettings.from_environment()
except ValidationError as error:
    st.error(
        "Invalid application configuration. APP_MODE must be `demo` or `live`.",
        icon=":material/error:",
    )
    st.caption(f"Configuration detail: {error}")
    st.stop()

with st.container(
    horizontal=True,
    vertical_alignment="center",
    horizontal_alignment="distribute",
):
    st.title("AI Operations Control Center")
    st.badge(
        f"{settings.app_mode.value.upper()} MODE",
        icon=":material/database:",
        color="blue" if settings.app_mode == AppMode.DEMO else "green",
    )

st.caption(
    "Demo snapshot: January 15, 2026 · All displayed information is fictional."
)

try:
    repository = LocalJsonRepository(DEMO_DATA_DIRECTORY)
    source = repository.load_metrics()
    workflow_runs = repository.load_workflow_runs()
    calculated_metrics = calculate_metrics(source)
    active_alerts = AlertService().evaluate(
        source,
        calculated_metrics,
        workflow_runs,
        created_at=DEMO_EVALUATION_TIMESTAMP,
    )
except (FileNotFoundError, JSONDecodeError, OSError, ValidationError, ValueError) as error:
    st.error(
        "Demo data is unavailable or invalid. Restore the fictional JSON fixtures "
        "under `data/demo/` and reload the app.",
        icon=":material/error:",
    )
    st.caption(f"Local validation detail: {error}")
    st.stop()

render_kpis(calculated_metrics)
render_workflows(workflow_runs)
render_alerts(active_alerts)
