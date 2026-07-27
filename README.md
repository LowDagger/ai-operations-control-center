# AI Operations Control Center

AI Operations Control Center is an interview-ready portfolio project for
monitoring direct-to-consumer (DTC) performance, operational workflows,
deterministic alerts, and concise founder summaries from one control plane.
Every committed dataset is fictional.

## Delivery status

The final delivery milestone is complete. The project includes:

- validated Pydantic v2 domain models;
- offline metric calculations with safe division-by-zero behavior;
- explicit, configuration-driven alert rules;
- a JSON-backed local demo repository;
- fictional demo fixtures with stable expected results;
- an offline Pytest suite;
- KPI cards, workflow monitoring, and active alert views in Streamlit;
- concise, structured founder summaries with deterministic offline fallback;
- a validated Supabase repository for live reads and trusted backend writes;
- a versioned PostgreSQL migration with RLS and read-only anon access;
- one manually triggered n8n workflow that ingests fixed fictional source data
  and writes raw metric inputs plus workflow-run observations to Supabase; and
- Streamlit Community Cloud deployment configuration and interview runbooks.

Claude remains an unconfigured extension stub and is not required for the MVP.
No final deployment is performed by this repository change.

## Architecture summary

```text
Fictional fixtures -> LocalJsonRepository ---------.
                                                   |
Fictional n8n inputs -> Supabase -> SupabaseRepository
                                                   |
                                                   v
Pydantic validation -> Python metric service -> Python alert service
                                                   |
                                                   v
                         Gemini summary or deterministic fallback
                                                   |
                                                   v
                                      Streamlit dashboard
```

The repository factory chooses local fixtures in demo mode and Supabase in live
mode. Python remains authoritative for calculations and alerts. Gemini can only
summarize validated results, and n8n can only prepare raw inputs and workflow
observations.

## Key features

- Eight en-US formatted DTC KPI cards.
- Deterministic warning, critical, workflow-failure, cost-spike, and
  missing-data alerts.
- Clear workflow status, severity, owner, retry-status, and failure context.
- Structured Gemini output with validation, timeout handling, and visible
  deterministic fallback.
- Demo/live repository selection that fails closed instead of silently mixing
  data sources.
- Supabase migration with financial numeric types, constraints, indexes, RLS,
  anon reads, and trusted backend writes.
- Portable n8n workflow with fixed fictional inputs and an explicit failure
  branch.

## Screenshots

> **Dashboard overview placeholder** — add a wide desktop capture showing KPI
> cards and the demo badges.

> **Operations placeholder** — add a capture showing the failed workflow and
> severity-labelled alerts.

> **Founder summary placeholder** — add a capture showing provider and fallback
> status.

> **n8n workflow placeholder** — add a canvas capture of the success and
> controlled-failure branches.

## Local setup

Python 3.11 or newer is required.

