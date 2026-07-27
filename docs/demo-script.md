# Interview demo script

Target length: 3–5 minutes. Use the public deployment in `APP_MODE=demo` so
the presentation is stable and requires no credentials.

## 0:00–0:30 — Open the control center

Open the dashboard and point out the **DEMO MODE** and **LOCAL DEMO DATA**
badges.

Say:

> This is a fictional January 15, 2026 snapshot of a direct-to-consumer
> operation. The demo is fully offline and deterministic, so every interviewer
> sees the same results.

## 0:30–1:15 — Explain the KPIs

Walk across Revenue, Ad spend, ROAS, CAC, AOV, CVR, Order volume, and Refund
rate.

Use these examples:

- Revenue is `$12,000.00` and ad spend is `$8,000.00`.
- Python calculates ROAS as `12,000 / 8,000 = 1.50x`.
- CAC is `$8,000 / 120 = $66.67`.
- Refund rate is `30 / 200 = 15.00%`.

Say:

> These calculations are pure Python and use validated Pydantic inputs. Gemini
> never calculates these values.

## 1:15–2:00 — Show deterministic alerts and the failed workflow

Scroll to the workflow and alert tables. Highlight:

- the failed **Refund Reconciliation** workflow;
- critical high refund-rate and creative-fatigue alerts;
- the cost-spike and workflow-failure alerts; and
- the warning that `impressions` is missing from the local fixture.

Say:

> Thresholds live in one validated configuration model. The alert service
> evaluates them in a stable order. The failed workflow has a named owner, but
> the system does not automatically retry or approve anything.

## 2:00–2:45 — Show the founder summary and fallback

Open the Founder Summary section and point out:

- provider used;
- `DEMO`, `LIVE`, or `FALLBACK` status;
- findings, recommended actions, and risks.

Say:

> In demo mode this narrative is deterministic. In live mode Gemini can
> summarize the already-calculated snapshot using structured output. If Gemini
> is missing, unavailable, times out, or returns invalid output, the app visibly
> falls back to the deterministic provider. The data and decisions do not
> change.

## 2:45–3:30 — Show the Supabase schema

Open `supabase/migrations/001_initial_schema.sql` and briefly identify:

- `metrics_snapshots`;
- `workflow_runs`;
- `alerts`; and
- `generated_summaries`.

Say:

> Demo mode never creates a Supabase client. Live mode uses the anon key for
> reads and fails closed if configuration is missing. The service-role key is
> reserved for trusted backend writes and never belongs in browser code.

## 3:30–4:15 — Show the n8n workflow

Open `n8n/workflows/dtc-operations-ingestion.json` in n8n or show the workflow
diagram from `docs/n8n-workflow.md`.

Explain:

- Manual Trigger;
- four fictional source-shaped datasets;
- normalization and aggregation of only the eleven raw inputs;
- fixed-ID Supabase upserts; and
- the controlled `simulate_failure` branch.

Say:

> n8n prepares raw inputs and records workflow observations. It does not
> calculate ROAS, CAC, AOV, CVR, refund rate, alerts, or retry decisions.

## 4:15–5:00 — Close on ownership and safety

Finish with:

> The architecture deliberately separates evidence, deterministic rules,
> persistence, and narrative assistance. Python owns calculations and alerts;
> humans own retries, escalation, and approvals; Gemini explains validated
> results; Supabase persists them; and n8n only ingests fictional raw data.

If time remains, mention the offline test suite and point to
`docs/scoring-and-alert-rules.md`, `docs/sop-workflow-failure.md`, and
`docs/security-and-privacy.md`.
