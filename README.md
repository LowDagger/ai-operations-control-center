# AI Operations Control Center

AI Operations Control Center is a portfolio project for monitoring direct-to-consumer
(DTC) business metrics, operational workflows, and deterministic alerts from one
control plane.

## Current milestone

Milestone 3 adds optional Gemini founder summaries on top of the deterministic
local foundation and Streamlit dashboard:

- validated Pydantic v2 domain models;
- offline metric calculations with safe division-by-zero behavior;
- explicit, configuration-driven alert rules;
- a JSON-backed local repository;
- fictional demo fixtures with stable expected results; and
- an offline Pytest suite;
- KPI cards, workflow monitoring, and active alert views in Streamlit; and
- concise, structured founder summaries with deterministic offline fallback.

There is no Supabase integration or n8n workflow in this milestone. Claude is an
unconfigured extension stub and is not required for the MVP.

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

The dashboard reads only the fictional fixtures under `data/demo/`.

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

> Screenshot placeholder — add the final Milestone 3 dashboard capture here.

All current data is fictional and exists only to demonstrate deterministic
behavior. AI will never control calculations, alert decisions, approvals, or
business rules. Future AI features may explain deterministic results, but the
underlying rules remain owned by application code and configuration.