```powershell
cd ai-operations-control-center
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

`pyproject.toml` is the authoritative project definition and contains all four
runtime dependencies. The runtime-only `requirements.txt` installs this local
`src/` package on Streamlit Community Cloud through `-e .`.

## Demo mode setup

Demo mode is the safe default. It requires no `.env`, API keys, network calls,
Gemini account, or Supabase project.

```powershell
streamlit run app.py
```

To make the mode explicit for the current PowerShell session:

```powershell
$env:APP_MODE="demo"
streamlit run app.py
```

The dashboard reads only the fictional fixtures under `data/demo/` and never
constructs a Supabase or Gemini client.

For a local secrets file, create `.streamlit/secrets.toml` without committing
it. Root-level Streamlit secrets are available as environment variables:

```toml
APP_MODE = "demo"
GEMINI_MODEL = "gemini-2.5-flash"
```

`.streamlit/secrets.toml` is excluded by `.gitignore`.

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

## Test commands

All tests are designed to run offline:

```powershell
python -m pytest
python -m compileall -q app.py src tests
git diff --check
python -m pip check
```

## Streamlit Community Cloud deployment

`app.py` at the repository root is the deployment entry point. Community Cloud
uses `requirements.txt` to install the local package, and `pyproject.toml`
provides its complete runtime dependency set.

1. Push the repository to GitHub without `.env` or
   `.streamlit/secrets.toml`.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **Create app**, then choose the repository and branch.
4. Set the main file path to `app.py`.
5. Open **Advanced settings** and select Python 3.12.
6. For the public portfolio deployment, paste:

   ```toml
   APP_MODE = "demo"
   ```

7. Select **Deploy** and confirm the page shows `DEMO MODE`,
   `LOCAL DEMO DATA`, and the January 15, 2026 fictional snapshot caption.

Demo deployment requires no credential. The complete supported secrets are:

| Secret | Demo | Live | Purpose |
| --- | --- | --- | --- |
| `APP_MODE` | Set to `"demo"` | Set to `"live"` | Selects the repository/provider path |
| `GEMINI_API_KEY` | Omit | Required for live Gemini only | Server-side Gemini authentication |
| `GEMINI_MODEL` | Optional | Optional; defaults to `gemini-2.5-flash` | Gemini model name |
| `SUPABASE_URL` | Omit | Required | Supabase project URL |
| `SUPABASE_ANON_KEY` | Omit | Required | Read-only dashboard client |
| `SUPABASE_SERVICE_ROLE_KEY` | Omit | Optional trusted writes only | Backend writer; never needed by the public read-only dashboard |

A full live read-and-summary configuration uses root-level TOML values:

```toml
APP_MODE = "live"
GEMINI_API_KEY = "replace-in-cloud-settings"
GEMINI_MODEL = "gemini-2.5-flash"
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_ANON_KEY = "replace-in-cloud-settings"
```

Do not add the service-role key to a public read-only deployment. Configure it
only for a separately reviewed trusted backend writer such as the documented
n8n process.

## Security boundaries

- Every committed and publicly readable record is fictional.
- Python calculates metrics and evaluates alert rules.
- Gemini receives validated results and returns narrative structured output
  only; provider failure visibly falls back.
- Humans decide retries, escalations, approvals, and operational actions.
- Demo mode creates no Gemini or Supabase client.
- Live mode fails closed when Supabase read configuration is missing and never
  silently reads local fixtures.
- The anon key is for RLS-controlled reads. The service-role key is restricted
  to trusted server-side writes.
- n8n writes raw metric inputs and workflow observations, never alerts.
- `.env`, virtual environments, caches, and `.streamlit/secrets.toml` are
  ignored.

See [security and privacy](docs/security-and-privacy.md), the
[workflow-failure SOP](docs/sop-workflow-failure.md), and
[scoring and alert rules](docs/scoring-and-alert-rules.md).

## Repository structure

```text
.
├── app.py
├── pyproject.toml
├── requirements.txt
├── .streamlit/config.toml
├── data/demo/
├── docs/
│   ├── architecture.md
│   ├── current-status.md
│   ├── demo-script.md
│   ├── n8n-workflow.md
│   ├── scoring-and-alert-rules.md
│   ├── security-and-privacy.md
│   └── sop-workflow-failure.md
├── n8n/
│   ├── sample-data/
│   └── workflows/
├── src/control_center/
│   ├── models/
│   ├── providers/
│   ├── repositories/
│   ├── services/
│   └── ui/
├── supabase/migrations/
└── tests/
```

## Interview talking points

- Deterministic-first design: the same fictional snapshot always produces the
  same metrics and alerts.
- Clear authority boundaries: code owns calculations, humans own decisions,
  and AI owns only constrained narrative assistance.
- Fail-closed live mode: missing or unavailable Supabase configuration never
  causes a silent local-data fallback.
- Provider portability: Gemini and deterministic providers share a validated
  summary interface; Claude remains an optional stub.
- Persistence isolation: Streamlit contains no Supabase calls, and mapping
  between Pydantic and database rows lives in one repository boundary.
- Safe automation: n8n uses fixed fictional inputs, idempotent upserts, and no
  alert or retry authority.
- Testability: external providers are mocked and network use is blocked in
  relevant offline tests.
- A concise 3–5 minute walkthrough is available in
  [`docs/demo-script.md`](docs/demo-script.md).

All current data is fictional and exists only to demonstrate deterministic
behavior. AI will never control calculations, alert decisions, approvals, or
business rules.
