# AI Operations Control Center

AI Operations Control Center is a portfolio project for monitoring direct-to-consumer
(DTC) business metrics, operational workflows, and deterministic alerts from one
control plane.

## Current milestone

Milestone 5 adds deterministic n8n ingestion while preserving the local demo
foundation, safe Gemini summaries, and Supabase repository:

- validated Pydantic v2 domain models;
- offline metric calculations with safe division-by-zero behavior;
- explicit, configuration-driven alert rules;
- a JSON-backed local demo repository;
- fictional demo fixtures with stable expected results; and
- an offline Pytest suite;
- KPI cards, workflow monitoring, and active alert views in Streamlit; and
- concise, structured founder summaries with deterministic offline fallback;
- a validated Supabase repository for live reads and trusted backend writes; and
- a versioned PostgreSQL migration with RLS and read-only anon access; and
- one manually triggered n8n workflow that ingests fixed fictional source data
  and writes raw metric inputs plus workflow-run observations to Supabase.

Claude remains an unconfigured extension stub and is not required for the MVP.
Final deployment and presentation polish are outside this milestone.

## Setup

Python 3.11 or newer is required.

```powershell
cd ai-operations-control-center
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run tests

```powershell
python -m pytest
```

## Run the dashboard

```powershell
streamlit run app.py
```

With the default `APP_MODE=demo`, the dashboard reads only the fictional fixtures
under `data/demo/` and never constructs a Supabase client.

## Supabase live persistence

Create a project from the [Supabase dashboard](https://supabase.com/dashboard).
From the project settings, copy the project URL, anon key, and—only for a trusted
server-side writer—the service-role key.

Apply the migration with the Supabase CLI:

```powershell
supabase init
supabase login
supabase link --project-ref YOUR_PROJECT_REF
supabase db push --dry-run
supabase db push
```

The migration at `supabase/migrations/001_initial_schema.sql` creates the metric,
workflow, alert, and generated-summary tables. It enables RLS and permits the
anon role to read the fictional portfolio data. It does not grant anon writes.

Enable the live dashboard for the current PowerShell session:

```powershell
$env:APP_MODE="live"
$env:SUPABASE_URL="https://YOUR_PROJECT_REF.supabase.co"
$env:SUPABASE_ANON_KEY="your-anon-key"
streamlit run app.py
```

Live mode requires the URL and anon key. It never silently falls back to local
fixtures. The optional `SUPABASE_SERVICE_ROLE_KEY` is used only to construct the
trusted write client behind repository save methods; it must never be placed in
browser code, committed, or exposed to users.

## n8n fictional ingestion

Import `n8n/workflows/dtc-operations-ingestion.json` into n8n after applying the
Supabase migration. The n8n server requires:

```text
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

The workflow starts with a Manual Trigger. Its default success path upserts one
fixed raw metric snapshot and one successful workflow observation. Set
`simulate_failure=true` in **Demo Controls** to run the controlled failure path,
which writes only a fixed failed workflow observation.

The export contains no secrets and requires no Shopify, Meta Ads, Klaviyo, or
Google credentials. Detailed import, configuration, and run instructions are in
[`docs/n8n-workflow.md`](docs/n8n-workflow.md).

## Gemini live summaries

Demo mode is the safe default and requires no API credentials. To create a
Gemini API key, open the
[Google AI Studio API Keys page](https://aistudio.google.com/app/apikey), select
or import a Google Cloud project, and create a Gemini API key. Google's
[API key guide](https://ai.google.dev/gemini-api/docs/api-key) documents the
current project and key-management flow. Keep the key in a server-side
environment variable and never commit it.

Enable live summaries for the current PowerShell session:

```powershell
$env:APP_MODE="live"
$env:SUPABASE_URL="https://YOUR_PROJECT_REF.supabase.co"
$env:SUPABASE_ANON_KEY="your-anon-key"
$env:GEMINI_API_KEY="your-key"
$env:GEMINI_MODEL="gemini-2.5-flash"
streamlit run app.py
```

Live Gemini runs only when `APP_MODE=live` and `GEMINI_API_KEY` is present. If
the key is missing, Gemini is unavailable, the request times out, or structured
output is invalid, the app logs only a safe error category and displays the
deterministic demo summary with a visible `FALLBACK` status.

Gemini provides narrative assistance only. AI never calculates metrics, creates
or changes alerts, chooses workflow retries, grants approvals, or makes
operational decisions.

## Screenshot

> Screenshot placeholder — add the final dashboard capture during presentation
> polish.

All current data is fictional and exists only to demonstrate deterministic
behavior. AI will never control calculations, alert decisions, approvals, or
business rules. Future AI features may explain deterministic results, but the
underlying rules remain owned by application code and configuration.
