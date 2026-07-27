# AI Operations Control Center

AI Operations Control Center is a portfolio project for monitoring direct-to-consumer
(DTC) business metrics, operational workflows, and deterministic alerts from one
control plane.

## Current milestone

Milestone 1 provides only the deterministic local foundation:

- validated Pydantic v2 domain models;
- offline metric calculations with safe division-by-zero behavior;
- explicit, configuration-driven alert rules;
- a JSON-backed local repository;
- fictional demo fixtures with stable expected results; and
- an offline Pytest suite.

There is no Streamlit UI, Gemini integration, Supabase integration, n8n workflow,
or network-dependent behavior in this milestone.

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

All current data is fictional and exists only to demonstrate deterministic
behavior. AI will never control calculations, alert decisions, approvals, or
business rules. Future AI features may explain deterministic results, but the
underlying rules remain owned by application code and configuration.

