# n8n DTC operations ingestion

## Purpose

`n8n/workflows/dtc-operations-ingestion.json` is a portable, manually triggered
demo workflow. It loads fixed fictional Shopify, Meta Ads, Klaviyo, and Google
Sheets-style records, normalizes them, produces the eleven raw inputs accepted
by the Python application, and writes the result to Supabase.

The committed files under `n8n/sample-data/` are readable reference copies of
the exact records embedded in the workflow. Embedding the records keeps the
export portable: an imported workflow does not depend on a host filesystem
mount, a SaaS account, or external source credentials.

All dates, identifiers, values, owners, and failure messages are fictional.

## Node-by-node flow

| Node | Responsibility |
| --- | --- |
| Manual Trigger | Starts the workflow only when an operator selects Execute Workflow. |
| Demo Controls | Holds the `simulate_failure` boolean. It defaults to `false`. |
| Load Fictional Sample Data | Loads fixed copies of the four committed sample datasets. |
| Normalize Source Records | Maps each simulated source shape into stable operational fields. |
| Aggregate Raw Operational Inputs | Sums only the eleven source inputs used by `DTCInputData`. |
| Simulate Failure? | Routes the run according to the explicit demo toggle. |
| Build Success Rows | Builds fixed metric-snapshot and successful-run rows. |
| Upsert Metric Snapshot | Upserts the raw input snapshot into `metrics_snapshots`. |
| Upsert Successful Workflow Run | Upserts the successful execution observation into `workflow_runs`. |
| Build Controlled Failure Row | Builds fixed failed-run metadata without a metric snapshot. |
| Upsert Failed Workflow Run | Upserts only the failed execution observation into `workflow_runs`. |

The IF node's true output is the simulated failure branch. Its false output is
the normal success branch.

## Deterministic output

The success path writes this raw input snapshot:

| Field | Value |
| --- | ---: |
| revenue | 12000.00 |
| ad_spend | 8000.00 |
| new_customers | 120 |
| orders | 200 |
| sessions | 10000 |
| refunds | 30 |
| refunded_revenue | 1800.00 |
| impressions | 250000 |
| clicks | 400 |
| creative_frequency | 6.0 |
| previous_period_ad_spend | 4000.00 |

Fixed UUIDs and timestamps make repeated demo runs predictable. Supabase REST
upserts use `on_conflict=id` with `resolution=merge-duplicates`, so each branch
updates its own known demo row rather than continually adding duplicates.

The workflow deliberately omits `roas`, `cac`, `aov`, `cvr`, `order_volume`,
and `refund_rate` from its database payload. Those values remain the
responsibility of the deterministic Python metric service.

## Required environment variables

Configure these variables in the server-side environment that starts n8n:

```text
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Restart n8n after changing its environment. The workflow reads the variables
through n8n expressions and the exported JSON contains neither value.

The service-role key is appropriate here only because this is a trusted
server-side ingestion process. Never put it in browser code, Streamlit client
state, a workflow note, a committed `.env` file, or an exported credential.

## Import steps

1. Apply `supabase/migrations/001_initial_schema.sql` to the target Supabase
   project.
2. Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the n8n server
   environment and restart n8n.
3. In n8n, create or open a workflow.
4. Open the workflow menu, select **Import from File**, and choose
   `n8n/workflows/dtc-operations-ingestion.json`.
5. Confirm that the imported workflow remains inactive. This workflow needs no
   Shopify, Meta, Klaviyo, or Google credentials.
6. Review the two HTTP Request nodes and verify that their URLs point to the
   expected Supabase project through `SUPABASE_URL`.

The workflow uses HTTP Request nodes rather than an embedded Supabase
credential object so that no secret reference or value is part of the export.

## Run the success path

1. Open **Demo Controls**.
2. Leave `simulate_failure` set to `false`.
3. Select **Execute Workflow**.
4. Confirm that **Upsert Metric Snapshot** and
   **Upsert Successful Workflow Run** complete.
5. In Supabase, verify the fixed snapshot ID
   `11111111-1111-4111-8111-111111111111` and successful workflow-run ID
   `22222222-2222-4222-8222-222222222222`.
6. Run the workflow again and confirm the same IDs are updated, not duplicated.

## Run the simulated failure path

1. Open **Demo Controls**.
2. Change `simulate_failure` to `true`.
3. Select **Execute Workflow**.
4. Confirm that **Upsert Failed Workflow Run** completes and that the metric
   snapshot node does not run.
5. In Supabase, verify failed workflow-run ID
   `33333333-3333-4333-8333-333333333333`.
6. Set `simulate_failure` back to `false` before the next success demonstration.

This controlled branch records a fictional failed workflow observation. It does
not throw an n8n execution error, decide whether to retry, or create an alert.

## Decision boundary

n8n is allowed to:

- load and normalize fictional source-shaped data;
- aggregate the eleven raw application inputs;
- record observed workflow execution metadata; and
- write raw metric snapshots and workflow runs through a trusted backend key.

n8n is not allowed to:

- calculate ROAS, CAC, AOV, CVR, order volume, or refund rate;
- create, update, or delete alerts;
- assign alert severity or evaluate alert thresholds;
- decide retries, approvals, spending actions, or other operational responses;
- invoke Gemini or replace its validated fallback behavior; or
- process real customer data in this portfolio workflow.

Python remains authoritative for all business metrics and deterministic alerts.
