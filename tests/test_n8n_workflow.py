"""Offline contract tests for the fictional n8n ingestion export."""

import json
from pathlib import Path

from control_center.models.metrics import DTCInputData

ROOT = Path(__file__).resolve().parents[1]
N8N_ROOT = ROOT / "n8n"
WORKFLOW_PATH = N8N_ROOT / "workflows" / "dtc-operations-ingestion.json"

EXPECTED_RAW_INPUTS = {
    "revenue": 12000.0,
    "ad_spend": 8000.0,
    "new_customers": 120,
    "orders": 200,
    "sessions": 10000,
    "refunds": 30,
    "refunded_revenue": 1800.0,
    "impressions": 250000,
    "clicks": 400,
    "creative_frequency": 6.0,
    "previous_period_ad_spend": 4000.0,
}


def _load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as fixture:
        return json.load(fixture)


def test_all_n8n_exports_and_sample_files_are_valid_json() -> None:
    paths = sorted(N8N_ROOT.rglob("*.json"))

    assert len(paths) == 5
    assert all(_load_json(path) is not None for path in paths)


def test_workflow_has_manual_trigger_and_both_persistence_paths() -> None:
    workflow = _load_json(WORKFLOW_PATH)
    nodes = workflow["nodes"]
    node_names = {node["name"] for node in nodes}

    assert workflow["active"] is False
    assert len(nodes) == len(node_names) == 11
    assert "Manual Trigger" in node_names
    assert "Simulate Failure?" in node_names
    assert "Upsert Metric Snapshot" in node_names
    assert "Upsert Successful Workflow Run" in node_names
    assert "Upsert Failed Workflow Run" in node_names

    branches = workflow["connections"]["Simulate Failure?"]["main"]
    assert branches[0][0]["node"] == "Build Controlled Failure Row"
    assert branches[1][0]["node"] == "Build Success Rows"


def test_workflow_export_contains_no_secret_or_alert_write() -> None:
    workflow = _load_json(WORKFLOW_PATH)
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert all("credentials" not in node for node in workflow["nodes"])
    assert "SUPABASE_URL" in workflow_text
    assert "SUPABASE_SERVICE_ROLE_KEY" in workflow_text
    assert ".supabase.co" not in workflow_text
    assert "eyJ" not in workflow_text
    assert "/rest/v1/metrics_snapshots" in workflow_text
    assert "/rest/v1/workflow_runs" in workflow_text
    assert "/rest/v1/alerts" not in workflow_text


def test_workflow_does_not_duplicate_python_metric_formulas() -> None:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8").lower()

    for calculated_field in (
        "roas",
        "cac",
        "aov",
        "cvr",
        "order_volume",
        "refund_rate",
    ):
        assert calculated_field not in workflow_text


def test_sample_data_produces_valid_deterministic_raw_inputs() -> None:
    shopify = _load_json(
        N8N_ROOT / "sample-data" / "shopify-orders.json"
    )["records"]
    meta = _load_json(N8N_ROOT / "sample-data" / "meta-ads.json")["records"]
    sheets = _load_json(
        N8N_ROOT / "sample-data" / "google-sheets-operations.json"
    )["records"]

    impressions = sum(record["impressions"] for record in meta)
    raw_inputs = {
        "revenue": sum(record["gross_revenue"] for record in shopify),
        "ad_spend": sum(record["spend"] for record in meta),
        "new_customers": sum(
            record["new_customers"] for record in shopify
        ),
        "orders": sum(record["order_count"] for record in shopify),
        "sessions": sum(record["sessions"] for record in sheets),
        "refunds": sum(record["refund_count"] for record in shopify),
        "refunded_revenue": sum(
            record["refunded_revenue"] for record in shopify
        ),
        "impressions": impressions,
        "clicks": sum(record["clicks"] for record in meta),
        "creative_frequency": sum(
            record["frequency"] * record["impressions"]
            for record in meta
        )
        / impressions,
        "previous_period_ad_spend": sum(
            record["previous_period_spend"] for record in meta
        ),
    }

    validated = DTCInputData.model_validate(raw_inputs)

    assert validated == DTCInputData.model_validate(EXPECTED_RAW_INPUTS)
