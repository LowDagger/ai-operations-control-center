# AI Operations Control Center

AI Operations Control Center is a portfolio project for monitoring direct-to-consumer
(DTC) business metrics, operational workflows, and deterministic alerts from one
control plane.

## Current milestone

Milestone 2 adds a Streamlit dashboard on top of the deterministic local
foundation:

- validated Pydantic v2 domain models;
- offline metric calculations with safe division-by-zero behavior;
- explicit, configuration-driven alert rules;
- a JSON-backed local repository;
- fictional demo fixtures with stable expected results; and
- an offline Pytest suite;
- KPI cards, workflow monitoring, and active alert views in Streamlit.

There is no Gemini integration, Supabase integration, n8n workflow, or
network-dependent data source in this milestone.

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

## Screenshot

> Screenshot placeholder — add the final Milestone 2 dashboard capture here.

All current data is fictional and exists only to demonstrate deterministic
behavior. AI will never control calculations, alert decisions, approvals, or
business rules. Future AI features may explain deterministic results, but the
underlying rules remain owned by application code and configuration.
